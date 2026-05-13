import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

# Add current directory to path for backend imports
sys.path.append(os.path.dirname(__file__))

from backend.data_processor import DataProcessor

st.set_page_config(
    page_title="Silverleaf Ops Insight",
    page_icon="🌿",
    layout="wide",
)

processor = DataProcessor()

DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "fee_records.csv")


@st.cache_data
@st.cache_data
def load_sample_data():
    return processor.load_csv(SAMPLE_CSV_PATH)


@st.cache_data
def load_uploaded_data(uploaded_file):
    return processor.load_csv(uploaded_file)


def format_currency(value):
    return f"{value:,.0f}"


def format_percent(value):
    return f"{value:.1f}%"


def render_metrics(report):
    stats = report["overall_stats"]
    st.markdown("### Collection Snapshot")
    cols = st.columns(6)
    cols[0].metric("Total Due (TZS)", format_currency(stats["total_due"]))
    cols[1].metric("Total Collected (TZS)", format_currency(stats["total_paid"]))
    cols[2].metric("Collection Rate", format_percent(stats["overall_collection_rate"]))
    cols[3].metric("Outstanding (TZS)", format_currency(stats["overall_outstanding"]))
    cols[4].metric("Students", stats["total_students"])
    cols[5].metric("Anomalies Flagged", report["anomaly_count"])


def render_charts(campus_df):
    st.markdown("### Campus Analytics")
    col1, col2 = st.columns(2)
    col1.bar_chart(campus_df[["collection_rate"]])
    col2.bar_chart(campus_df[["outstanding"]])


def render_campus_table(campus_df):
    st.markdown("### Campus Breakdown")
    st.dataframe(campus_df.rename(columns={
        "student_count": "Students",
        "total_due": "Total Due",
        "total_paid": "Total Paid",
        "outstanding": "Outstanding",
        "collection_rate": "Collection Rate",
    }), use_container_width=True)


def render_anomalies(anomalies):
    st.markdown("### Flagged Anomalies")
    if not anomalies:
        st.success("No anomalies detected.")
        return

    df = pd.DataFrame(anomalies)
    high = df[df["severity"] == "high"]
    medium = df[df["severity"] == "medium"]

    if not high.empty:
        with st.expander(f"High severity anomalies ({len(high)})", expanded=True):
            st.dataframe(high[['student_id', 'campus', 'amount_due', 'flag_reason']].rename(columns={
                'student_id': 'Student ID',
                'campus': 'Campus',
                'amount_due': 'Amount Due',
                'flag_reason': 'Reason'
            }), use_container_width=True)

    if not medium.empty:
        with st.expander(f"Medium severity anomalies ({len(medium)})", expanded=False):
            st.dataframe(medium[['student_id', 'campus', 'amount_due', 'flag_reason']].rename(columns={
                'student_id': 'Student ID',
                'campus': 'Campus',
                'amount_due': 'Amount Due',
                'flag_reason': 'Reason'
            }), use_container_width=True)


def main():
    st.title("🌿 Silverleaf Ops Insight")
    st.write(
        "A Streamlit dashboard for fee collection analytics, outstanding balances, and anomaly detection across Silverleaf campuses."
    )

    with st.sidebar:
        st.header("Upload Data")
        uploaded_file = st.file_uploader(
            "Upload fee records CSV",
            type=["csv"],
            help="Columns expected: campus, student_id, amount_due, amount_paid, last_payment_date",
        )
        use_sample = st.button("Load Sample Data")
        st.markdown("---")
        st.markdown(
            "**Notes:**\n\n- Use the sample data to explore the dashboard quickly.\n- Upload your own CSV to analyze real fee records.\n- This tool is built for Tanzania with TZS reporting and low-bandwidth compatibility."
        )

    report = None
    df = None

    if uploaded_file is not None:
        try:
            df = load_uploaded_data(uploaded_file)
            report = processor.generate_report(df)
        except Exception as e:
            st.error(f"Unable to load CSV: {e}")
    elif use_sample:
        try:
            df = load_sample_data()
            report = processor.generate_report(df)
        except Exception as e:
            st.error(f"Unable to load sample data: {e}")

    if report is not None:
        render_metrics(report)
        campus_df = pd.DataFrame(report["by_campus"]).T
        campus_df = campus_df[['student_count', 'total_due', 'total_paid', 'outstanding', 'collection_rate']]
        campus_df['collection_rate'] = campus_df['collection_rate'].astype(float)
        campus_df = campus_df.sort_values(by='collection_rate', ascending=False)

        render_charts(campus_df)
        render_campus_table(campus_df)
        render_anomalies(report["anomalies"])
        st.markdown("---")
        st.write("Report generated:", datetime.fromisoformat(report['timestamp']).strftime('%Y-%m-%d %H:%M:%S'))

        with st.expander("View raw data", expanded=False):
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Upload a CSV file or click 'Load Sample Data' to start.")


if __name__ == '__main__':
    main()
