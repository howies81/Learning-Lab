import streamlit as st
from web_app_barcode_scanner import run_barcode_scanner

# This forces the app to refresh every 0.5 seconds to check for a scan
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=500, key="datarefresh")
# ---------------------

st.set_page_config(page_title="Sodium Scanner T&T")

st.title("🛒 Sodium Scanner Tool")
st.write("Let's check the sodium content of your Caribbean groceries.")

# 1. Initialize the memory bank if it doesn't exist
if "last_barcode" not in st.session_state:
    st.session_state.last_barcode = None

# Call the scanner function from the other file
barcode_result = run_barcode_scanner()

if barcode_result.video_processor:
    barcode_found = barcode_result.video_processor.found_barcode

    if barcode_found:
        st.session_state.last_barcode = barcode_found

if st.session_state.last_barcode:
    st.success(f"Captured Barcode: {st.session_state.last_barcode}")
    
        # NEXT STEP: 
        # check_csv_for_sodium(barcode_result)
    if st.button("Scan Another Item"):
        st.rerun()
else:
    st.info("Looking for a barcode... (Hold it steady!)")