from __future__ import annotations

import io
import os
import sys
import tempfile
from datetime import datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on sys.path so `src` imports work when run via Streamlit
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.orchestrator import process_file  # noqa: E402

# Load .env to populate Azure OpenAI settings for LLM calls
load_dotenv()

st.set_page_config(page_title="SSA Comment Reviewer", layout="wide")
# Left-aligned top title above all other content
st.markdown("""
<h1 style="margin-top: 0;">SSA Comment Reviewer</h1>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    - Upload an Excel file with a comment text column.
    - Click Run to process redactions and themes.
    - When done, click Open to view the output Excel.
    """)

# Inputs
uploaded = st.file_uploader("Select input Excel (.xlsx)", type=["xlsx"], accept_multiple_files=False)
text_column = st.text_input("Enter comment text column name here:", value="comment")
processes_val = st.number_input("[Technical] Worker processes (0 = auto)", min_value=0, max_value=64, value=0, step=1)

# Default output path inside project data/ directory
default_output_dir = os.path.join(PROJECT_ROOT, "data")
os.makedirs(default_output_dir, exist_ok=True)

def _suggest_output_name(name: str) -> str:
    base, ext = os.path.splitext(name)
    if not ext:
        ext = ".xlsx"
    return f"{base}_processed{ext}"

if uploaded is not None:
    suggested = _suggest_output_name(uploaded.name)
else:
    suggested = "comment_processing_results.xlsx"

output_dir = st.text_input(
    "Output directory", value=default_output_dir, help="Directory where the results .xlsx will be written"
)
proposed_output_path = os.path.join(output_dir or default_output_dir, suggested)
st.caption(f"Will save as: {proposed_output_path}")

run_clicked = st.button("Run")

# Keep state of last output path to show Open button
if "last_output_path" not in st.session_state:
    st.session_state["last_output_path"] = None

if run_clicked:
    if uploaded is None:
        st.error("Please upload an input Excel file.")
    else:
        # Write uploaded file to a temp path on disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_input_path = tmp.name

        st.info("Processing... this may take a few minutes depending on file size.")
        try:
            # Ensure output directory exists
            target_dir = output_dir or default_output_dir
            os.makedirs(target_dir, exist_ok=True)
            processes: Optional[int] = None if processes_val == 0 else int(processes_val)
            n, out_path = process_file(
                input_path=tmp_input_path,
                output_path=os.path.join(target_dir, suggested),
                text_column=text_column,
                processes=processes,
            )
            st.success(f"Processed {n} rows -> {out_path}")
            st.session_state["last_output_path"] = out_path
        except Exception as e:
            st.exception(e)
        finally:
            try:
                os.remove(tmp_input_path)
            except Exception:
                pass

# Show Open button if the output exists
out_path = st.session_state.get("last_output_path") or proposed_output_path
if out_path and os.path.exists(out_path):
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Open output file"):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(out_path)  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    os.system(f"open '{out_path}'")
                else:
                    os.system(f"xdg-open '{out_path}'")
            except Exception as e:
                st.error(f"Failed to open file: {e}")
    with col2:
        st.caption(f"Last updated: {datetime.fromtimestamp(os.path.getmtime(out_path)).strftime('%Y-%m-%d %H:%M:%S')}")
