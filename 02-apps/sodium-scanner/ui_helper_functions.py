import streamlit as st

def handle_global_failure(error_message, button_key_suffix):
    error_placeholder = st.empty()
    choice_placeholder = st.empty()
    error_placeholder.error(error_message)
    choice_placeholder.error("Product could not be identified.\
                              Do you want to manually enter nutritional data?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes", key=f"yes_{button_key_suffix}"):
            error_placeholder.empty()
            choice_placeholder.empty()
            # Open manual entry form
    with col2:
        if st.button("No", key=f"no_{button_key_suffix}"):
            error_placeholder.empty()
            choice_placeholder.empty()