import streamlit as st
import pandas as pd
from sodium_reveal import calculate_paho_warnings
from manual_input_form import show_manual_entry_form

def handle_global_failure(error_message, button_key_suffix):
    error_placeholder = st.empty()
    choice_placeholder = st.empty()
    button_placeholer = st.empty()

    error_placeholder.error(error_message)
    choice_placeholder.error("Product could not be identified.\
                              Do you want to manually enter nutritional data?")
    
    with button_placeholer.container():
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

def info_display(product):
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

def display_nutrition_results(item):
    st.divider()
    st.subheader(f"📊 {item.get('brand', 'Unknown Brand')} - {item.get('product_type', 'Product')}")
    
    # Calculate warnings
    warnings = calculate_paho_warnings(item)
    
    if warnings:
        st.markdown("### ⚠️ HEALTH WARNINGS (PAHO Model)")
        # Display warnings as high-visibility alerts
        for w in warnings:
            st.error(f"**{w}**")
    else:
        st.success("✅ This product meets PAHO nutrient profile targets.")

    # Display Facts in a clean table/columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Calories", f"{item['calories']} kcal")
    col2.metric("Sodium", f"{item['sodium_mg']} mg")
    #col3.metric("Sugars", f"{item.get('sugars_g', 0)} g")
    
    with st.expander("See Full Nutrition Label"):
        st.table(pd.DataFrame([item]).T.rename(columns={0: "Value"}))

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
        INSUFFICIENT DATA
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
    elif "HIGH IN SODIUM" in PAHO_warning:
        # Custom CSS for the "Black Octagon" look (simulated with black error box)
        warning_display = st.markdown(f"""
        <div style="background-color:black; color:white; padding:10px; 
                border-radius:5px; text-align:center; font-weight:bold; 
                margin-bottom:10px; border: 2px solid white;">
        HIGH IN SODIUM
        </div>
        """, unsafe_allow_html=True)
    else:
        safe_display = st.markdown(f"""
        <div style="background-color:green; color:white; padding:10px; 
                border-radius:5px; text-align:center; font-weight:bold; 
                margin-bottom:10px; border: 2px solid white;">
        LOW IN SODIUM
        </div>
        """, unsafe_allow_html=True)
    cols = st.columns(2)
    cols[0].metric("Sodium", f"{data.get('sodium_mg', 'N/A')} mg")
    cols[1].metric("Calories", f"{data.get('calories', 'N/A')} kcal")