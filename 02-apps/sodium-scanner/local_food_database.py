import pandas as pd
import streamlit as st
import datetime
from streamlit_gsheets import GSheetsConnection

""" @st.cache_data(ttl=300)  # refresh cache every 5 minutes
def load_food_data():
    return pd.read_csv("food_item_nutrition_facts.csv", dtype={"barcode": str}) """

conn = st.connection("gsheets", type=GSheetsConnection)

def check_cloud_database(barcode):
    
        

    """Searches the Google Sheet for a barcode."""
    try:
        df = conn.read(ttl="5m", dtype={"barcode": str})
        # Convert barcode to string and strip spaces to ensure a match
        barcode_str = "BC-" + str(barcode).replace("BC-", "").strip().upper()
        #print(df['barcode'])

        # 3. Aggressively clean the DataFrame column temporarily for matching
        # This converts to string, strips hidden spaces, and forces uppercase
        df_cleaned_barcodes = df['barcode'].astype(str).str.strip().str.upper()

        #df['barcode'] = df['barcode'].astype(str).str.strip()
        #result = df[df['barcode'] == barcode_str] # .astype(str).str.replace("'", "", regex=False)
        
        # 4. Perform the match against the cleaned column
        result = df[df_cleaned_barcodes == barcode_str]

        if not result.empty:
            # Return the first match as a dictionary
            #print("Full")
            return {"status": "success", "data": result.iloc[0].to_dict()}
        #print("Empty")
        return {"status": "not_found", "data": None}
    
    except Exception as e:
        error_msg = str(e)
        
        # Log the error for the developer to see in the terminal
        print(f"Cloud Logic Error: {error_msg}")
        
        # Provide helpful UI feedback based on the error type
        if "403" in error_msg:
            #st.error("Database Access Denied: Check Service Account Permissions.")
            return {"status": "db_access_error", "data": None}
        elif "HTTPSConnectionPool" in error_msg or "Timeout" in error_msg:
           # st.warning("Connection Issues: The app is having trouble reaching Google.")
           return {"status": "db_conn_error", "data": None}
        elif "barcode" in error_msg:
            #st.error("Sheet Error: The 'barcode' column was not found.")
            return {"status": "barcode_error", "data": None}
        else:
            # General catch-all for anything else
            #st.error(f"Cloud Connection Error: {error_msg}")
            return {"status": "cloud_conn_error", "data": None}
    


def save_new_product_to_cloud(new_data):
    """
    Appends a new product row to the Google Sheet.
    """
    try:
        # 1. Fetch current data (without cache to avoid overwriting)
        existing_df = conn.read()

          # --- NEW DUPLICATE CHECK START ---
        # Normalize the incoming barcode and existing barcodes for a fair comparison
        incoming_barcode = "BC-" + str(new_data['barcode']).strip()

        if not existing_df.empty:
            existing_barcodes = existing_df['barcode'].astype(str).str.strip().tolist()
            if incoming_barcode in existing_barcodes:
                return True
            # --- NEW DUPLICATE CHECK END ---
            
        
        # 2. Add the ' quote to barcode for safe Sheet storage
        # if not str(new_data['barcode']).startswith("'"):
            #new_data['barcode'] = f"'{new_data['barcode']}" 
            
        # 3. Create DataFrame and Append, adding metadata in the last 3 columns
        new_data['barcode'] = incoming_barcode
        new_row = pd.DataFrame([new_data])
        #new_row['barcode'] = new_row['barcode'].astype(str).apply(lambda x: "BC-" + x.strip())
        new_row['data_source'] = 'Open Food Facts API'
        new_row['verified_by'] = 'System_Auto'
        new_row['verification_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)

        # 2. Fill the empty 'NaN' spots for the old rows
        # This ensures your 'verified_by' column stays consistent
        updated_df['verified_by'] = updated_df['verified_by'].fillna('Legacy_Entry')
        updated_df['data_source'] = updated_df['data_source'].fillna('Manual_Batch_1')
        updated_df['verification_date'] = updated_df['verification_date'].fillna('2026-01-01 00:00:00')
        
        # Safety check before writing
        if updated_df.empty or len(updated_df.columns) == 0:
            print("Safety check failed: DataFrame is empty, aborting update")
            return False

        # 4. Update the Sheet
        conn.update(data=updated_df)
        
        # 5. Clear cache so the search finds it immediately next time
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False

def save_to_pending(new_data):
    """
    Appends a product row to the 'Pending' sheet for manual review.
    """
    try:
        existing_df = conn.read(worksheet="Pending")
        
        """ if not str(new_data['barcode']).startswith("'"):
            new_data['barcode'] = f"'{new_data['barcode']}" """
        #print(new_data['barcode'])
        new_data['barcode'] = str(new_data['barcode']).strip()
        new_row = pd.DataFrame([new_data])
        #new_row['barcode'] = new_row['barcode'].astype(str).apply(lambda x: "BC-" + x.strip())
        #print(new_row['barcode'])
        new_row['data_source'] = 'Crowdsourced'
        new_row['verified_by'] = 'To_be_verified'
        new_row['verification_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        
        # Safety check before writing
        if updated_df.empty or len(updated_df.columns) == 0:
            print("Safety check failed: DataFrame is empty, aborting update")
            return False


        conn.update(worksheet="Pending", data=updated_df)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Pending sheet update error: {e}")
        return False