import streamlit as st
from web_app_barcode_scanner import get_barcode_from_scanner
from lookup_manager import fetch_product_data

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

# --- FRAGMENT AREA: Only this part refreshes every 500ms ---
@st.fragment
def scanner_section():
    if st.session_state.last_barcode is None:
        st_autorefresh(interval=500, key="scanner_refresh")
        st.info("Looking for a barcode... (Hold it steady!)")
        barcode_result = get_barcode_from_scanner()
        
        if barcode_result:
            st.session_state.last_barcode = barcode_result
            st.rerun()

# Call the fragmented scanner
scanner_section()

if st.session_state.last_barcode:
    product_info = fetch_product_data(st.session_state.last_barcode)
    
    
    if isinstance(product_info, dict): # 2. Check if we actually got a Dictionary (Success)
        text_display = f"""
        ### {product_info['barcode']}
        **Category:** {product_info['product_type']}
        **Brand:** {product_info['brand']}

        ---
        #### 📊 Nutritional Profile
        **Sodium:** {product_info['sodium_mg']}mg
        **Calories:** {product_info['calories']}kcal
        ---
        """
        st.markdown(text_display)
    elif product_info == "ITEM NOT FOUND IN DATABASE!":
        st.warning("⚠️ Product not found locally.")
        st.info("Proceeding to check the OpenFoodFacts global database...")
        # This triggers if BOTH local and global fail
        st.error("Product could not be identified.")

    elif product_info == "FILE CANNOT BE FOUND!":
        st.error("Local Database cannot be found. Contact the system administrator")

    if st.button("Scan Another Item"):
            st.session_state.last_barcode = None
            barcode_result = None
            st.rerun()
            
    
    

