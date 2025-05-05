import streamlit as st
import numpy as np
import pandas as pd
import wave
import av
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
import io
import smtplib
from email.message import EmailMessage

# -------------------- Doctor Data --------------------
def convert_to_float(coord):
    try:
        if isinstance(coord, str):
            coord = coord.replace('°', '').replace('N', '').replace('E', '')
            coord = coord.replace('S', '-').replace('W', '-')
            coord = coord.replace('\u200b', '').strip()
        return float(coord)
    except:
        return None

@st.cache_data
def load_doctors_data():
    df = pd.read_excel("Best neurologists in all over India.xlsx")
    df['state'] = df['state'].astype(str).str.strip().str.title()
    df['city'] = df['city'].astype(str).str.strip().str.title()
    df['latitude'] = df['latitude'].apply(convert_to_float)
    df['longitude'] = df['longitude'].apply(convert_to_float)
    return df

doctors_df = load_doctors_data()

st.title("🧠 Parkinson's Unified Risk Assessment")

# -------------------- Voice Test --------------------
st.header("🎧 Voice Test (Live Recording)")

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame):
        self.recorded_frames.append(frame.to_ndarray())
        return frame

webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False}
)

if "voice_result" not in st.session_state:
    st.session_state.voice_result = None

if webrtc_ctx.audio_processor:
    st.info("Recording... Speak now for at least 5 seconds.")
    if st.button("Process Voice"):
        audio_data = np.concatenate(webrtc_ctx.audio_processor.recorded_frames, axis=0).flatten()
        if len(audio_data) > 80000:
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            zcr = zero_crossings / len(audio_data)
            st.write(f"🔍 Zero Crossing Rate: **{zcr:.4f}**")
            st.session_state.voice_result = "High Risk" if zcr > 0.1 else "Low Risk"
            st.success(f"Voice Test Result: **{st.session_state.voice_result}**")
        else:
            st.warning("Please speak for at least 5 seconds before processing.")

# -------------------- Questionnaire --------------------
st.header("🗘️ Questionnaire Test")
questions = [
    "Do you experience tremors frequently?",
    "Do you feel stiffness in muscles?",
    "Do you notice slow movements?",
    "Do you have balance problems?"
]
answers = [st.radio(q, ["Yes", "No"], key=q) for q in questions]
questionnaire_result = "High Risk" if "Yes" in answers else "Low Risk"
st.session_state.questionnaire_result = questionnaire_result
st.success(f"Questionnaire Result: **{questionnaire_result}**")

# -------------------- Typing Speed Test --------------------
st.header("⌨️ Typing Speed Test")
sentence = "The quick brown fox jumps over the lazy dog"
st.write(f"Type this sentence quickly: **{sentence}**")

if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "typing_result" not in st.session_state:
    st.session_state.typing_result = None

if st.button("Start Typing Test"):
    st.session_state.start_time = pd.Timestamp.now()

typed_text = st.text_input("Type here:")

if st.button("Submit Typing"):
    if st.session_state.start_time:
        end_time = pd.Timestamp.now()
        time_taken = (end_time - st.session_state.start_time).total_seconds()
        speed = len(typed_text) / time_taken if time_taken > 0 else 0
        st.session_state.typing_result = "Normal Typing Speed" if speed > 2 else "Slow Typing Speed"
        st.success(f"Typing Test Result: **{st.session_state.typing_result}**")
    else:
        st.error("Please click 'Start Typing Test' first!")

# -------------------- Final Assessment --------------------
st.header("\u2705 Final Assessment")

voice_result = st.session_state.get("voice_result")
questionnaire_result = st.session_state.get("questionnaire_result")
typing_result = st.session_state.get("typing_result")

risk_flags = sum([
    voice_result == "High Risk",
    questionnaire_result == "High Risk",
    typing_result == "Slow Typing Speed"
]) if voice_result and questionnaire_result and typing_result else 0

if voice_result and questionnaire_result and typing_result:
    if risk_flags == 0:
        final_result = "Low Risk of Parkinson's"
        video_url = "https://youtu.be/k3GyywA3QDY"
    elif risk_flags == 1:
        final_result = "Medium Risk of Parkinson's"
        video_url = "https://youtu.be/uOljoOvycuo"
    else:
        final_result = "High Risk of Parkinson's Detected"
        video_url = "https://youtu.be/M7gp61ObrgQ"

    st.subheader(f"🎯 **{final_result}**")
    st.session_state.final_result = final_result
else:
    st.warning("Please complete all 3 tests to get your final assessment.")
    video_url = None

# -------------------- Video & Diet --------------------
if video_url:
    st.markdown("### 🧘 Recommended Exercise Video")
    st.video(video_url)

st.markdown("### 🥗 Personalized Diet Plan")

if "final_result" in st.session_state:
    if "Low Risk" in st.session_state.final_result:
        st.markdown("""
        - **Balanced Diet:** Fruits, vegetables, whole grains, lean protein  
        - **Hydration:** 8+ glasses water  
        - **Omega-3:** Moderate fish/nuts intake  
        - **Low Processed Sugar:** Choose fruits over sweets  
        """)
    elif "Medium Risk" in st.session_state.final_result:
        st.markdown("""
        - **Anti-inflammatory Foods:** Leafy greens, turmeric, berries  
        - **Magnesium Rich:** Bananas, spinach, almonds  
        - **Healthy Fats:** Avocados, walnuts  
        - **Limit Dairy & Red Meat:** Choose plant-based protein  
        """)
    elif "High Risk" in st.session_state.final_result:
        st.markdown("""
        - **Neuroprotective Diet:** Omega-3 (salmon, flaxseed), berries, broccoli  
        - **High Fiber:** Oats, whole wheat, beans  
        - **Antioxidants:** Green tea, dark chocolate (small amount)  
        - **Strict Sugar/Sodium Control:** Avoid packaged food  
        """)

# -------------------- Progress Tracking --------------------
st.header("📈 Progress Tracking Dashboard")

progress_data = {
    "Voice Test": st.session_state.get("voice_result", "Not completed"),
    "Questionnaire": st.session_state.get("questionnaire_result", "Not completed"),
    "Typing Test": st.session_state.get("typing_result", "Not completed"),
    "Final Assessment": st.session_state.get("final_result", "Not completed")
}

progress_df = pd.DataFrame(list(progress_data.items()), columns=["Test", "Result"])
st.table(progress_df)

# -------------------- Save & Load Progress --------------------
st.header("💾 Save & Load Your Progress")

if st.button("Save Progress"):
    progress_to_save = {
        'voice_result': st.session_state.get('voice_result'),
        'questionnaire_result': st.session_state.get('questionnaire_result'),
        'typing_result': st.session_state.get('typing_result'),
        'final_result': st.session_state.get('final_result')
    }
    progress_df_save = pd.DataFrame([progress_to_save])
    buffer = io.BytesIO()
    progress_df_save.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("Download Progress File", buffer, file_name="parkinsons_progress.csv", mime="text/csv")
    
uploaded_file = st.file_uploader("Upload Progress File (.csv)", type=["csv"])

if uploaded_file is not None:
    loaded_progress = pd.read_csv(uploaded_file)
    if not loaded_progress.empty:
        st.session_state['voice_result'] = loaded_progress['voice_result'][0]
        st.session_state['questionnaire_result'] = loaded_progress['questionnaire_result'][0]
        st.session_state['typing_result'] = loaded_progress['typing_result'][0]
        st.session_state['final_result'] = loaded_progress['final_result'][0]
        st.success("✅ Progress loaded successfully! Please check the dashboard above.")

# -------------------- Doctor Map --------------------
st.header("\U0001f5fa️ Find Nearby Neurologists")

state = st.selectbox("Select State", sorted(doctors_df['state'].dropna().unique()))
city = st.selectbox("Select City", sorted(doctors_df[doctors_df['state'] == state]['city'].dropna().unique()))

filtered_doctors = doctors_df[
    (doctors_df['state'] == state) &
    (doctors_df['city'] == city) &
    doctors_df['latitude'].notnull() &
    doctors_df['longitude'].notnull()
]

if not filtered_doctors.empty:
    st.success(f"Neurologists available in {city}, {state}:")
    for _, row in filtered_doctors.iterrows():
        st.write(f"🩺 **{row['name']}**")
        st.write(f"🏥 {row['hospital']}")
        st.write(f"📞 Contact: {row['contact']}")
        st.markdown("---")

    m = folium.Map(location=[filtered_doctors['latitude'].mean(), filtered_doctors['longitude'].mean()], zoom_start=10)
    for _, row in filtered_doctors.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=row['name'],
            popup=f"<b>{row['name']}</b><br>{row['hospital']}<br>📞 {row['contact']}",
            icon=folium.Icon(color='red', icon='user-md', prefix='fa')
        ).add_to(m)
    st_folium(m, width=700, height=400)

# -------------------- Appointment Booking --------------------
st.markdown("### 🗓️ Book an Appointment")

if not filtered_doctors.empty:
    selected_doctor = st.selectbox("Choose a doctor", filtered_doctors['name'])
    patient_name = st.text_input("Your Name")
    patient_contact = st.text_input("Your Phone Number")
    preferred_date = st.date_input("Preferred Appointment Date")

    if st.button("Confirm Appointment"):
        st.success(f"✅ Appointment booked with **{selected_doctor}** on **{preferred_date}**.")
        st.info("Please contact the clinic directly to confirm the time slot.")

# -------------------- Email Progress Report --------------------
st.header("📧 Email Your Progress Report")

recipient_email_progress = st.text_input("Enter your email to receive your progress report")

if st.button("Send Progress Report"):
    if not recipient_email_progress:
        st.warning("Please enter your email address.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Parkinson's Progress Report", ln=True, align='C')
        pdf.ln(10)

        for test_name, result in progress_data.items():
            pdf.cell(200, 10, txt=f"{test_name}: {result}", ln=True)

        pdf_bytes = pdf.output(dest='S').encode('latin-1')

        msg = EmailMessage()
        msg['Subject'] = "Your Parkinson's Progress Report"
        msg['From'] = "anweshasarkar2001@gmail.com"  # Replace
        msg['To'] = recipient_email_progress
        msg.set_content("Hi, please find attached your current progress report.")
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename="Parkinsons_Progress_Report.pdf")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("anweshasarkar2001@gmail.com", "hntt cwwm xmtd ctep")  # Replace
                smtp.send_message(msg)
            st.success("✅ Progress report sent successfully to your email!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
            # ... (keep your entire existing code unchanged up to the Email Progress Report section)

# -------------------- Medication Reminder System --------------------
st.header("💊 Medication Reminder System")

if "medications" not in st.session_state:
    st.session_state.medications = []

with st.form("medication_form", clear_on_submit=True):
    med_name = st.text_input("Medication Name")
    dose = st.text_input("Dosage (e.g., 1 tablet)")
    time_of_day = st.time_input("Time of Day")
    frequency = st.selectbox("Frequency", ["Daily", "Weekly"])
    notes = st.text_area("Notes (optional)")
    submit = st.form_submit_button("Add Reminder")

if submit:
    reminder = {
        "med_name": med_name,
        "dose": dose,
        "time_of_day": time_of_day.strftime("%H:%M"),
        "frequency": frequency,
        "notes": notes,
        "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.medications.append(reminder)
    st.success(f"✅ Added reminder for {med_name} at {reminder['time_of_day']} ({frequency})")

# Display existing reminders
if st.session_state.medications:
    st.subheader("🗓️ Your Medication Reminders")
    for idx, med in enumerate(st.session_state.medications):
        st.write(f"**{med['med_name']}** - {med['dose']} at {med['time_of_day']} ({med['frequency']})")
        if med['notes']:
            st.write(f"📝 {med['notes']}")
        st.markdown("---")

# -------------------- Save & Load Reminders --------------------
st.markdown("### 💾 Save & Load Medication Reminders")

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Save Reminders to File"):
        df_meds = pd.DataFrame(st.session_state.medications)
        df_meds.to_csv("medication_reminders.csv", index=False)
        st.success("✅ Reminders saved successfully.")

with col2:
    if st.button("📂 Load Reminders from File"):
        try:
            df_loaded = pd.read_csv("medication_reminders.csv")
            st.session_state.medications = df_loaded.to_dict('records')
            st.success("✅ Reminders loaded successfully.")
        except FileNotFoundError:
            st.error("❌ No saved reminders found.")

# -------------------- Email Medication Reminders --------------------
st.markdown("### 📧 Email Today's Medication Reminders")

recipient_email_meds = st.text_input("Enter your email to receive today's medication reminders")

if st.button("Send Medication Reminders by Email"):
    today_day = pd.Timestamp.now().strftime("%A")
    today_meds = [
        med for med in st.session_state.medications
        if med['frequency'] == 'Daily' or (med['frequency'] == 'Weekly' and today_day == 'Monday')  # customize if needed
    ]

    if not recipient_email_meds:
        st.warning("Please enter your email address.")
    elif not today_meds:
        st.info("No medications scheduled for today.")
    else:
        message_body = "Here are your medication reminders for today:\n\n"
        for med in today_meds:
            message_body += f"- {med['med_name']} ({med['dose']}) at {med['time_of_day']}\n"
            if med['notes']:
                message_body += f"  Notes: {med['notes']}\n"

        msg = EmailMessage()
        msg['Subject'] = "Today's Medication Reminders"
        msg['From'] = "anweshasarkar2001@gmail.com"  # Replace with your email
        msg['To'] = recipient_email_meds
        msg.set_content(message_body)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("anweshasarkar2001@gmail.com", "hntt cwwm xmtd ctep")  # Replace with your app password
                smtp.send_message(msg)
            st.success("✅ Medication reminders sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")










