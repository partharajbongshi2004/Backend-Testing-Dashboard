import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Clothing Store Backend QA Dashboard",
    page_icon="🧪",
    layout="wide",
)

# Resolve paths relative to this file so Streamlit Cloud never hits path issues
BASE_DIR = Path(__file__).resolve().parent
TEST_FILE = BASE_DIR / "test_backend.py"
BACKEND_FILE = BASE_DIR / "backend_app.py"


def run_pytest_suite(test_filter: str = "") -> dict:
    """
    Execute pytest in a subprocess using the active Python interpreter
    and parse structured JSON metrics + console output.
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_report:
        report_path = Path(tmp_report.name)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST_FILE),
        "-v",
        "--tb=short",
        "--json-report",
        f"--json-report-file={report_path}",
    ]

    if test_filter.strip():
        cmd.extend(["-k", test_filter.strip()])

    start_time = time.perf_counter()
    process = subprocess.run(
        cmd,
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
    )
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    report_data = {}
    if report_path.exists():
        try:
            report_data = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {}
        finally:
            report_path.unlink(missing_ok=True)

    summary = report_data.get("summary", {})
    tests_list = report_data.get("tests", [])

    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0) + summary.get("error", 0)

    # Build structured per-test dataframe rows
    structured_rows = []
    for t in tests_list:
        nodeid = t.get("nodeid", "")
        parts = nodeid.split("::")
        suite_name = parts[1] if len(parts) > 1 else "General"
        test_name = parts[-1] if parts else nodeid
        outcome = t.get("outcome", "unknown").upper()
        call_duration_ms = round(t.get("call", {}).get("duration", 0.0) * 1000, 3)

        structured_rows.append(
            {
                "Test Suite": suite_name,
                "Test Case": test_name,
                "Status": outcome,
                "Duration (ms)": call_duration_ms,
            }
        )

    raw_logs = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "execution_time_ms": elapsed_ms,
        "return_code": process.returncode,
        "rows": structured_rows,
        "raw_logs": raw_logs.strip(),
    }


# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🛠️ QA Control Panel")
    st.markdown("Configure and trigger automated backend tests.")

    suite_choice = st.selectbox(
        "Target Test Suite",
        options=[
            "All Backend Tests",
            "TestDiscountCalculation",
            "TestInventoryStatus",
            "TestUserCredentials",
            "TestOrderTotalIntegration",
        ],
    )

    keyword_filter = "" if suite_choice == "All Backend Tests" else suite_choice

    run_button = st.button("▶️ Run Pytest Suite", type="primary", use_container_width=True)

    st.divider()
    st.subheader("📁 Monitored Modules")
    st.code(f"• {BACKEND_FILE.name}\n• {TEST_FILE.name}", language="text")


# --- HEADER ---
st.title("🧪 Clothing Store Backend Testing Dashboard")
st.markdown(
    "Automated QA verification suite for **discount logic**, **inventory thresholds**, "
    "**user authentication**, and **taxed order calculations**."
)

# Auto-run on initial load or when button is clicked
if "test_results" not in st.session_state or run_button:
    with st.spinner("Running automated pytest suite..."):
        st.session_state["test_results"] = run_pytest_suite(keyword_filter)

results = st.session_state["test_results"]

# --- KPI METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tests", results["total"])
col2.metric("Passed", results["passed"], delta="OK" if results["passed"] > 0 else None)
col3.metric(
    "Failed",
    results["failed"],
    delta=f"-{results['failed']}" if results["failed"] > 0 else "0",
    delta_color="inverse",
)
col4.metric("Execution Time (ms)", f"{results['execution_time_ms']:.2f} ms")

if results["total"] > 0 and results["failed"] == 0:
    st.success(f"All {results['passed']} backend tests passed successfully!")
elif results["failed"] > 0:
    st.error(f"{results['failed']} test(s) failed. Inspect the execution logs below.")
else:
    st.warning("No tests matched the selected filter.")

st.divider()

# --- VISUAL SUMMARY & BREAKDOWN ---
if results["rows"]:
    df_results = pd.DataFrame(results["rows"])

    chart_col, table_col = st.columns([1, 1.4], gap="large")

    with chart_col:
        st.subheader("📊 Test Results by Suite")
        suite_summary = (
            df_results.groupby(["Test Suite", "Status"])
            .size()
            .unstack(fill_value=0)
        )
        st.bar_chart(suite_summary, use_container_width=True)

        st.subheader("⏱️ Latency per Suite (ms)")
        latency_summary = df_results.groupby("Test Suite")["Duration (ms)"].sum()
        st.bar_chart(latency_summary, use_container_width=True)

    with table_col:
        st.subheader("📋 Detailed Test Cases")
        st.dataframe(
            df_results,
            use_container_width=True,
            hide_index=True,
            height=460,
        )

# --- RAW EXECUTION LOGS & SOURCE VIEWER ---
st.divider()
tab_logs, tab_backend, tab_tests = st.tabs(
    ["🖥️ Pytest Execution Logs", "⚙️ backend_app.py", "🔬 test_backend.py"]
)

with tab_logs:
    st.code(results["raw_logs"], language="text")

with tab_backend:
    st.code(BACKEND_FILE.read_text(encoding="utf-8"), language="python")

with tab_tests:
    st.code(TEST_FILE.read_text(encoding="utf-8"), language="python")
