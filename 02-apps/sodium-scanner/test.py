import streamlit as st
from web_app_barcode_scanner import get_barcode_from_scanner
from local_food_database import check_local_database

# This forces the app to refresh every 0.5 seconds to check for a scan
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=500, key="datarefresh")
# ---------------------

st.set_page_config(page_title="Sodium Scanner T&T")

st.title("🛒 Sodium Scanner Tool")
st.write("Let's check the sodium content of your Caribbean groceries.")

# Initialize the memory bank if it doesn't exist
if "last_barcode" not in st.session_state:
    st.session_state.last_barcode = None

# Determine if the scanner should be active
# If we have a barcode, we 'pause' the scanner logic
scanner_active = st.session_state.last_barcode is None

# Call the scanner function from the web app scanner file
# once scanner should be active
if scanner_active:
    barcode_result = get_barcode_from_scanner()
     

    # Check to see if a barcode has been found
    if barcode_result:
        # Store result in last_barcode child of Streamlit library
        st.session_state.last_barcode = barcode_result
        st.rerun()

else:
    if st.session_state.last_barcode:
        st.success(f"Captured Barcode: {st.session_state.last_barcode}")
        # NEXT STEP: check if csv is available. 
        # If so, check csv for sodium content according to barcode
        check_local_database(st.session_state.last_barcode)


        if st.button("Scan Another Item"):
            st.session_state.last_barcode = None
            barcode_result = None
            st.rerun()
            
    
    else:
        st.info("Looking for a barcode... (Hold it steady!)")

