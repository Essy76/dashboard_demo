import streamlit as st
import pandas as pd
import plotly.express as px
import os

def check_password():
    def password_entered():
        if st.session_state["password"] == "Welcome_Downer_123":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect password")
        return False
    else:
        return True

if check_password():
    st.write("🎉 Welcome to the dashboard!")
    
    st.set_page_config("📊 Special Reader Dashboard", layout="wide")
    st.title("📊 Special Reader Dashboard")

    # === Upload Box (optional) ===
    uploaded_file = st.file_uploader("Upload a new .xlsx file (optional)", type=["xlsx"])

    # === Load Data ===
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        source = "Uploaded file"
    else:
        default_path = "dwn_aml_29-May-2024.xlsx"
        if os.path.exists(default_path):
            df = pd.read_excel(default_path, engine="openpyxl")
            source = "Default file"
        else:
            st.error("No file uploaded, the default file is missing.")
            st.stop()

    st.caption(f"📄 Using data from: **{source}**")

    # === Clean column names ===
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # === Filter out columns like DO_NOT_IMPORT ===
    df = df[[col for col in df.columns if not col.startswith("DO_NOT_IMPORT")]]

    # === Meter Reader dropdown ===
    meter_readers = df['Meter_Reader'].dropna().unique()
    col1, col2, col3 = st.columns([1, 2, 7])  # Total is 10; col2 is ~20%
    with col2:
        st.markdown("### 👤 Special Reader")  # Label above dropdown
        selected_reader = st.selectbox(
        "Special Reader",  # Give it a real label
        sorted(meter_readers),
        label_visibility="collapsed"  # This hides the label but keeps it accessible
        )

    reader_df = df[df['Meter_Reader'] == selected_reader]

    st.subheader(f"📋 Jobs for {selected_reader}")
    st.dataframe(reader_df[['MIRN', 'METER_NO', 'ADDRESS', 'Job_Type']], use_container_width=True)

    # === Job Type Count for this reader ===
    job_counts = reader_df['Job_Type'].value_counts().reset_index()
    job_counts.columns = ['Job Type', 'Count']
    fig_job_type = px.bar(job_counts, x='Job Type', y='Count',
                        title=f"{selected_reader} - Job Type Counts",
                        color='Job Type', text='Count')
    st.plotly_chart(fig_job_type, use_container_width=True)

    # === Total Job Count for All Readers ===
    st.subheader("📊 Total Jobs by Meter Reader")
    all_reader_counts = df['Meter_Reader'].value_counts().reset_index()
    all_reader_counts.columns = ['Meter Reader', 'Job Count']

    fig_all_pct = px.bar(
        all_reader_counts.sort_values('Job Count'),
        x='Job Count',
        y='Meter Reader',
        orientation='h',
        text='Job Count',
        title='Total Jobs by Meter Reader',
        labels={'Job Count': 'Number of Jobs', 'Meter Reader': 'Reader'}
    )
    fig_all_pct.update_traces(marker_color='steelblue', textposition='outside')
    st.plotly_chart(fig_all_pct, use_container_width=True)

    with st.expander("🔍 View Reader Job Counts Table"):
        st.dataframe(all_reader_counts, use_container_width=True)
