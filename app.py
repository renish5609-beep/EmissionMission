import streamlit as st
import pandas as pd
from transformers import pipeline
from feedback import generate_feedback
import pydeck as pdk
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import io


def generate_pdf_report(total_emission, breakdown, comparison_text, feedback_list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []


    story.append(Paragraph("EmissionMission Report", styles["Title"]))
    story.append(Spacer(1, 12))


    story.append(Paragraph(f"Total Emissions: {total_emission:.2f} lbs CO₂/month", styles["Heading2"]))
    story.append(Spacer(1, 12))


    story.append(Paragraph("Breakdown:", styles["Heading3"]))
    for category, value in breakdown.items():
        story.append(Paragraph(f"{category}: {value:.2f} lbs", styles["Normal"]))
    story.append(Spacer(1, 12))


    if comparison_text:
        story.append(Paragraph("Comparison:", styles["Heading3"]))
        story.append(Paragraph(comparison_text, styles["Normal"]))
        story.append(Spacer(1, 12))


    if feedback_list:
        story.append(Paragraph("Suggestions:", styles["Heading3"]))
        for tip in feedback_list:
            story.append(Paragraph(f"• {tip}", styles["Normal"]))


    doc.build(story)
    buffer.seek(0)
    return buffer


st.set_page_config(page_title="EmissionMission", layout="centered")


pipe = pipeline("text-generation", model="gpt2")


state_averages = {
    "Texas": 1200,
"California": 900,
"New York": 850,
"Alabama": 780,
"New Jersey": 890,
"Pennsylvania": 750,
"Florida": 725,
"Louisiana": 730,
"Alaska": 715,
"Arizona": 740,
"Arkansas": 710,
"Colorado": 720,
"Connecticut": 735,
"Delaware": 745,
"Georgia": 760,
"Hawaii": 705,
"Idaho": 770,
"Illinois": 755,
"Indiana": 765,
"Iowa": 735,
"Kansas": 720,
"Kentucky": 710,
"Maine": 725,
"Maryland": 745,
"Massachusetts": 755,
"Michigan": 780,
"Minnesota": 770,
"Mississippi": 720,
"Missouri": 735,
"Montana": 705,
"Nebraska": 740,
"Nevada": 730,
"New Hampshire": 715,
"New Mexico": 725,
"North Carolina": 765,
"North Dakota": 710,
"Ohio": 775,
"Oklahoma": 720,
"Oregon": 705,
"Rhode Island": 715,
"South Carolina": 735,
"South Dakota": 710,
"Tennessee": 760,
"Utah": 720,
"Vermont": 730,
"Virginia": 740,
"Washington": 750,
"West Virginia": 710,
"Wisconsin": 725,
"Wyoming": 705,


}


country_average = 1000


page = st.sidebar.radio("Go to", ["🏠 Home", "📊 View Graph and Feedback", "📈 Comparison", "⚡ Energy Saving Calculator", "Nationwide Emissions Map 🗺️"])




if page == "🏠 Home":
    st.title("🏠 EmissionMission: Track Your Household Impact")
    st.markdown("Enter your household usage below:")


    with st.form("emission_form"):
        electricity_kwh = st.number_input("Electricity (kWh/month)", min_value=0.0)
        gas_therms = st.number_input("Natural Gas (therms/month)", min_value=0.0)
        water_gal = st.number_input("Water Usage (gallons/month)", min_value=0.0)
        internet_gb = st.number_input("Internet Usage (GB/month)", min_value=0.0)
        submitted = st.form_submit_button("Calculate Emissions")


    if submitted:
        elec_factor = 0.92
        gas_factor = 11.7
        water_factor = 0.0024
        internet_factor = 0.02


        elec_emission = electricity_kwh * elec_factor
        gas_emission = gas_therms * gas_factor
        water_emission = water_gal * water_factor
        internet_emission = internet_gb * internet_factor


        total_emission = elec_emission + gas_emission + water_emission + internet_emission


        st.session_state.total_emission = total_emission
        st.session_state.breakdown = {
            "Electricity": elec_emission,
            "Gas": gas_emission,
            "Water": water_emission,
            "Internet": internet_emission,
        }


        st.success("Emissions calculated! Go to 'View Graph and Feedback' or 'Comparison' to see your results.")




elif page == "📊 View Graph and Feedback":
    st.title("📊 Your Monthly Emissions Breakdown")


    if "total_emission" in st.session_state:
        breakdown = st.session_state.breakdown
        total = st.session_state.total_emission


        st.markdown(f"### Total Emissions: {total:.2f} lbs CO₂ per month")
        st.bar_chart(pd.DataFrame(breakdown, index=["Emissions (lbs CO₂)"]).T)


        st.markdown("### EmissionMission Suggestions")
        for item in generate_feedback(breakdown):
            st.success(item)


        st.markdown("---")
        st.markdown("### 💬 Need help? Ask our AI!")
        user_input = st.text_input("You:", key="chat_input")


        if user_input:
            with st.spinner("Thinking..."):
                results = pipe(user_input, max_length=100, do_sample=True, temperature=0.7)
                reply = results[0]['generated_text'][len(user_input):].strip()
                st.markdown(f"**AI:** {reply}")
    else:
        st.warning("Please calculate your emissions on the Home page first.")
if st.button("📄 Export to PDF"):
            comparison_text = ""
            if "Comparison" in st.session_state:
                comparison_text = st.session_state["Comparison"]


            pdf_buffer = generate_pdf_report(total, breakdown, comparison_text, generate_feedback(breakdown))
            st.download_button(
                label="Download Report",
                data=pdf_buffer,
                file_name="emission_report.pdf",
                mime="application/pdf",
            )




elif page == "📈 Comparison":
    st.title("📈 Emissions Comparison")


    user_state = st.text_input("Enter your state (e.g., Texas):").title().strip()


    if "total_emission" not in st.session_state:
        st.warning("Please calculate your emissions on the Home page first.")
    elif user_state == "":
        st.info("Please enter your state above to compare emissions.")
    else:
        user_emission = st.session_state.total_emission
        state_emission = state_averages.get(user_state, None)


        st.markdown(f"### Your Total Emissions: {user_emission:.2f} lbs CO₂/month")


        if state_emission:
            st.markdown(f"### Average Emissions for {user_state}: {state_emission} lbs CO₂/month")
            diff_state = user_emission - state_emission
            if diff_state > 0:
                st.markdown(f"**You are {diff_state:.2f} lbs above your state average.**")
            else:
                st.markdown(f"**You are {-diff_state:.2f} lbs below your state average. Good job!**")
        else:
            st.warning("State not found in dataset.")


        st.markdown(f"### National Average Emissions: {country_average} lbs CO₂/month")
        diff_country = user_emission - country_average
        if diff_country > 0:
            st.markdown(f"**You are {diff_country:.2f} lbs above the national average.**")
        else:
            st.markdown(f"**You are {-diff_country:.2f} lbs below the national average. Great!**")




elif page == "⚡ Energy Saving Calculator":
    st.title("⚡ Energy Saving Calculator")
    st.markdown("Estimate your monthly savings by reducing your utility usage.")


    with st.form("saving_form"):
        elec_current = st.number_input("Current Electricity (kWh/month)", min_value=0.0)
        elec_reduction = st.slider("Reduce electricity usage by (%)", 0, 100, 10)


        gas_current = st.number_input("Current Natural Gas (therms/month)", min_value=0.0)
        gas_reduction = st.slider("Reduce gas usage by (%)", 0, 100, 10)


        water_current = st.number_input("Current Water Usage (gallons/month)", min_value=0.0)
        water_reduction = st.slider("Reduce water usage by (%)", 0, 100, 10)


        internet_current = st.number_input("Current Internet Usage (GB/month)", min_value=0.0)
        internet_reduction = st.slider("Reduce internet usage by (%)", 0, 100, 10)


        submitted = st.form_submit_button("Calculate Savings")


    if submitted:
        elec_factor = 0.92
        gas_factor = 11.7
        water_factor = 0.0024
        internet_factor = 0.02


        elec_cost = 0.13
        gas_cost = 1.05
        water_cost = 0.005
        internet_cost = 0.10


        elec_saved = elec_current * (elec_reduction / 100)
        gas_saved = gas_current * (gas_reduction / 100)
        water_saved = water_current * (water_reduction / 100)
        internet_saved = internet_current * (internet_reduction / 100)


        emissions_saved = (
            elec_saved * elec_factor +
            gas_saved * gas_factor +
            water_saved * water_factor +
            internet_saved * internet_factor
        )


        cost_saved = (
            elec_saved * elec_cost +
            gas_saved * gas_cost +
            water_saved * water_cost +
            internet_saved * internet_cost
        )


        st.success(f"Estimated emissions saved: {emissions_saved:.2f} lbs CO₂")
        st.success(f"Estimated cost saved: ${cost_saved:.2f}")


elif page == "Nationwide Emissions Map 🗺️":
    st.title("🗺️ U.S. State Emissions Map")
    st.markdown("Hover over each state to view average monthly household CO₂ emissions (in lbs).")


    state_coords = {
    "Texas": [31.0, -99.0],
        "California": [36.7783, -119.4179],
        "New York": [43.0, -75.0],
        "Alabama": [32.8067, -86.7911],
        "New Jersey": [40.0583, -74.4057],
        "Florida": [27.766279, -81.686783],
        "Louisiana":[31.169546, -91.867805],
        "Alaska": [61.370716, -152.404419],
"Arizona": [33.729759, -111.431221],
"Arkansas": [34.969704, -92.373123],
"Colorado": [39.550051, -105.782067],
"Connecticut": [41.603221, -73.087749],
"Delaware": [38.910832, -75.52767],
"Georgia": [33.729759, -83.804901],
"Hawaii": [21.094318, -157.498337],
"Idaho": [44.240459, -114.478828],
"Illinois": [40.349457, -88.986137],
"Indiana": [39.849426, -86.258278],
"Iowa": [42.011539, -93.210526],
"Kansas": [38.5266, -96.726486],
"Kentucky": [37.66814, -84.670067],
"Maine": [45.253783, -69.445469],
"Maryland": [39.063946, -76.802101],
"Massachusetts": [42.230171, -71.530106],
"Michigan": [43.326618, -84.536095],
"Minnesota": [45.694454, -93.900192],
"Mississippi": [32.741646, -89.678696],
"Missouri": [38.456085, -92.288368],
"Montana": [46.921925, -110.454353],
"Nebraska": [41.12537, -98.268082],
"Nevada": [38.313515, -117.055374],
"New Hampshire": [43.452492, -71.563896],
"New Mexico": [34.840515, -106.248482],
"North Carolina": [35.630066, -79.806419],
"North Dakota": [47.528912, -99.784012],
"Ohio": [40.388783, -82.764915],
"Oklahoma": [35.565342, -96.928917],
"Oregon": [44.572021, -122.070938],
"Pennsylvania": [40.590752, -77.209755],
"Rhode Island": [41.680893, -71.51178],
"South Carolina": [33.856892, -80.945007],
"South Dakota": [44.299782, -99.438828],
"Tennessee": [35.747845, -86.692345],
"Utah": [40.150032, -111.862434],
"Vermont": [44.045876, -72.710686],
"Virginia": [37.769337, -78.169968],
"Washington": [47.400902, -121.490494],
"West Virginia": [38.491226, -80.954578],
"Wisconsin": [44.268543, -89.616508],
"Wyoming": [42.755966, -107.30249]


    }


    map_df = pd.DataFrame([
        {
            "state": state,
            "emissions": state_averages[state],
            "lat": state_coords[state][0],
            "lon": state_coords[state][1],
        }
        for state in state_averages if state in state_coords
    ])


    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_fill_color='[255, 140, 0, 160]',
        get_radius=30000,
        pickable=True,
    )


    view_state = pdk.ViewState(latitude=37.5, longitude=-96, zoom=3.5)


    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{state}: {emissions} lbs CO₂/month"}
    ))


