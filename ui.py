import asyncio
import random
import re
import streamlit as st
from datetime import date, time, timedelta, datetime
from active_pricing.pricing import driverplan_compat_adjust
from driver import generate_driver, generate_driver_scores
import loading_files
from trip_request import create_trip_request
from travel_planner import response 


# pages
def page_trip_setup():
    st.header("Trip Setup")

    # date
    chosen_date = st.date_input(
        "Date",
        value = date.today()
    )

    # duration
    duration = st.slider("Duration(hrs)", min_value=0.0, max_value=10.0, value=5.0, step=0.5)

    # language
    languages = st.multiselect(
        "Choose languages (multiple allowed)",
        loading_files.load_languages("data_collection/Database/driver_identifier.csv"),
        default = []
    )

    # city
    city = st.selectbox("Choose a city", ["Oxford", "London", "Bristol"])

    # attraction
    attractions = loading_files.load_attractions_by_city(city)
    
    must_visits = st.multiselect(
        "Choose attractions (multiple allowed)",
        attractions,
        default = []
    )


    def slugify(name: str) -> str:
        s = name.lower().strip()
        s = re.sub(r"[^a-z0-9]+", "_", s)
        return s.strip("_")
    must_visit_ids = [slugify(n) for n in must_visits]

    # prefernce_text
    st.subheader("Tell us what you want")
    preference_text = st.text_area(
        "Describe your ideal trip (e.g., pace, interests, food, museums, accessibility needs).",
        placeholder="Example: I like a relaxed pace, love local food and museums, and prefer less walking."
    )

    # service
    GUIDE_TYPES = {
      "Driver Guide": "Provides private transportation and basic route guidance. Ideal if you want comfort and flexibility while moving between attractions.",
      "Driver only": "Professional driver only. No guided explanations—best if you prefer to explore independently while avoiding navigation stress.",
      "Your GOOD Buddy": "A friendly local companion who explores the city with you, shares insider tips, and helps you experience the place like a local friend.",
      "Bike Guide": "Guided tours by bicycle. Perfect for active travelers who want an eco-friendly, immersive way to explore nearby attractions."
    }

    service = st.selectbox("Choose guide type", list(GUIDE_TYPES.keys()))
    st.caption(GUIDE_TYPES[service])

    # budget
    st.subheader("Budget maximum")
    budget_max = st.slider("Maximum budget (£)", 0, 3000, 1000, step=50)

    trip_request = create_trip_request(must_visit_ids=must_visit_ids, 
                                       duration=duration,
                                       budget=budget_max,
                                       service=service,
                                       chosen_date=chosen_date,
                                       city=city,
                                       languages=languages,
                                       description=preference_text)

    if st.button("Next"):
        st.session_state.trip_request = trip_request
        st.session_state.step = 2
        st.rerun()


def page_plans():
    st.header("Choose Plan")

    if st.button("Back"):
        st.session_state.step = 1
        st.rerun()

    cur_response =  asyncio.run(response.actual_response(st.session_state.trip_request))
    st.write(f"request_id: {cur_response.request_id}")
    st.write(f"candidate_count: {cur_response.candidate_count}")
    st.write(f"trip_description: {cur_response.trip_description}")
    print(st.session_state.trip_request)
    # Display the 5 plans
    for i, r in enumerate(cur_response.routes):
        title = f"{r.theme}" if getattr(r, "theme", None) else f"Route {r.route_id}"
        print(r.attractions)

        with st.expander(f"Plan {i+1}: {title}", expanded=(i == 0)):
            # Top summary
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Duration (hrs)", f"{r.total_duration_hours:.1f}")
            c3.metric("Stops", len(r.timeline))

            # Optional fields
            if getattr(r, "explanation", None):
                st.caption(r.explanation)

            if getattr(r, "micro_stops", None):
                st.markdown("**Micro-stops**")
                for ms in r.micro_stops:
                    st.write(f"• {ms}")

            # Timeline (your list of dict-like items)
            st.markdown("**Timeline**")
            for idx, t in enumerate(r.timeline, start=1):
                min = t.offset_end_min - t.offset_start_min
                h = min // 60
                min = min % 60
                st.write(
                    f"{idx}. **{t.attraction_name}** "
                    f"({h}hr {min}min) · "
                )
                if getattr(t, "travel_to_next_minutes", None) is not None:
                    st.caption(f"Travel to next: {t.travel_to_next_minutes} min")

            if st.button("Choose this plan", key=f"choose_{i}"):
                st.session_state.selected_route = r
                st.session_state.step = 3
                st.rerun()
    

def page_matching():
    st.header("Matching")

    if st.button("Back"):
        st.session_state.step = 2
        st.rerun()

    trip_request = st.session_state.get("trip_request")
    plan = st.session_state.get("selected_route")
    all_drivers = generate_driver("data_collection/Database/driver_identifier.csv")
    driver_score = generate_driver_scores(all_drivers, plan, trip_request)
    driver_with_total_price = driverplan_compat_adjust(driver_score, trip_request.chosen_date, plan.attractions, trip_request.budget)

    for i, dp in enumerate(driver_with_total_price[:10]):
        col_left, col_right = st.columns([3, 1])

        with col_left:
            st.subheader(f"{i+1}. {dp.driver.name}")

        with col_right:
            st.subheader(f"£{dp.total_price:.2f}")
      
        if st.button("Choose this driver", key=f"choose_driver_{i}"):
            st.session_state.selected_driver_price = dp
            st.success("Driver selected!")
            st.session_state.step = 4
            st.rerun()

def confirm_page():
    st.header("Confirm Plan and Driver")

    driver_price = st.session_state.get("selected_driver_price")
    plan = st.session_state.get("selected_route")
    trip_request = st.session_state.get("trip_request")

    if not driver_price or not plan:
        st.warning("Missing selection. Please choose a plan and a driver first.")
        return

    with st.expander("Trip details", expanded=True):
        st.write(f"**City:** {trip_request.city.capitalize()}")
        st.write(f"**Date:** {trip_request.chosen_date}")
        st.write(f"**Language:** {", ".join(trip_request.languages)}")
        st.write(f"**Service:** {trip_request.service.value}")

    with st.expander("Selected plan", expanded=True):
        st.write(f"**Plan Theme:** {plan.theme}")
        st.write("**Attractions:**")
        for a in plan.attractions:
            st.write(f"- {a.replace('_', ' ').title()}")

    st.subheader("Driver & Price")
    st.write(f"**Driver:** {driver_price.driver.name}")
    st.write(f"**Total price:** £{driver_price.total_price:.2f}")

    col_confirm, col_cancel = st.columns(2)

    with col_confirm:
        if st.button("✅ Confirm booking", type="primary"):
            st.session_state.step = 5
            st.rerun()

    with col_cancel:
        if st.button("❌ Cancel"):
            st.session_state.step = 3  # go back to matching page
            st.rerun()

    
def page_request_sent():
    st.header("✅ Request Sent")

    # simple “reference id” for demo
    if "request_id" not in st.session_state:
        st.session_state.request_id = f"REQ-{random.randint(100000, 999999)}"

    st.write(f"**Reference:** {st.session_state.request_id}")

    st.success(
        f"Your request has been sent. "
        f"We’ll notify you when they accept."
    )

    if st.button("Start new trip"):
        # reset only what you need
        for k in ["plans", "selected_plan", "selected_driver", "request_id", "request_time", "must_visits"]:
            st.session_state.pop(k, None)
        st.session_state.step = 1
        st.rerun()


# main

st.title("Tour Planner and Guide Matcher")
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
