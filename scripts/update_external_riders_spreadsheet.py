import json
import os
import warnings

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
FORM_RESPONSE_SPREADSHEET_ID = "1TDq1ffECjsfuxY8ITAxhU8YCh3wY_Mim91b7qSh3DjM"
FORM_RESPONSE_RANGE_NAME = "Form Responses 1!A:AN"

LISTING_SPREADSHEET_ID = "1_eD1mIZovYdXcHHxpTpGu7VoZ4bON0EtPdX8RdvsuTo"
LISTING_SHEET_NAME = "Feuille 1"
URL_LISTING = (
    f"https://docs.google.com/spreadsheets/d/{LISTING_SPREADSHEET_ID}/gviz/"
    f"tq?tqx=out:csv&sheet={LISTING_SHEET_NAME}"
)


def update_external_riders_spreadsheet(service_account_info):
    """Update the external riders spreadsheet with new riders."""

    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=FORM_RESPONSE_SPREADSHEET_ID, range=FORM_RESPONSE_RANGE_NAME)
        .execute()
    ).get("values", [])

    headers = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))

    df_form_responses = pd.DataFrame(data, columns=headers)
    df_form_responses["Timestamp"] = pd.to_datetime(df_form_responses["Timestamp"])
    df_form_responses["Nom"] = df_form_responses["Nom"].str.strip().str.upper()
    df_form_responses["Prénom"] = (
        df_form_responses["Prénom"].str.strip().str.capitalize()
    )
    df_form_responses["Date de naissance"] = pd.to_datetime(
        df_form_responses.loc[:, "Date de naissance"], format="%m/%d/%Y"
    )

    column_comparison = ["Nom", "Prénom", "Date de naissance"]
    df_form_responses = df_form_responses.drop_duplicates(
        subset=column_comparison, keep="last"
    )

    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=LISTING_SPREADSHEET_ID, range=LISTING_SHEET_NAME)
        .execute()
    ).get("values", [])

    headers = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))

    df_licences = pd.DataFrame(data, columns=headers)
    df_licences["Nom"] = df_licences["Nom"].str.strip().str.upper()
    df_licences["Prénom"] = df_licences["Prénom"].str.strip().str.capitalize()
    df_licences["Date de naissance"] = pd.to_datetime(
        df_licences.loc[:, "Date de naissance"], format="%d/%m/%Y"
    )
    df_licences["Date d'inscription"] = pd.to_datetime(
        df_licences.loc[:, "Date d'inscription"], format="%d/%m/%Y"
    )

    # Find new riders that are not in the current listing
    df_new_riders = df_form_responses.merge(
        df_licences[column_comparison],
        on=column_comparison,
        how="left",
        indicator=True,
    )
    # Keep only the rows that are unique to df_form_responses
    df_new_riders = df_new_riders[df_new_riders["_merge"] == "left_only"].drop(
        columns=["_merge"]
    )

    if df_new_riders.empty:
        print("No new riders to add")
        return

    map_form_responses_to_licence = {
        "Nom": "Nom",
        "Prénom": "Prénom",
        "Date de naissance": "Date de naissance",
        "Club": "Club",
        "Département": "Département",
        "Numéro de licence FSGT": "Numéro de licence FSGT",
        "Catégorie FFC": "Catégorie FFC",
        "Catégorie UFOLEP": "Catégorie UFOLEP",
        "Catégorie FSGT": "Catégorie FSGT département d'origine",
    }

    df_new_licences = df_new_riders[map_form_responses_to_licence.keys()].rename(
        columns=map_form_responses_to_licence
    )

    df_new_licences = pd.concat([df_licences, df_new_licences], axis=0)
    # Convert datetime columns to string format before sending to Google Sheets
    df_new_licences["Date de naissance"] = df_new_licences[
        "Date de naissance"
    ].dt.strftime("%d/%m/%Y")
    df_new_licences["Date d'inscription"] = df_new_licences[
        "Date d'inscription"
    ].dt.strftime("%d/%m/%Y")

    # Replace "Aucune" values with empty strings in specific columns
    columns_to_clean = [
        "Catégorie FFC",
        "Catégorie UFOLEP",
        "Catégorie FSGT département d'origine",
    ]
    for col in columns_to_clean:
        df_new_licences[col] = df_new_licences[col].apply(
            lambda x: "" if isinstance(x, str) and x.startswith("Aucune") else x
        )

    # Replace NaN values with empty strings
    df_new_licences = df_new_licences.fillna("")

    # Convert dataframe to values list for Google Sheets
    values = [df_new_licences.columns.tolist()] + df_new_licences.values.tolist()

    # Update the entire sheet with new values
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=LISTING_SPREADSHEET_ID,
            range=LISTING_SHEET_NAME,
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )

    print(f"Updated {result.get('updatedCells')} cells")


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
        update_external_riders_spreadsheet(service_account_info)
