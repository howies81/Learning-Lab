import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)  # refresh cache every 5 minutes
def load_food_data():
    return pd.read_csv("food_item_nutrition_facts.csv", dtype={"barcode": str})

def check_local_database(barcode):
    try:
        food_df = load_food_data() # Force barcodes to stay as Text
        food_item = food_df[food_df['barcode'] == str(barcode)]
        
        if not food_item.empty:
            return {"status": "success", "data": food_item.iloc[0].to_dict()}
        else:
            return {"status": "not_found", "data": None}
            
    except FileNotFoundError:
        return {"status": "file_error", "data": None}