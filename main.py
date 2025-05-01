import streamlit as st
import mysql.connector
from datetime import datetime
import pandas as pd  # Added for DataFrame support
from streamlit_lottie import st_lottie
import requests

# ------------------ DATABASE CONNECTION ------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="niru",  
        database="hospitaldb"
    )

# ------------------ AUTHENTICATION ------------------
def verify_user(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as err:
        st.error(f"❌ Error: {err}")
        return None

# ------------------ PATIENT FUNCTIONS ------------------
def insert_patient(pid, name, age, gender, dob):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patient (P_ID, Name, Age, Gender, DOB) VALUES (%s, %s, %s, %s, %s)",
            (pid, name, age, gender, dob)
        )
        conn.commit()
        st.success(f"✅ Patient {name} (ID: {pid}) added successfully!")
    except mysql.connector.Error as err:
        st.error(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()

def get_patients():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def search_patient(search_term):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient WHERE P_ID = %s OR Name LIKE %s", (search_term, f"%{search_term}%"))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# ------------------ BILL FUNCTIONS ------------------
def insert_bill(bid, pid, amount, bill_date):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.callproc("AddBill", (bid, pid, amount, bill_date))
        conn.commit()
        st.success(f"✅ Bill {bid} (₹{amount}) added on {bill_date} for Patient {pid}!")
    except mysql.connector.Error as err:
        st.error(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()


def get_bills():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def search_bills_by_pid(pid):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills WHERE P_ID = %s", (pid,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# ------------------ APPOINTMENT FUNCTIONS ------------------
def insert_appointment(aid, pid, doctor_name, date, time, reason):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (A_ID, P_ID, Doctor_Name, Appointment_Date, Appointment_Time, Reason) VALUES (%s, %s, %s, %s, %s, %s)",
            (aid, pid, doctor_name, date, time, reason)
        )
        conn.commit()
        st.success(f"✅ Appointment {aid} scheduled with Dr. {doctor_name} on {date} at {time}")
    except mysql.connector.Error as err:
        st.error(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()

def get_appointments():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# ------------------ SESSION MANAGEMENT ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# ------------------ LOGIN PAGE ------------------
if not st.session_state.logged_in:
    st.set_page_config(page_title="🏥 Login - Hospital System", layout="centered")
    st.title("🔐 Login to Hospital Management System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = verify_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# ------------------ MAIN DASHBOARD ------------------
st.set_page_config(page_title="🏥 Hospital Management System", layout="wide")
st.title("🏥 Hospital Management Dashboard")

# Sidebar
st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.username}`")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

menu = ["Home", "Add Patient", "View Patients", "Add Bill", "View Bills", "Search Patient", 
        "Search Bill by Patient ID", "Schedule Appointment", "View Appointments"]
choice = st.sidebar.selectbox("📂 Menu", menu)

# ------------------ PAGES ------------------
if choice == "Home":
    st.markdown("## 👋 Welcome to **Hospital Management System**")
    st.markdown("Efficiently manage patients, billing, and records with a seamless interface.")

    # Overview Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="👨‍⚕️ Total Patients", value=len(get_patients()))
    with col2:
        st.metric(label="💰 Total Bills", value=f"₹ {sum([b[2] for b in get_bills()])}")
    with col3:
        st.metric(label="📅 Today", value=datetime.now().strftime("%d %B %Y"))

    st.markdown("---")
    # Rest of Home page remains the same...

elif choice == "Add Patient":
    st.subheader("➕ Add New Patient")
    with st.form(key="add_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            pid = st.number_input("Patient ID", min_value=1, step=1)
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1))
        submit = st.form_submit_button("Add Patient")
        if submit:
            insert_patient(pid, name, age, gender, dob)

elif choice == "View Patients":
    st.subheader("📋 All Patients")
    data = get_patients()
    if data:
        df = pd.DataFrame(data, columns=["Patient ID", "Name", "Age", "Gender", "Date of Birth"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No patient records found.")

elif choice == "Add Bill":
    st.subheader("🧾 Add New Bill")
    with st.form(key="add_bill_form"):
        bid = st.number_input("Bill ID", min_value=1, step=1)
        pid = st.number_input("Patient ID", min_value=1, step=1)
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        bill_date = st.date_input("Bill Date", value=datetime.today())
        submit_bill = st.form_submit_button("Add Bill")
        if submit_bill:
            insert_bill(bid, pid, amount, bill_date)


elif choice == "View Bills":
    st.subheader("💳 Patient Bills")
    data = get_bills()
    if data:
        df = pd.DataFrame(data, columns=["Bill ID", "Patient ID", "Amount", "Bill Date"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No bill records found.")

elif choice == "Search Patient":
    st.subheader("🔍 Search Patient by ID or Name")
    search_term = st.text_input("Enter Patient ID or Name")
    if st.button("Search"):
        result = search_patient(search_term)
        if result:
            df = pd.DataFrame(result, columns=["Patient ID", "Name", "Age", "Gender", "Date of Birth"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No matching patient found.")

elif choice == "Search Bill by Patient ID":
    st.subheader("🔎 Search Bills by Patient ID")
    pid = st.number_input("Enter Patient ID", min_value=1, step=1)
    if st.button("Search Bills"):
        result = search_bills_by_pid(pid)
        if result:
            df = pd.DataFrame(result, columns=["Bill ID", "Patient ID", "Amount", "Bill Date"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No bills found for this patient.")

elif choice == "Schedule Appointment":
    st.subheader("📅 Schedule an Appointment")
    with st.form("appointment_form"):
        aid = st.number_input("Appointment ID", min_value=1)
        pid = st.number_input("Patient ID", min_value=1)
        doctor_name = st.text_input("Doctor's Name")
        date = st.date_input("Appointment Date")
        time = st.time_input("Appointment Time")
        reason = st.text_area("Reason for Visit")
        submit = st.form_submit_button("Schedule")
        if submit:
            insert_appointment(aid, pid, doctor_name, date, time, reason)

elif choice == "View Appointments":
    st.subheader("📋 All Appointments")
    data = get_appointments()
    if data:
        df = pd.DataFrame(data, columns=[
            "Appointment ID", "Patient ID", "Doctor Name", 
            "Appointment Date", "Appointment Time", "Reason"
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No appointments found.")