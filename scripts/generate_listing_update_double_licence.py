# %%
import json
import os
import warnings

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1lZwxoMeF2gBuFLgjoaBREPl8YFESYwJLV5o1JEjKHKI"
RANGE_NAME = "Form Responses 1!A:M"


def generate_listing(filename, service_account_info):
    """Generate a CSV listing of double license declarations from the last week.

    Parameters
    ----------
    filename : str
        Path where the CSV file will be saved.
    service_account_info : dict
        Google service account credentials information.

    Notes
    -----
    This function connects to a Google Sheet containing double license declarations,
    downloads all entries, and filters for only those submitted in the last 7 days.
    The filtered data is saved to a CSV file and also returned as a DataFrame.
    """
    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    headers = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(headers):
            row.append("")

    df = pd.DataFrame(data, columns=headers)
    for col in ("Date de naissance", "Timestamp"):
        df[col] = pd.to_datetime(df[col])

    one_week_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
    df_last_week = df[df["Timestamp"] >= one_week_ago]
    if not df_last_week.empty:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df_last_week.to_csv(filename, index=False)


class MissingServiceAccount(Warning):
    pass


if __name__ == "__main__":
    """Entry point for the pixi task."""
    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
    if not service_account_json:
        # raise a warning to avoid a failure when building locally the website and not
        # having the credentials.
        warnings.warn(
            "GOOGLE_SERVICE_ACCOUNT environment variable not found.",
            MissingServiceAccount,
        )
    else:
        service_account_info = json.loads(service_account_json)
        generate_listing(
            "scratch/update_double_licences_declaration.csv", service_account_info
        )