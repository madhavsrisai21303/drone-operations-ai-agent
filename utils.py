import os
import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd

# Google API scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Your Google Sheet name
SPREADSHEET_NAME = "Skylark_Drone_Operations"

def get_credentials():
    """
    Dual-mode credentials loader:
    - If GOOGLE_CREDENTIALS environment variable exists → use it (Render)
    - Else → use local credentials.json file
    """
    if "GOOGLE_CREDENTIALS" in os.environ:
        creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
    else:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
    return creds

def connect_sheet():
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME)
    return sheet

def load_data():
    sheet = connect_sheet()

    pilots_ws = sheet.worksheet("Pilot_Roster")
    drones_ws = sheet.worksheet("Drone_Fleet")
    missions_ws = sheet.worksheet("Missions")

    pilots = pd.DataFrame(pilots_ws.get_all_records())
    drones = pd.DataFrame(drones_ws.get_all_records())
    missions = pd.DataFrame(missions_ws.get_all_records())

    return pilots, drones, missions

def update_pilots(pilots_df):
    sheet = connect_sheet()
    ws = sheet.worksheet("Pilot_Roster")
    ws.clear()
    ws.update([pilots_df.columns.values.tolist()] + pilots_df.values.tolist())

def update_missions(missions_df):
    sheet = connect_sheet()
    ws = sheet.worksheet("Missions")
    ws.clear()
    ws.update([missions_df.columns.values.tolist()] + missions_df.values.tolist())
