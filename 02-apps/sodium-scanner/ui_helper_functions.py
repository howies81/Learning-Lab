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
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", key=f"yes_{button_key_suffix}"):
                error_placeholder.empty()
                choice_placeholder.empty()
                # Open manual entry form
                show_manual_entry_form(st.session_state.last_barcode)
        with col2:
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
        no_data_display = st.markdown(f"""
    <div style="background-color:red; color:white; padding:10px; 
                border-radius:5px; text-align:center; font-weight:bold; 
                margin-bottom:10px; border: 2px solid white;">
        INSUFFICIENT <br> 
        DATA
    </div>
    """, unsafe_allow_html=True)
        
        choice_question = f"""
        Are you willing to input any available nutrition data for this product?
        """
        choice_question_blk = st.markdown(choice_question)
        column_1, column_2 = st.columns(2)
        with column_1:
            if st.button("Yes", key="yes_choice"):
                choice_question_blk.empty()
                show_manual_entry_form(st.session_state.last_barcode)
                #show_manual_entry_form(barcode)
        with column_2:
            if st.button("No", key="no_choice"):
                choice_question_blk.empty()
    elif "HIGH IN SODIUM" in PAHO_warning:
        # Custom CSS for the "Black Octagon" look (simulated with black error box)
        warning_display = st.markdown(f"""
        <div style="background-color:black; color:white; padding:10px; 
                border-radius:5px; text-align:center; font-weight:bold; 
                margin-bottom:10px; border: 2px solid white;">
        HIGH IN <br>
        SODIUM
        </div>
        """, unsafe_allow_html=True)
    else:
        safe_display = st.markdown(f"""
        <div style="background-color:green; color:white; padding:10px; 
                border-radius:5px; text-align:center; font-weight:bold; 
                margin-bottom:10px; border: 2px solid white;">
        ✅ <br> SODIUM OK
        </div>
        """, unsafe_allow_html=True)
    cols = st.columns(2)
    cols[0].metric("Sodium", f"{data.get('sodium_mg', 'N/A')} mg")
    cols[1].metric("Calories", f"{data.get('calories', 'N/A')} kcal")