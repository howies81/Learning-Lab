import pandas as pd
import streamlit as st

def check_local_database(barcode):
    try:
        food_df = pd.read_csv("food_items.csv", dtype={"barcode": str}) # Force barcodes to stay as Text
        food_item = food_df[food_df['barcode'] == str(barcode)]
        
        if not food_item.empty:
            return food_item.iloc[0].to_dict()
        return None
    except FileNotFoundError:
        st.warning("Food Item database cannot be found!")
        return None