import streamlit as st
from web_app_barcode_scanner import get_barcode_from_scanner
from ui_helper_functions import handle_global_failure, display_sodium_results
from local_food_database import check_cloud_database, save_new_product_to_cloud
from streamlit_autorefresh import st_autorefresh
from global_food_database import check_global_database
#from sodium_reveal import calculate_paho_warnings
from manual_input_form import show_manual_entry_form


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
    product_info = check_cloud_database(st.session_state.last_barcode)
    
    
    if product_info['status'] == "success": # 2. Check if we actually got a Dictionary (Success)
        product = product_info['data']
        #Call function to process sodium and calories data from local csv file. Then output
        #sodium and calorie facts of product, and display black octagonal warning label
        #if PAHO Nutrient Profile Model criteria for sodium is exceeded

        check_local_db_success = st.empty()
        with check_local_db_success.container():
          #Call function to process sodiun and calories data
           display_sodium_results(product_info)

        # display warning label if necessary

        manual_input_choice = st.empty()
        with manual_input_choice.container():
            choice_question = f"""
            Is the information about this product correct?
            """
            st.markdown(choice_question)
            column_1, column_2 = st.columns(2)
            with column_1:
                if st.button("Yes", key="yes_choice"):
                    st.info("Thank You!")
                    #check_local_db_success.empty()
                    #Open manual input form
            with column_2:
                if st.button("No", key="no_choice"):
                    check_local_db_success.empty()
                    show_manual_entry_form(st.session_state.last_barcode)
        
    #If product was not found in local CSV database file"""

    elif product_info["status"] == "not_found":
        #Display information messages
        prod_not_found_locally = st.empty()
        global_db_open = st.empty()
        prod_not_found_locally.warning("⚠️ Product not found locally.")
        global_db_open.info("Proceeding to check the OpenFoodFacts global database...")

        # Attempt to connect to global database
        with st.spinner("Checking global database... this may take a moment"):
            global_info = check_global_database(st.session_state.last_barcode)

        #If successful in connecting to database AND finding product
        if global_info["status"] == "success":
            prod_not_found_locally.empty()
            global_db_open.empty()
            global_conn_success = st.empty()
            global_conn_success.success("Connected to global database")
            check_global_db_success = st.empty()
            with check_global_db_success.container():
                display_sodium_results(global_info)
                save_new_product_to_cloud(global_info["data"])

                
                #sodium and calorie facts of product, and display black octagonal warning label
                #if PAHO Nutrient Profile Model criteria for sodium is exceeded
                #info_display(global_info)

        # else if error occurred in attempt to connect to API
        elif global_info["status"] in ["api_error", "parse_error"]:
             #Placeholders for error messages
             handle_global_failure("An unexpected error occurred while connecting to\
                                    global database.", "api_error_not_found")
             
        
        #else if good connection to API but product could not be found in database
        else:
            handle_global_failure("Product not found in global database.", "not_found_not_found")
            
    
    #If Google Sheets file could NOT be found
    elif product_info["status"] in ["db_access_error", "db_conn_error", 
                                 "barcode_error", "cloud_conn_error"]:
        local_db_not_found = st.empty()
        global_db_open = st.empty()
        local_db_not_found.error("Local Database cannot be found.")
        global_db_open.info("Proceeding to check the OpenFoodFacts global database...")

        # Attempt to connect to global database
        global_info = check_global_database(st.session_state.last_barcode)

        #If successful in connecting to database AND finding product
        if global_info["status"] == "success":
            local_db_not_found.empty()
            global_db_open.empty()
            global_conn_success = st.empty()
            global_conn_success.success("Connected to global database")
            check_global_db_success = st.empty()
            with check_global_db_success.container():
                display_sodium_results(global_info)
                cloud_save_flag = save_new_product_to_cloud(global_info["data"])
                if cloud_save_flag is False:
                    cloud_failure_msg = st.error("Data from Open Food Facts database wasn't saved!")

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
            #barcode_result = None
            st.rerun(scope="app")
            
    
    

