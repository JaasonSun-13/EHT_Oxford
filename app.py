import asyncio
import random
import re
import base64
import streamlit as st
from datetime import date
from pathlib import Path
from matching.pricing import driverplan_compat_adjust
from matching.driver import generate_driver, generate_driver_scores
from frontend import loading_files
from frontend.trip_request import create_trip_request
from travel_planner import response


# =============================================================================
# Page config & CSS
# =============================================================================

st.set_page_config(
    page_title="GOOD Tour Planner",
    page_icon="🗺️",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,700&family=Playfair+Display:wght@600;700&display=swap');

    .stApp {
        font-family: 'DM Sans', sans-serif;
        max-width: 480px;
        margin: 0 auto;
        font-size: 1.1rem;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        letter-spacing: -0.02em;
    }

    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
        color: white; padding: 1.8rem 1.2rem; border-radius: 16px;
        margin-bottom: 1.2rem; text-align: center !important;
        position: relative; overflow: hidden;
    }
    .hero::after {
        content: ''; position: absolute; top: -60%; right: -30%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(233,196,106,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero h2 { font-size: 1.9rem; margin: 0 0 0.2rem 0; position: relative; z-index: 1; text-align: center !important; }
    .hero p { font-size: 1.05rem; opacity: 0.75; margin: 0; position: relative; z-index: 1; text-align: center !important; }

    .steps { display: flex; justify-content: center; gap: 0.3rem; margin-bottom: 1.5rem; }
    .step { display: flex; flex-direction: column; align-items: center; font-size: 0.8rem; font-weight: 500; color: #bbb; }
    .step.active { color: #e9c46a; font-weight: 700; }
    .step.done { color: #2a9d8f; }
    .step-dot {
        width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.0rem; font-weight: 700;
        border: 2px solid #ddd; background: white; margin-bottom: 0.25rem;
    }
    .step.active .step-dot { border-color: #e9c46a; background: #e9c46a; color: #1a1a2e; }
    .step.done .step-dot { border-color: #2a9d8f; background: #2a9d8f; color: white; }
    .step-line { width: 28px; height: 2px; background: #ddd; align-self: center; margin-bottom: 12px; }
    .step-line.done { background: #2a9d8f; }

    .route-card {
        background: white; border: 1px solid #eee; border-radius: 14px;
        padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }
    .route-title { font-family: 'Playfair Display', serif; font-size: 1.7rem; font-weight: 700; margin: 0 0 0.15rem 0; }
    .route-meta { font-size: 1.1rem; color: #888; margin-bottom: 0.5rem; }

    .tl { border-left: 2px solid #e9c46a; padding-left: 1rem; margin: 0.5rem 0; }
    .tl-stop { position: relative; padding: 0.4rem 0; }
    .tl-stop::before {
        content: ''; position: absolute; left: -1.35rem; top: 0.65rem;
        width: 10px; height: 10px; border-radius: 50%;
        background: #e9c46a; border: 2px solid white; box-shadow: 0 0 0 2px #e9c46a;
    }
    .tl-stop-name { font-weight: 600; font-size: 1.05rem; color: #1a1a2e; }
    .tl-stop-detail { font-size: 0.88rem; color: #888; }
    .tl-walk { font-size: 0.85rem; color: #aaa; padding: 0.15rem 0; }

    .theme-fastest { border-left-color: #ef4444; }
    .theme-fastest .tl-stop::before { background: #ef4444; box-shadow: 0 0 0 2px #ef4444; }
    .theme-popular { border-left-color: #f59e0b; }
    .theme-popular .tl-stop::before { background: #f59e0b; box-shadow: 0 0 0 2px #f59e0b; }
    .theme-balanced { border-left-color: #10b981; }
    .theme-balanced .tl-stop::before { background: #10b981; box-shadow: 0 0 0 2px #10b981; }
    .theme-relaxed { border-left-color: #3b82f6; }
    .theme-relaxed .tl-stop::before { background: #3b82f6; box-shadow: 0 0 0 2px #3b82f6; }
    .theme-hidden_gems { border-left-color: #8b5cf6; }
    .theme-hidden_gems .tl-stop::before { background: #8b5cf6; box-shadow: 0 0 0 2px #8b5cf6; }

    .stat-row { display: flex; gap: 0.5rem; margin: 0.5rem 0; }
    .stat-pill { flex: 1; background: #f5f5f5; border-radius: 10px; padding: 0.5rem; text-align: center; }
    .stat-pill .val { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #1a1a2e; }
    .stat-pill .lbl { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #999; }

    .driver-card {
        background: white; border: 1px solid #eee; border-radius: 14px;
        padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        display: flex; align-items: center; gap: 0.8rem;
    }
    .driver-info { flex: 1; }
    .driver-name { font-weight: 700; font-size: 1.1rem; }
    .driver-detail { font-size: 0.9rem; color: #888; }
    .driver-price { font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700; color: #059669; }

    .section-label { font-size: 1.5rem; font-weight: 700; letter-spacing: 0.02em; color: #1a1a2e; margin: 1rem 0 0.4rem 0; }

    .success-banner {
        background: linear-gradient(135deg, #064e3b, #059669);
        color: white; padding: 1.5rem 1rem; border-radius: 16px;
        text-align: center !important; margin-bottom: 1rem;
    }
    .success-banner h2 { font-size: 1.7rem; margin: 0 0 0.3rem 0; text-align: center !important; }
    .success-banner p { font-size: 1.0rem; opacity: 0.85; margin: 0; text-align: center !important; }

    .confirm-card {
        background: white; border: 1px solid #eee; border-radius: 14px;
        padding: 1.2rem; margin-bottom: 0.8rem; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }
    .confirm-card h3 { margin: 0 0 0.5rem 0; font-size: 1.2rem; }
    .confirm-row { display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid #f3f3f3; }
    .confirm-row:last-child { border-bottom: none; }
    .confirm-label { font-size: 0.95rem; color: #888; }
    .confirm-val { font-size: 0.95rem; font-weight: 600; color: #1a1a2e; }

    .stButton > button { border-radius: 12px !important; font-weight: 600 !important; font-size: 1.05rem !important; }

    [data-testid="stMetric"] { background: #f8f9fa; border-radius: 10px; padding: 0.6rem !important; text-align: center; }
    [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif !important; font-size: 1.3rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.9rem !important; }

    .stSlider label, .stSelectbox label, .stMultiSelect label,
    .stDateInput label, .stTextArea label, .stRadio label { font-size: 1.05rem !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Components
# =============================================================================

def render_hero():
    st.markdown("""
    <div class="hero">
        <h2>Tour Planner</h2>
        <p>Plan your perfect day</p>
    </div>
    """, unsafe_allow_html=True)


def render_steps(current):
    labels = ["Setup", "Routes", "Match", "Confirm", "Done"]
    html = '<div class="steps">'
    for i, label in enumerate(labels, 1):
        cls = "active" if i == current else ("done" if i < current else "")
        html += f'<div class="step {cls}"><div class="step-dot">{i}</div>{label}</div>'
        if i < len(labels):
            line_cls = "done" if i < current else ""
            html += f'<div class="step-line {line_cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


THEME_EMOJI = {"fastest": "⚡", "popular": "🌟", "balanced": "⚖️", "relaxed": "🌿", "hidden_gems": "💎"}
THEME_DESC = {"fastest": "Max stops, min travel", "popular": "Crowd favourites", "balanced": "Best of both worlds", "relaxed": "Fewer stops, breathe more", "hidden_gems": "Off the beaten path"}
THEME_COLOR = {"fastest": "#ef4444", "popular": "#f59e0b", "balanced": "#10b981", "relaxed": "#3b82f6", "hidden_gems": "#8b5cf6"}


# =============================================================================
# Page 1: Trip Setup
# =============================================================================

def page_trip_setup():
    render_hero()
    render_steps(1)

    st.markdown('<div class="section-label">📅 When</div>', unsafe_allow_html=True)
    chosen_date = st.date_input("Date", value=date.today(), label_visibility="collapsed")
    duration = st.slider("Duration (hours)", min_value=0.0, max_value=10.0, value=5.0, step=0.5)

    st.markdown('<div class="section-label">🏙️ Where</div>', unsafe_allow_html=True)
    city = st.selectbox("City", ["Oxford", "London", "Bristol"], label_visibility="collapsed")

    st.markdown('<div class="section-label">🌐 Languages</div>', unsafe_allow_html=True)
    languages = st.multiselect(
        "Languages",
        loading_files.load_languages("data_collection/Database/driver_identifier.csv"),
        default=[], label_visibility="collapsed",
    )

    st.markdown('<div class="section-label">📍 Must-visit</div>', unsafe_allow_html=True)
    attractions = loading_files.load_attractions_by_city(city)
    must_visits = st.multiselect("Attractions", attractions, default=[], label_visibility="collapsed")

    def slugify(name: str) -> str:
        s = name.lower().strip()
        s = re.sub(r"[^a-z0-9]+", "_", s)
        return s.strip("_")
    must_visit_ids = [slugify(n) for n in must_visits]

    st.markdown('<div class="section-label">✍️ Preferences</div>', unsafe_allow_html=True)
    preference_text = st.text_area(
        "Describe your ideal trip",
        placeholder="Relaxed pace, love museums, prefer less walking...",
        height=80, label_visibility="collapsed",
    )

    # Guide type — 4 image cards
    st.markdown('<div class="section-label">🧑‍🤝‍🧑 Guide Type</div>', unsafe_allow_html=True)

    GUIDE_CARDS = [
        {"key": "Your GOOD Buddy", "label": "GOOD Buddy", "desc": "Local companion who shares insider tips",
         "img": "https://plus.unsplash.com/premium_photo-1661376831665-6af1e64af6e1?q=80&w=400&h=250&fit=crop&auto=format"},
        {"key": "Bike Guide", "label": "Bike Guide", "desc": "Eco-friendly bicycle tour with a local biker",
         "img": "https://plus.unsplash.com/premium_photo-1663051092082-cd8347e4353d?q=80&w=400&h=250&fit=crop&auto=format"},
        {"key": "Driver Guide", "label": "Driver Guide", "desc": "Private transport + commentary",
         "img": "https://plus.unsplash.com/premium_photo-1682088009870-5db57bae6e31?q=80&w=400&h=250&fit=crop&auto=format"},
        {"key": "Driver only", "label": "Driver Only", "desc": "Professional driver, explore your way",
         "img": "https://plus.unsplash.com/premium_photo-1683133426404-402a7b42f1fd?q=80&w=400&h=250&fit=crop&auto=format"},
    ]

    if "service" not in st.session_state:
        st.session_state.service = "Your GOOD Buddy"

    cols = st.columns(2, gap="small")
    for idx, g in enumerate(GUIDE_CARDS):
        with cols[idx % 2]:
            is_selected = st.session_state.service == g["key"]
            border_color = "#e9c46a" if is_selected else "#eee"
            shadow = "0 0 0 3px #e9c46a" if is_selected else "0 2px 8px rgba(0,0,0,0.04)"
            check = "✅ " if is_selected else ""
            st.markdown(f"""
            <div style="border: 2px solid {border_color}; border-radius: 14px; overflow: hidden;
                        box-shadow: {shadow}; margin-bottom: 0.5rem;">
                <img src="{g['img']}" style="width:100%; height:120px; object-fit:cover;" />
                <div style="padding: 0.5rem 0.7rem;">
                    <div style="font-weight:700; font-size:1.05rem; color:#1a1a2e;">{check}{g['label']}</div>
                    <div style="font-size:0.9rem; color:#888;">{g['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{'✅ Selected' if is_selected else 'Select'}", key=f"guide_{g['key']}",
                         use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.service = g["key"]
                st.rerun()

    service = st.session_state.service

    st.markdown('<div class="section-label">💰 Budget</div>', unsafe_allow_html=True)
    budget_max = st.slider("Maximum budget (£)", 0, 3000, 1000, step=50, label_visibility="collapsed")

    trip_request = create_trip_request(
        must_visit_ids=must_visit_ids, duration=duration, budget=budget_max,
        service=service, chosen_date=chosen_date, city=city,
        languages=languages, description=preference_text,
    )

    st.markdown("")
    if st.button("🚀 Generate Routes", use_container_width=True, type="primary"):
        st.session_state.trip_request = trip_request
        st.session_state.step = 2
        st.rerun()


# =============================================================================
# Page 2: Routes
# =============================================================================

def page_plans():
    render_steps(2)

    if st.button("← Back"):
        st.session_state.step = 1
        st.rerun()

    with st.spinner("🤖 Generating routes..."):
        cur_response = asyncio.run(response.actual_response(st.session_state.trip_request))

    if cur_response.trip_description:
        st.info(f"💡 {cur_response.trip_description}")

    if not cur_response.routes:
        st.error("No routes found. Try more time or budget.")
        return

    for i, r in enumerate(cur_response.routes):
        theme = r.theme or "route"
        emoji = THEME_EMOJI.get(theme, "📌")
        desc = THEME_DESC.get(theme, "")
        color = THEME_COLOR.get(theme, "#e9c46a")

        st.markdown(f"""
        <div class="route-card">
            <div class="route-title">{emoji} {theme.replace('_', ' ').title()}</div>
            <div class="route-meta">{desc}</div>
            <div class="stat-row">
                <div class="stat-pill"><div class="val">{r.total_duration_hours:.1f}h</div><div class="lbl">Duration</div></div>
                <div class="stat-pill"><div class="val">{len(r.timeline)}</div><div class="lbl">Stops</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View schedule", expanded=(i == 0)):
            if getattr(r, "explanation", None):
                st.caption(r.explanation)

            if getattr(r, "micro_stops", None):
                st.markdown("**✨ Nearby bonus stops:**")
                for ms in r.micro_stops:
                    st.write(f"💎 {ms}")

            timeline_html = f'<div class="tl theme-{theme}">'
            for idx, t in enumerate(r.timeline, start=1):
                dur = t.offset_end_min - t.offset_start_min
                dur_h = dur // 60
                dur_m = dur % 60
                time_label = f"{dur_h}hr {dur_m}min" if dur_h else f"{dur_m}min"
                timeline_html += f"""
                <div class="tl-stop">
                    <div class="tl-stop-name">{t.attraction_name}</div>
                    <div class="tl-stop-detail">{time_label}</div>
                </div>"""
                if getattr(t, "travel_to_next_minutes", None) is not None and t.travel_to_next_minutes > 0:
                    timeline_html += f'<div class="tl-walk">🚶 {t.travel_to_next_minutes} min travel</div>'
            timeline_html += '</div>'
            st.markdown(timeline_html, unsafe_allow_html=True)

            if st.button(f"✅ Choose {theme.replace('_', ' ').title()}", key=f"choose_{i}",
                         type="primary", use_container_width=True):
                st.session_state.selected_route = r
                st.session_state.step = 3
                st.rerun()


# =============================================================================
# Page 3: Driver Matching (with pricing)
# =============================================================================

def page_matching():
    render_steps(3)

    if st.button("← Back"):
        st.session_state.step = 2
        st.rerun()

    trip_request = st.session_state.get("trip_request")
    plan = st.session_state.get("selected_route")
    if not trip_request or not plan:
        st.warning("No route selected.")
        return

    theme = getattr(plan, "theme", "")
    emoji = THEME_EMOJI.get(theme, "📌")
    color = THEME_COLOR.get(theme, "#e9c46a")

    st.markdown(f"""
    <div class="route-card" style="border-left: 4px solid {color};">
        <div class="route-title">{emoji} {theme.replace('_', ' ').title()}</div>
        <div class="route-meta">{plan.total_duration_hours:.1f}h · {len(plan.timeline)} stops</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Finding guides & calculating prices..."):
        all_drivers = generate_driver("data_collection/Database/driver_identifier.csv")
        driver_score = generate_driver_scores(all_drivers, plan, trip_request)
        driver_with_total_price = driverplan_compat_adjust(
            driver_score, trip_request.chosen_date, plan.attractions, trip_request.budget
        )

    st.caption(f"{len(driver_with_total_price)} guides matched")

    if not driver_with_total_price:
        st.warning("No matching guides. Try another route or service.")
        return

    for i, dp in enumerate(driver_with_total_price[:10]):
        # First 5 get real photos, rest get cartoon avatars
        if i < 5:
            photo_path = Path(__file__).parent / "photos" / f"driver_{i}.png"
            if photo_path.exists():
                b64 = base64.b64encode(photo_path.read_bytes()).decode()
                avatar_html = f'<img src="data:image/png;base64,{b64}" style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />'
            else:
                avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={dp.driver.name}"
                avatar_html = f'<img src="{avatar_url}" style="width:80px; height:80px; border-radius:50%;" />'
        else:
            avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={dp.driver.name}"
            avatar_html = f'<img src="{avatar_url}" style="width:80px; height:80px; border-radius:50%;" />'

        st.markdown(f"""
        <div class="driver-card">
            {avatar_html}
            <div class="driver-info">
                <div class="driver-name">{dp.driver.name}</div>
                <div class="driver-detail">⭐ {dp.driver.rating}</div>
            </div>
            <div class="driver-price">£{dp.total_price:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Choose {dp.driver.name}", key=f"choose_driver_{i}",
                     type="primary", use_container_width=True):
            st.session_state.selected_driver_price = dp
            st.session_state.step = 4
            st.rerun()


# =============================================================================
# Page 4: Confirm
# =============================================================================

def confirm_page():
    render_steps(4)

    driver_price = st.session_state.get("selected_driver_price")
    plan = st.session_state.get("selected_route")
    trip_request = st.session_state.get("trip_request")

    if not driver_price or not plan:
        st.warning("Missing selection. Go back and choose.")
        return

    theme = getattr(plan, "theme", "")
    emoji = THEME_EMOJI.get(theme, "📌")
    color = THEME_COLOR.get(theme, "#e9c46a")

    st.markdown(f"""
    <div class="confirm-card">
        <h3>📋 Trip Details</h3>
        <div class="confirm-row"><span class="confirm-label">City</span><span class="confirm-val">{trip_request.city.capitalize()}</span></div>
        <div class="confirm-row"><span class="confirm-label">Date</span><span class="confirm-val">{trip_request.chosen_date}</span></div>
        <div class="confirm-row"><span class="confirm-label">Languages</span><span class="confirm-val">{', '.join(trip_request.languages)}</span></div>
        <div class="confirm-row"><span class="confirm-label">Service</span><span class="confirm-val">{trip_request.service.value}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="confirm-card" style="border-left: 4px solid {color};">
        <h3>{emoji} Route: {theme.replace('_', ' ').title()}</h3>
    </div>
    """, unsafe_allow_html=True)

    for a in plan.attractions:
        st.write(f"📍 {a.replace('_', ' ').title()}")

    st.markdown(f"""
    <div class="confirm-card">
        <h3>🧑‍🦱 Guide & Price</h3>
        <div class="confirm-row"><span class="confirm-label">Driver</span><span class="confirm-val">{driver_price.driver.name}</span></div>
        <div class="confirm-row"><span class="confirm-label">Rating</span><span class="confirm-val">⭐ {driver_price.driver.rating}</span></div>
        <div class="confirm-row"><span class="confirm-label">Total Price</span><span class="confirm-val" style="color:#059669; font-size:1.2rem;">£{driver_price.total_price:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Confirm booking", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.rerun()
    with c2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.step = 3
            st.rerun()


# =============================================================================
# Page 5: Request Sent
# =============================================================================

def page_request_sent():
    render_steps(5)

    driver_price = st.session_state.get("selected_driver_price")

    if "request_id" not in st.session_state:
        st.session_state.request_id = f"REQ-{random.randint(100000, 999999)}"

    driver_name = driver_price.driver.name if driver_price else "your guide"

    st.markdown(f"""
    <div class="success-banner">
        <h2>✅ Request Sent!</h2>
        <p>Sent to <strong>{driver_name}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill"><div class="val">{st.session_state.request_id}</div><div class="lbl">Reference</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.success("We'll notify you when they accept.")

    st.markdown("")
    if st.button("🆕 Start new trip", use_container_width=True, type="primary"):
        for k in list(st.session_state.keys()):
            if k != "step":
                st.session_state.pop(k, None)
        st.session_state.step = 1
        st.rerun()


# =============================================================================
# Main
# =============================================================================

if "step" not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:
    page_trip_setup()
elif st.session_state.step == 2:
    page_plans()
elif st.session_state.step == 3:
    page_matching()
elif st.session_state.step == 4:
    confirm_page()
elif st.session_state.step == 5:
    page_request_sent()