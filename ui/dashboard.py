import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="PulseGuard AI Observability",
    layout="wide"
)

# ------------------------------------------------
# PREMIUM HEADER
# ------------------------------------------------

st.markdown(
"""
<h1 style='text-align:center;
background: linear-gradient(90deg,#00c6ff,#0072ff);
-webkit-background-clip: text;
color: transparent;
font-size:48px;'>
🚀 PulseGuard AI Observability Dashboard
</h1>
""",
unsafe_allow_html=True
)

st.markdown("---")

# ------------------------------------------------
# GLOBAL REFRESH
# ------------------------------------------------

col1, col2 = st.columns([10,1])

with col2:
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

# ------------------------------------------------
# API FUNCTIONS
# ------------------------------------------------

def fetch(endpoint):
    try:
        r = requests.get(f"{API}{endpoint}")
        return r.json()
    except:
        return []

def investigate(question):
    try:
        r = requests.post(
            f"{API}/investigate",
            json={"question": question}
        )
        return r.json()
    except:
        return {"error": "API not reachable"}

# ------------------------------------------------
# OVERVIEW METRICS
# ------------------------------------------------

overview = fetch("/dashboard/overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🚨 Total Incidents", overview.get("total_incidents",0))

with col2:
    st.metric("🖥 Services Monitored", 7)

with col3:
    st.metric("⚡ System Health", "Operational")

st.divider()

# ------------------------------------------------
# TABS
# ------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Live Incidents",
    "📜 Incident History",
    "📊 Service Metrics",
    "📜 Logs & Dependencies",
    "🧠 AI Investigation"
])

# ------------------------------------------------
# LIVE INCIDENTS
# ------------------------------------------------

with tab1:

    col1, col2 = st.columns([10,1])

    with col1:
        st.subheader("Live Incident Feed")

    with col2:
        if st.button("Refresh", key="live"):
            st.rerun()

    data = fetch("/incidents/live")

    if data:

        df = pd.DataFrame(data)

        st.dataframe(df, use_container_width=True)

    else:

        st.success("No active incidents")

# ------------------------------------------------
# INCIDENT HISTORY
# ------------------------------------------------

with tab2:

    col1, col2 = st.columns([10,1])

    with col1:
        st.subheader("Incident History")

    with col2:
        if st.button("Refresh", key="history"):
            st.rerun()

    data = fetch("/incidents")

    if data:

        df = pd.DataFrame(data)

        st.dataframe(df, use_container_width=True)

    else:

        st.info("No incidents available")

# ------------------------------------------------
# SERVICE METRICS
# ------------------------------------------------

with tab3:

    col1, col2 = st.columns([10,1])

    with col1:
        st.subheader("Service Metrics")

    with col2:
        if st.button("Refresh", key="metrics"):
            st.rerun()

    services = [
        "auth-service",
        "payment-service",
        "order-service",
        "inventory-service",
        "search-service",
        "notification-service"
    ]

    service = st.selectbox("Select Service", services)

    metrics = fetch(f"/metrics/{service}")
    errors = fetch(f"/metrics/{service}/errors")
    latency = fetch(f"/metrics/{service}/latency")

    if metrics:

        df = pd.DataFrame(metrics)

        st.subheader("System Metrics")

        st.line_chart(df[["cpu","memory","latency","error_rate"]])

   

    service_incidents = fetch(f"/services/{service}/incidents")

    if service_incidents:

        st.subheader("Incidents for Selected Service")

        df = pd.DataFrame(service_incidents)

        st.dataframe(df, use_container_width=True)

# ------------------------------------------------
# LOGS + DEPENDENCIES
# ------------------------------------------------

with tab4:

    col1, col2 = st.columns([10,1])

    with col1:
        st.subheader("Logs & Service Dependencies")

    with col2:
        if st.button("Refresh", key="logs"):
            st.rerun()

    service = st.selectbox(
        "Select Service",
        [
            "Notification-service",
            "auth-service",
            "payment-service",
            "order-service",
            "inventory-service"
        ],
        key="log_service"
    )

    logs = fetch(f"/logs/{service}")

    if logs:

        st.subheader("Recent Logs")

        df = pd.DataFrame(logs)

        st.dataframe(df, use_container_width=True)

    trace = fetch(f"/trace/{service}")

    if trace:

        st.subheader("Service Dependencies")

        st.write("Service:", trace["service"])

        if trace["dependencies"]:

            for dep in trace["dependencies"]:

                st.write("➡️", dep)

        else:

            st.write("No dependencies")

# ------------------------------------------------
# AI INVESTIGATION
# ------------------------------------------------

with tab5:

    st.subheader("🧠 PulseGuard AI Root Cause Investigation")

    question = st.text_input(
        "Ask PulseGuard",
        placeholder="Why is payment-service failing?"
    )

    col1, col2 = st.columns([2,10])

    with col1:
        run = st.button("Investigate")

    if run and question:

        with st.spinner("Running AI investigation..."):

            result = investigate(question)

            if "analysis" in result:

                analysis = result["analysis"]

                st.success("Investigation Completed")

                st.markdown("---")

                # -----------------------------------
                # PARSE AI RESPONSE
                # -----------------------------------

                sections = analysis.split("##")

                service = ""
                timeline = ""
                root = ""
                impact = ""
                fixes = ""

                for sec in sections:

                    if "Service" in sec:
                        service = sec.replace("Service","").strip()

                    elif "Incident Timeline" in sec:
                        timeline = sec.replace("Incident Timeline","").strip()

                    elif "Root Cause" in sec:
                        root = sec.replace("Root Cause","").strip()

                    elif "Impact" in sec:
                        impact = sec.replace("Impact","").strip()

                    elif "Recommended Fix" in sec:
                        fixes = sec.replace("Recommended Fix","").strip()

                # -----------------------------------
                # SERVICE CARD
                # -----------------------------------

                if service:
                    st.markdown("### 🔧 Service")
                    st.info(service)

                # -----------------------------------
                # INCIDENT TIMELINE
                # -----------------------------------

                if timeline:

                    st.markdown("### ⏱ Incident Timeline")

                    for line in timeline.split("\n"):
                        if line.strip():
                            st.write("•", line)

                # -----------------------------------
                # ROOT CAUSE
                # -----------------------------------

                if root:

                    st.markdown("### 🚨 Root Cause")

                    st.error(root)

                # -----------------------------------
                # IMPACT
                # -----------------------------------

                if impact:

                    st.markdown("### 📉 Impact")

                    st.warning(impact)

                # -----------------------------------
                # RECOMMENDED FIXES
                # -----------------------------------

                if fixes:

                    st.markdown("### ✅ Recommended Fix")

                    for line in fixes.split("\n"):
                        if line.strip():
                            st.write("✔️", line)

                # -----------------------------------
                # RAW OUTPUT (ENGINEER VIEW)
                # -----------------------------------

                with st.expander("Raw AI Output"):

                    st.code(analysis)

            else:

                st.error(result)