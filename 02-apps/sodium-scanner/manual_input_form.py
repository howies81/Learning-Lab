import streamlit as st
from local_food_database import save_to_pending

def show_manual_entry_form(barcode):
    """
    Displays a Streamlit form for users to contribute missing data.
    """
    st.info(f"Barcode {barcode} not found. Help us by adding it to the database!")
    
    with st.form("add_product_form", clear_on_submit=True):
        brand = st.text_input("Brand Name")
        product_name = st.text_input("Product Name (e.g. Tomato Soup)")
        
        col1, col2 = st.columns(2)
        with col1:
            is_liquid = st.toggle("Is this a liquid?", value=False)
            sodium = st.number_input("Sodium (mg) per serving", min_value=0, step=1)
        with col2:
            calories = st.number_input("Calories per serving", min_value=0, step=1)
            serving_size = st.number_input("Serving Size of Food Item (g or mL)", min_value=1)
            container_size = st.number_input("Container Size of Food Item (g or mL)", min_value=1)
            sugars = st.number_input("Sugar content per serving of Food Item (g)", min_value=1)
            added_sugars = st.toggle("Is the sugar content added sugar?", value=False)
            fats = st.number_input("Fat content per serving of Food Item (g)", min_value=1)
            sat_fat = st.number_input("Saturated fat content per serving of Food Item (g)", min_value=1)
            trans_fat = st.number_input("Trans fat content per serving of Food Item (g)", min_value=1)

        submitted = st.form_submit_button("Submit Product")
        
        if submitted:
            if brand and product_name:
                # Map inputs to your 14 Google Sheet headers
                new_entry = {
                    "barcode": barcode,
                    "product_type": product_name,
                    "is_liquid": is_liquid,
                    "brand": brand,
                    "weight_g": container_size if not is_liquid else 0,
                    "amount_mL": container_size if is_liquid else 0,
                    "serving_weight_g": serving_size if not is_liquid else 0,
                    "serving_amt_mL": serving_size if is_liquid else 0,
                    #"product_type": "Liquid" if is_liquid else "Solid",
                    "sodium_mg": sodium,
                    "sugars_g": sugars, 
                    "added_sugars_g": sugars if added_sugars else 0, 
                    "fat_g": fats, 
                    "sat_fat_g": sat_fat, 
                    "trans_fat_g": trans_fat,
                    "calories": calories,
                    
                    # Fill remaining columns with defaults/zeros
                }
                save_to_pending(new_entry)
            else:
                st.error("Please provide both a Brand and Product Name so data can be verified.")