import streamlit as st
import pandas as pd
from sensor import read_sensor_data  # Import the sensor data reading function

# Initialize session state to manage the current page and responses
if 'page' not in st.session_state:
    st.session_state.page = 0  # Start at 0 for the welcome page

if 'responses' not in st.session_state:
    st.session_state.responses = [None] * 10  # Adjust to the number of questions

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = []  # List to store sensor data for each question

if 'submitted' not in st.session_state:
    st.session_state.submitted = False  # Track whether the user has submitted

# Function to move to the next page
def next_page():
    if st.session_state.page < len(questions):
        st.session_state.page += 1
        st.rerun()

# Function to move to the previous page
def prev_page():
    if st.session_state.page > 1:  # Avoid going back to the welcome page
        st.session_state.page -= 1
        st.rerun()

# List of questions
questions = [
    "Pertanyaan 1: Bagaimana perasaan Anda dalam seminggu terakhir?",
    "Pertanyaan 2: Seberapa sering Anda merasa gelisah?",
    "Pertanyaan 3: Apakah Anda merasa sulit untuk tidur?",
    "Pertanyaan 4: Seberapa sering Anda merasa sedih tanpa alasan jelas?",
    "Pertanyaan 5: Apakah Anda sering merasa lelah?",
    "Pertanyaan 6: Seberapa sering Anda merasa tidak berharga?",
    "Pertanyaan 7: Seberapa sering Anda merasa tidak berdaya?",
    "Pertanyaan 8: Apakah Anda merasa sulit untuk berkonsentrasi?",
    "Pertanyaan 9: Seberapa sering Anda merasa putus asa?",
    "Pertanyaan 10: Seberapa sering Anda merasa kesulitan dalam menikmati aktivitas yang biasanya menyenangkan?"
]

# Function to display the initial page with instructions
def show_welcome_page():
    st.title("Kuesioner Psikologis untuk Prediksi Depresi")
    st.write("""
    Selamat datang di kuesioner prediksi depresi.
    Kuesioner ini berisi 10 pertanyaan yang dirancang untuk membantu mengidentifikasi
    kemungkinan tingkat depresi Anda. Harap menjawab dengan jujur.

    Setelah selesai, sistem akan memberikan prediksi tingkat depresi berdasarkan jawaban Anda.

    Klik tombol 'Isi Kuesioner' di bawah ini untuk memulai.
    """)
    if st.button("Isi Kuesioner"):
        st.session_state.page = 1  # Set the page to 1 to go to the first question
        st.rerun()

# Function to display a single question per page with real-time sensor data
def show_question_page(start_index):
    st.write("## 2D Depression Levels Measurement")
    col1, col2 = st.columns([1, 2])  # Adjust column width for more space on the right side

    with col1:
        st.write("#### Physical Dimension")

        # Fetch real-time sensor data from MAX30102
        heart_rate, oxygen_saturation, temperature = read_sensor_data()

        # Create a layout for 3 rows, each with 2 columns (value and label)
        for i in range(3):
            row_col1, row_col2 = st.columns(2)  # Create two columns for each row

            with row_col1:
                # Display heart rate, oxygen saturation, and temperature
                if i == 0:
                    value = heart_rate
                    label = "BPM"
                elif i == 1:
                    value = oxygen_saturation
                    label = "SpO2"
                else:
                    value = temperature
                    label = "Temp"

                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; border-radius: 10px; background-color: #ffffff; padding: 5px; margin-bottom: 10px;">
                    <b style="color: #5e17eb; font-size: 32px;">{value}</b>
                </div>
                """, unsafe_allow_html=True)

            with row_col2:
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; border-radius: 10px; background-color: #5e17eb; padding: 5px; margin-bottom: 5px;">
                    <b style="color: #ffffff; font-size: 18px;">{label}</b>
                </div>
                """, unsafe_allow_html=True)


        # Save the sensor data for the current question
        if len(st.session_state.sensor_data) <= start_index:
            st.session_state.sensor_data.append([heart_rate, oxygen_saturation, temperature])
        else:
            st.session_state.sensor_data[start_index] = [heart_rate, oxygen_saturation, temperature]

        

    with col2:
        st.write("#### Psychological Dimension")

        # Display a single question per page
        st.write(f"**{questions[start_index]}**")
        response = st.session_state.responses[start_index]

        # Create a horizontal layout for radio buttons
        st.markdown("""<div style="display: flex; justify-content: space-between;">""", unsafe_allow_html=True)

        # Display radio buttons horizontally
        selected_response = st.radio(
            f"Pilih jawaban untuk Pertanyaan {start_index+1}:",
            ("1", "2", "3", "4", "5"),
            index=0 if response is None else ["1", "2", "3", "4", "5"].index(response),
            key=f"q{start_index}",  # Ensuring the key is unique by including `start_index`
            horizontal=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.session_state.responses[start_index] = selected_response

        # Navigation buttons
        button_col1, button_col2 = st.columns([1, 1])
        with button_col1:
            if start_index > 0:
                if st.button("Sebelumnya"):
                    prev_page()

        with button_col2:
            if start_index < len(questions) - 1:
                if st.button("Lanjutkan"):
                    next_page()
            else:
                if st.button("Submit"):
                    st.session_state.page = len(questions) + 1  # Move to the result page
                    st.session_state.submitted = True
                    st.rerun()

# Function to calculate and display the result
def show_result_page():
    # Convert responses to numerical values (1-5)
    numerical_responses = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5
    }

    # Calculate total score
    total_score = sum(numerical_responses[response] for response in st.session_state.responses)

    # Store the sensor data for each question
    data = {
        f"Pertanyaan {i+1}": st.session_state.sensor_data[i] for i in range(10)
    }

    # Convert data to a pandas DataFrame for table display
    df = pd.DataFrame(data, index=["Heart Rate (BPM)", "Oxygen Saturation (%)", "Temperature (°C)"])

    st.write("#### Hasil Pengukuran Fisik dan Psikologis")
    st.table(df)

    # Display the total score
    st.write(f"Total Skor dari 10 Pertanyaan: **{total_score}**")

    # Display level of depression
    if total_score <= 15:
        st.write("#### Level Depresi: **Rendah**")
    elif 16 <= total_score <= 30:
        st.write("#### Level Depresi: **Sedang**")
    else:
        st.write("### Level Depresi: **Tinggi**")

    # Optional: Display sensor data again or relevant insights based on the score
    st.write("Hasil pengukuran ini adalah prediksi. Silakan konsultasi ke tenaga medis profesional jika diperlukan.")

# Main flow of the app
if st.session_state.page == 0:
    show_welcome_page()  # Show welcome page if page is 0
elif st.session_state.page == len(questions) + 1:
    show_result_page()  # Show the result page after submission
else:
    show_question_page(st.session_state.page - 1)  # Display questions starting from index 0
