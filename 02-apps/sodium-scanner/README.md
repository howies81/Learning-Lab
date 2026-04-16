# 🛒 Caribbean Sodium Scanner (v1.0)
## Empowering Trinidad & Tobago to make heart-healthy grocery choices.

### 🌟 The Mission
Non-communicable diseases (NCDs) like hypertension are a major health challenge in the Caribbean. This tool is designed to help citizens instantly identify high-sodium products using their smartphone camera, cross-referencing local grocery data with PAHO (Pan American Health Organization) nutritional standards.

### 🛠️ Features
Live Barcode Detection: Real-time scanning using WebRTC and pyzbar.

Mobile Optimized: Specifically configured to use the rear-facing "environment" camera on smartphones.

Instant Feedback: Uses Streamlit's session state for a seamless "scan-and-see" experience.

Localized Data: (In Progress) A database tailored to products found in local groceries and supermarkets such as Massy, JTA, Xtra Foods and more.

### 🚀 Getting Started
#### 1. Prerequisites
You will need Python 3.9+ installed. You also need zbar shared libraries installed on your system.

#### 2. Installation
Clone this repository and install the required "gears":

Bash
git clone (coming soon)
cd sodium-scanner
pip install -r requirements.txt
#### 3. Running the App
Bash
streamlit run test.py
### 📂 Project Structure
test.py: The main user interface and logic controller.

web_app_barcode_scanner.py: The "Engine Room" containing the WebRTC processor and barcode logic.

/data: (Coming Soon) CSV files containing local product nutrition facts.

/assets: Branding and PAHO warning icons.

### ⚖️ Disclaimer
This app is an advocacy tool and does not provide medical advice. Always consult with a healthcare professional regarding dietary requirements.
