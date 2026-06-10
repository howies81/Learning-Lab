import streamlit as st
import time
import urllib.parse
from web_app_barcode_scanner import get_barcode_from_scanner
from ui_helper_functions import  display_sodium_results
from local_food_database import check_cloud_database, save_new_product_to_cloud
from global_food_database import check_global_database
from manual_input_form import show_manual_entry_form


st.set_page_config(page_title="Sodium Scanner T&T")

st.title("🛒 Sodium Scanner Tool")
st.write("Let's check the sodium content of your Caribbean groceries.")

# =====================================================================
# STAGE 1: SYSTEM STATE INITIALIZATION
# =====================================================================
# We use st.session_state like an internal control panel to remember
# exactly which screen the user is viewing and what data is being held.

# Initialize the memory bank if it doesn't exist
if "current_screen" not in st.session_state:
    st.session_state.current_screen = "SCANNING" # Valid views: SCANNING, PROCESS,
#                                                  PROMPT_CHOICE, MANUAL_FORM, SHOW_RESULTS
if "target_barcode" not in st.session_state:
    st.session_state.target_barcode = None
if "loaded_product_data" not in st.session_state:
    st.session_state.loaded_product_data = None
if "inputted_product_data" not in st.session_state:
    st.session_state.inputted_product_data = None
if "diagnostic_error_msg" not in st.session_state:
    st.session_state.diagnostic_error_msg = ""

@st.fragment(run_every=0.5)
def render_scanner_view():
    manual_container = st.container()
    camera_container = st.container()

    with manual_container:
        st.info("Do you prefer to enter the barcode manually?")

        with st.form("manual_barcode_form", clear_on_submit=True):
            manual_barcode = st.text_input("Barcode Input", max_chars=13, placeholder="0123456789101")
            submitted = st.form_submit_button("🔍 Search for Barcode", use_container_width=True)

            if submitted:
                cleaned_barcode = manual_barcode.strip()
                # Enforce valid barcode structures (most retail barcodes are between 8 and 13 digits)
                if cleaned_barcode.isnumeric() and (8 <= len(cleaned_barcode) <= 13):
                    st.session_state.target_barcode = cleaned_barcode
                    st.session_state.current_screen = "PROCESS"
                    st.rerun(scope="app") # Force global parent update to move to process screen
                else:
                    st.error("⚠️ Invalid barcode format. Please enter a valid 8 to 13 digit number.")

            
    with camera_container:
        st.write("---")
        if st.session_state.target_barcode is None:
            st.info("📷 Looking for a barcode... (Hold packaging steady!)")
            barcode_result = get_barcode_from_scanner()
            
            if barcode_result:
                st.session_state.target_barcode = str(barcode_result).strip()
                st.session_state.current_screen = "PROCESS"
                st.rerun(scope="app")
# =====================================================================
# STATE A: LIVE CAMERA SCANNING VIEW
# =====================================================================
if st.session_state.current_screen == "SCANNING":
    render_scanner_view()
    

        

# =====================================================================
# STATE B: CENTRALIZED DATA PROCESSING PIPELINE
# =====================================================================

elif st.session_state.current_screen == "PROCESS":
    #First we check the local database
    product_info = check_cloud_database(st.session_state.target_barcode)
    
    
    if product_info['status'] == "success": # 2. Check if we actually got a Dictionary (Success)
        st.session_state.loaded_product_data = product_info
        st.session_state.current_screen = "SHOW_RESULTS"
        st.rerun()

        #Call function to process sodium and calories data from local csv file. Then output
        #sodium and calorie facts of product, and display black octagonal warning label
        #if PAHO Nutrient Profile Model criteria for sodium is exceeded

    #If product not found in local database, or there is a problem connecting to the local database,
    # proceed to global database 
    elif product_info["status"] in ["not_found", "db_access_error", "db_conn_error",\
                                     "barcode_error", "cloud_conn_error"]:
        #Display information messages
        #If the database is accessed but the product is not found
        if product_info["status"] == "not_found":
            prod_not_found_locally = st.empty()
            global_db_open = st.empty()
            st.session_state.diagnostic_error_msg = "⚠️ Product not found locally."
            prod_not_found_locally.warning(st.session_state.diagnostic_error_msg)
            global_db_open.info("Proceeding to check the OpenFoodFacts global database...")
        
        #If the database is cannot be accessed
        elif product_info["status"] in ["db_access_error", "db_conn_error", "cloud_conn_error"]:
            #If there is a problem connecting to the local database, display UI message and
            # send an email to the system administrator
            
            prod_local_bad_conn = st.empty()
            global_db_open = st.empty()
            st.session_state.diagnostic_error_msg = "🛑 Cannot access local database. Contact the system administrator"
            prod_local_bad_conn.error(st.session_state.diagnostic_error_msg)

            # EMAIL SUPPORT INTEGRATION ADD-ON: 
            # Pre-builds an automatic email report link for the local connection error
            support_email = st.secrets["email"]["admin"]
            sub = urllib.parse.quote("ALERT: Local Database Access Failure")
            msg = urllib.parse.quote(f"System failed to check local database for barcode: {st.session_state.target_barcode}")
            st.markdown(f'<a href="mailto:{support_email}?subject={sub}&body={msg}">📧 Click here to report this database dropout to Admin</a>', unsafe_allow_html=True)

            global_db_open.info("Proceeding to check the OpenFoodFacts global database...")
        
        #If reading the barcode produced bad data, do this
        elif product_info["status"] == "barcode_error":
            prod_not_found_locally = st.empty()
            st.session_state.diagnostic_error_msg = "Error reading barcode. Scan or manually enter barcode again"
            prod_not_found_locally.error(st.session_state.diagnostic_error_msg)
            time.sleep(3)
            st.session_state.current_screen = "SCANNING"
            st.session_state.target_barcode = None
            st.session_state.loaded_product_data = None
            st.rerun()

        # Attempt to connect to global database
        with st.spinner("In progress..."):
            global_info = check_global_database(st.session_state.target_barcode)
        #If successful in connecting to global database, show UI message
        #and set session state variables
        if global_info["status"] == "success":
            st.success("Connected to global database")
            st.session_state.loaded_product_data = global_info
            save_new_product_to_cloud(st.session_state.loaded_product_data["data"])
            st.session_state.current_screen = "SHOW_RESULTS"
            st.rerun()

        #If API error encountered in connecting to global database, show UI error message
        #and set session state variables
        elif global_info["status"] == "api_error":
            st.session_state.diagnostic_error_msg = "Network connection timeout to global server"
            st.session_state.current_screen = "PROMPT_CHOICE"
            st.rerun()

        #If error encountered in parsing data from global database, show UI error message
        #and set session state variables
        elif global_info["status"] == "parse_error":
            st.session_state.diagnostic_error_msg = "Payload parsing corruption encountered"
            st.session_state.current_screen = "PROMPT_CHOICE"
            st.rerun()

        #Else if food item not found in global database, show UI error message
        #and set session state variables
        else:
            st.session_state.diagnostic_error_msg = "Product unregistered in global food database"
            st.session_state.current_screen = "PROMPT_CHOICE"
            st.rerun()
     
    

    # ==============================================================
    # PROMPTING USING CHOICE HERE
    #===============================================================

elif st.session_state.current_screen == "PROMPT_CHOICE":
    st.info(f"The nutritional information of the food item with barcode\
            {st.session_state.target_barcode} could not be found")
    if st.session_state.diagnostic_error_msg:
        st.error(st.session_state.diagnostic_error_msg)
    st.info(f"Do you want to input the nutritional data for\
             {st.session_state.target_barcode} into the database?")
    
    flex = st.container(horizontal=True, horizontal_alignment="right")
    if flex.button("Yes, I'll enter data"):
        st.session_state.current_screen = "MANUAL_FORM"
        st.rerun()
    if flex.button("No, return to scanner"):
        st.session_state.current_screen = "SCANNING"
        st.session_state.loaded_product_data = None
        st.session_state.target_barcode = None
        st.session_state.diagnostic_error_msg = ""
        st.rerun()

    # ==============================================================
    # DISPLAY MANUAL INPUT FORM HERE
    #===============================================================
elif st.session_state.current_screen == "MANUAL_FORM":
    # 1. Create a clean top layout with a modern flex container
    top_bar = st.container(horizontal=True)
    
    # Put the title on the left, and a "Cancel" button on the right
    with top_bar:
        st.title("📝 Data Contribution Panel")
        
        # This is the "Change Mind" eject handle!
        if st.button("❌ Cancel & Return", type="secondary", help="Click here to discard changes and scan another item"):
            st.session_state.current_screen = "SCANNING"
            st.session_state.target_barcode = None
            st.session_state.diagnostic_error_msg = ""
            st.rerun()

    show_manual_entry_form(st.session_state.target_barcode)
    
    
elif st.session_state.current_screen == "SHOW_RESULTS":
    display_sodium_results(st.session_state.loaded_product_data)
    if st.button("🛒 Scan Another Item", use_container_width=True, type="primary"):
        st.session_state.current_screen = "SCANNING"
        st.session_state.loaded_product_data = None
        st.session_state.target_barcode = None
        st.session_state.diagnostic_error_msg = ""
        st.rerun()

 
st.write("---")
col1, col2 = st.columns([4, 1]) # Pushes the button to the bottom right corner

with col2:
    if st.button("🔄 Reset App", help="Force clear memory and restart scanner"):
        st.session_state.current_screen = "SCANNING"
        st.session_state.loaded_product_data = None
        st.session_state.target_barcode = None
        st.session_state.diagnostic_error_msg = ""
        st.rerun()
        



