import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Data Sentinel", layout="wide")

st.title("🧠 Data Sentinel - Data Quality Dashboard")

# ----------------------------
# Initialize state safely
# ----------------------------
data = None

# ----------------------------
# Upload file
# ----------------------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    response = requests.post(
        f"{API_URL}/upload-csv",
        files={"file": (uploaded_file.name, uploaded_file, "text/csv")}
    )

    if response.status_code == 200:
        data = response.json()
        report = data["report"]

        st.success(f"Dataset ID: {data.get('id', 'N/A')}")

        # ----------------------------
        # Score display
        # ----------------------------
        st.metric(
            label="Dataset Health Score",
            value=f"{report.get('dataset_health_score', 0)} / 100"
        )

        # ----------------------------
        # Column health table
        # ----------------------------
        st.subheader("Column Health")

        df_health = pd.DataFrame(report.get("column_health", {})).T
        st.dataframe(df_health)

        # ----------------------------
        # Missing values
        # ----------------------------
        st.subheader("Missing Values")

        df_missing = pd.DataFrame.from_dict(
            report.get("missing_values", {}),
            orient="index",
            columns=["missing_count"]
        )

        st.bar_chart(df_missing)

    else:
        st.error(response.text)

# ----------------------------
# AI INSIGHTS (SAFE RENDERING)
# ----------------------------
st.subheader("🧠 AI Insights")

if data and data.get("ai_insight"):
    st.markdown(data["ai_insight"])

elif uploaded_file:
    st.info("AI insights not available for this dataset.")

# ----------------------------
# Historical reports
# ----------------------------
st.divider()
st.subheader("📚 Saved Reports")

if st.button("Load Reports"):
    res = requests.get(f"{API_URL}/reports")

    if res.status_code == 200:
        reports = res.json()

        df = pd.DataFrame(reports)
        st.dataframe(df)
    else:
        st.error("Failed to fetch reports")