# %%
import json
import os
import warnings

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1lZwxoMeF2gBuFLgjoaBREPl8YFESYwJLV5o1JEjKHKI"
RANGE_NAME = "Form Responses 1!A:N"


def _get_values(service):
    """Get the values from the Google Sheet.

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        Google Sheets API service.

    Returns
    -------
    list[list[str]]
        The values from the Google Sheet.
    """
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    return result.get("values", [])


def generate_listing(filename, service_account_info):
    """Generate a XLSX listing of double license declarations from the last week.

    Parameters
    ----------
    filename : str
        Path where the XLSX file will be saved.
    service_account_info : dict
        Google service account credentials information.

    Notes
    -----
    This function connects to a Google Sheet containing double license declarations,
    downloads all entries, and filters for only those submitted in the last 7 days.
    The filtered data is saved to a XLSX file and also returned as a DataFrame.
    """
    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    values = _get_values(service)
    if not values:
        return

    headers = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(headers):
            row.append("")

    df = pd.DataFrame(data, columns=headers)
    for col in ("Date de naissance", "Timestamp"):
        df[col] = pd.to_datetime(df[col])

    one_day_ago = pd.Timestamp.now() - pd.Timedelta(days=1)
    df_last_day = df[df["Timestamp"] >= one_day_ago]
    if not df_last_day.empty:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df_last_day.to_excel(filename, index=False)


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
            "scratch/update_double_licences_declaration.xlsx", service_account_info
        )
