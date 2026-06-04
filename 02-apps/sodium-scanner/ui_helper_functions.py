import streamlit as st
from sodium_reveal import calculate_paho_warnings
from manual_input_form import show_manual_entry_form

def handle_global_failure(error_message, button_key_suffix):
    error_placeholder = st.empty()
    choice_placeholder = st.empty()
    button_placeholder = st.empty()

    error_placeholder.error(error_message)
    choice_placeholder.error("Product could not be identified.\
                              Do you want to manually enter nutritional data?")
    
    with button_placeholder.container():
        col1, col2, col3 = st.columns([4,1,1])
        with col2:
            if st.button("Yes", key=f"yes_{button_key_suffix}"):
                error_placeholder.empty()
                choice_placeholder.empty()
                # Open manual entry form
                show_manual_entry_form(st.session_state.last_barcode)
        with col3:
            if st.button("No", key=f"no_{button_key_suffix}"):
                error_placeholder.empty()
                choice_placeholder.empty()

def display_sodium_results(item):
    data = item["data"]
    PAHO_warning = calculate_paho_warnings(data)

    #Check Google Sheets API connection from Google Drive account
    
    #  input data from global database into csv file in Google Drive, then output
    # save_new_product_to_cloud(global_info)

    if "INSUFFICIENT DATA" in PAHO_warning:
        st.markdown("""
        <div style="
            background-color: red;
            color: white;
            width: 150px;
            height: 150px;
            clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-family: Arial;
            font-size: 16px;
            text-align: center;
            margin: auto;">
            INSUFFICIENT<br>DATA!
        </div>
        """, unsafe_allow_html=True)
    
        
        choice_question = f"""
        Are you willing to input any available nutrition data for this product?
        """
        change_data_choice(choice_question)

    elif "HIGH IN SODIUM" in PAHO_warning:
        # Custom CSS for the "Black Octagon" look (simulated with black error box)
        st.markdown("""
        <div style="
            background-color: black;
            color: white;
            width: 150px;
            height: 150px;
            clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-family: Arial;
            font-size: 16px;
            text-align: center;
            margin: auto;">
            HIGH IN<br>SODIUM
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background-color: rgb(0, 255, 155);
            color: white;
            width: 150px;
            height: 150px;
            clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-family: Arial;
            font-size: 16px;
            text-align: center;
            margin: auto;">
            ✅<br>SODIUM OK
        </div>
        """, unsafe_allow_html=True)
    cols = st.columns(2)
    cols[0].metric("Sodium", f"{data.get('sodium_mg', 'N/A')} mg")
    cols[1].metric("Calories", f"{data.get('calories', 'N/A')} kcal")

#@st.dialog("Input Nutrition Data?")
def change_data_choice(question):
    st.markdown(question)
    col_1, col_2, col_3 = st.columns([3, 1, 1])
    with col_2.container():
        if st.button("Yes, input data", help="Click this button to input data in form"):
            st.session_state.current_screen = "MANUAL_FORM"
            st.rerun()
    with col_3.container():
        if st.button("No, leave alone", help="Leave as is"):
            st.info("Thank you!")
        


