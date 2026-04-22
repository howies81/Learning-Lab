import streamlit as st
from web_app_barcode_scanner import get_barcode_from_scanner
from ui_helper_functions import handle_global_failure
from local_food_database import check_local_database
from streamlit_autorefresh import st_autorefresh
from global_food_database import check_global_database


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
    #First we check the local database
    product_info = check_local_database(st.session_state.last_barcode)
    
    
    if product_info['status'] == "success": # 2. Check if we actually got a Dictionary (Success)
        product = product_info['data']
        #Call function to process sodium and calories data from local csv file. Then output
        #sodium and calorie facts of product, and display black octagonal warning label
        #if PAHO Nutrient Profile Model criteria for sodium is exceeded

        text_display = f"""
        ### {product['barcode']}
        **Category:** {product['product_type']}
        **Brand:** {product['brand']}

        ---
        #### 📊 Nutritional Profile
        **Sodium:** {product['sodium_mg']}mg
        **Calories:** {product['calories']}kcal
        ---
        """
        st.markdown(text_display)

    #If product was not found in local CSV database file
    elif product_info["status"] == "not_found":
        #Display information messages
        prod_not_found_locally = st.empty()
        global_db_open = st.empty()
        prod_not_found_locally.warning("⚠️ Product not found locally.")
        global_db_open.info("Proceeding to check the OpenFoodFacts global database...")

        # Attempt to connect to global database
        global_info = check_global_database(st.session_state.last_barcode)

        #If successful in connecting to database AND finding product
        if global_info["status"] == "success":
            global_conn_success = st.empty()
            global_conn_success.success("Connected to global database")
            #Call function to process sodium and calories data from global database,
            #OPEN csv file, input data from global database into csv file, then output
            #sodium and calorie facts of product, and display black octagonal warning label
            #if PAHO Nutrient Profile Model criteria for sodium is exceeded

        # else if error occurred in attempt to connect to API
        elif global_info["status"] in ["api_error", "parse_error"]:
             #Placeholders for error messages
             handle_global_failure("An unexpected error occurred while connecting to\
                                    global database.", "api_error_not_found")
             
        
        #else if good connection to API but product could not be found in database
        else:
            handle_global_failure("Product not found in global database.", "not_found_not_found")
            
    
    #If local CSV file could NOT be found
    elif product_info["status"] == "file_error":
        local_db_not_found = st.empty()
        global_db_open = st.empty()
        local_db_not_found.error("Local Database cannot be found. Contact the system administrator")
        global_db_open.info("Proceeding to check the OpenFoodFacts global database...")

        # Attempt to connect to global database
        global_info = check_global_database(st.session_state.last_barcode)

        #If successful in connecting to database AND finding product
        if global_info["status"] == "success":
            global_conn_success = st.empty()
            global_conn_success.success("Connected to global database")
            #Call function to process sodium and calories data from global database,
            #CREATE csv file, input data from global database into csv file, then output
            #sodium and calorie facts of product, and display black octagonal warning label
            #if PAHO Nutrient Profile Model criteria for sodium is exceeded

        # else if error occurred in attempt to connect to API
        elif global_info["status"] in ["api_error", "parse_error"]:
             #Placeholders for error messages
             handle_global_failure("An unexpected error occurred while connecting to\
                                    global database.", "api_error_file_error")
             
        
        #else if good connection to API but product could not be found in database
        else:
            handle_global_failure("Product not found in global database.", "not_found_file_error")
            

    if st.button("Scan Another Item"):
            st.session_state.last_barcode = None
            barcode_result = None
            st.rerun()
            
    
    

