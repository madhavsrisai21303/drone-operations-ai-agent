import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Google API scopes
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Name of your Google Sheet (must match exactly)
SPREADSHEET_NAME = "Skylark_Drone_Operations"

# Credentials file (local development)
CREDS_FILE = "credentials.json"


def connect_sheet():
    """
    Connect to Google Sheets using service account credentials.
    """
    creds = Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME)
    return sheet


def load_data():
    """
    Load data from Google Sheets into pandas DataFrames.
    """
    sheet = connect_sheet()

    pilots_ws = sheet.worksheet("Pilot_Roster")
    drones_ws = sheet.worksheet("Drone_Fleet")
    missions_ws = sheet.worksheet("Missions")

    pilots = pd.DataFrame(pilots_ws.get_all_records())
    drones = pd.DataFrame(drones_ws.get_all_records())
    missions = pd.DataFrame(missions_ws.get_all_records())

    return pilots, drones, missions


def update_pilots(pilots_df):
    """
    Overwrite Pilot_Roster sheet with updated data.
    """
    sheet = connect_sheet()
    ws = sheet.worksheet("Pilot_Roster")

    ws.clear()
    ws.update(
        [pilots_df.columns.values.tolist()] +
        pilots_df.values.tolist()
    )


def update_missions(missions_df):
    """
    Overwrite Missions sheet with updated data.
    """
    sheet = connect_sheet()
    ws = sheet.worksheet("Missions")

    ws.clear()
    ws.update(
        [missions_df.columns.values.tolist()] +
        missions_df.values.tolist()
    )
