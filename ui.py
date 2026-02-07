import streamlit as st
from datetime import date, timedelta, datetime
import loading_files

# pages
def page_trip_setup():
    st.header("Trip Setup")

    # name
    name = st.text_input("Your name")

    # date
    start_date = st.date_input(
        "Start date",
        value = date.today()
    )
    end_date = st.date_input(
        "End date",
        value = start_date + timedelta(days=3),
        min_value = start_date
    )

    days = (end_date - start_date).days
    st.write("Trip duration:", days, "days")

    # language
    language = st.selectbox("Choose your preffered language:", ["a", "b"])

    # city
    city = st.selectbox("Choose a city", ["Oxford", "London", "Bristol"])

    # attraction
    #attractions = loading_files.load_attractions_by_city(city)
    attractions = ["s"]
    
    must_visits = st.multiselect(
        "Choose attractions (multiple allowed)",
        attractions,
        default = []
    )

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
    budget_max = st.slider("Maximum budget (£)", 0, 10000, 800, step=50)

    if st.button("Next"):
        st.session_state.name = name
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.days = days
        st.session_state.language = language
        st.session_state.city = city
        st.session_state.must_visits = must_visits
        st.session_state.preference_text = preference_text
        st.session_state.service = service
        st.session_state.budget_max = budget_max
        st.session_state.step = 2


def page_plans():
    st.header("Choose Plan")

    if st.button("Back"):
        st.session_state.step = 1

    # Generate plans ONCE
    plans = generate_five_plans(
        city = st.session_state.city,
        must_visits = st.session_state.must_visits,
        days = st.session_state.days
        service = st.session_state.service
    )

    # Display the 5 plans
    for i, plan in enumerate(["we", "s"]):
        with st.expander(f"Plan {i+1}: {plan.title}", expanded=(i == 0)):
            st.caption(plan.reason)

            for day in plan.days:
                st.markdown(f"**Day {day.day}**")
                for item in day.items:
                    st.write(f"• {item.name}")

            if st.button("Choose this plan", key=f"choose_{i}"):
                st.session_state.selected_plan = plan
                st.session_state.step = 3
                st.rerun()
    

def page_matching():
    st.header("Matching")

    if st.button("Back"):
        st.session_state.step = 2

    drivers = match_drivers(st.session_state.plan) #todo: add parameter
    
    for i, d in enumerate(drivers):
      st.subheader(f"{i+1}. {d.name}")
      st.write("🗺 Can explain:", ", ".join(d.attractions))

      if st.button("Choose this driver", key=f"choose_driver_{i}"):
          st.session_state.selected_driver = d
          st.success("Driver selected!")
          st.session_state.step = 3


def page_request_sent():
    st.header("✅ Request Sent")

    driver = st.session_state.get("driver")
    plan = st.session_state.get("plan")

    if not driver or not plan:
        st.warning("Missing selection. Please choose a plan and a driver first.")
        return

    # simple “reference id” for demo
    if "request_id" not in st.session_state:
        st.session_state.request_id = f"REQ-{random.randint(100000, 999999)}"
        st.session_state.request_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.success(
        f"Your request has been sent to **{driver.name}**. "
        f"We’ll notify you when they accept."
    )

    st.write(f"**Reference:** {st.session_state.request_id}")
    st.write(f"**Time:** {st.session_state.request_time}")

    with st.expander("Trip details", expanded=True):
        st.write(f"**City:** {st.session_state.get('city')}")
        st.write(f"**Dates:** {st.session_state.get('start_date')} → {st.session_state.get('end_date')}")
        st.write(f"**Language:** {st.session_state.get('language')}")
        st.write(f"**Service:** {st.session_state.get('service')}")

    with st.expander("Selected plan", expanded=True):
        st.subheader(plan.title)

        # show day-by-day if you have it
        for day in plan.days:
            st.markdown(f"**Day {day.day}**")
            for item in day.items:
                st.write(f"• {item.name}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to drivers"):
            st.session_state.step = 3  # set this to your driver selection page number
            st.rerun()
    with col2:
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
    page_request_sent()
