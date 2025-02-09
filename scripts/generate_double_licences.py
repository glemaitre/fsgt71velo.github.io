import io
import json
import os
import warnings

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]
SHEET_ID = "19C5tMDiFtOLSEmzPYmt6v91yJC4NejoE"
SHEET_NAME = "Feuil1"


def generate_html_table(df_licences):
    """Generate the HTML table for the double licences.

    Parameters
    ----------
    df_licences : pd.DataFrame
        The dataframe containing the double licences data.

    Returns
    -------
    str
        The HTML table for the double licences.
    """
    html_table = (
        '<table class="table" id="doubleLicencesTable"><thead>'
        "<tr>"
        '<th rowspan="2" class="align-middle text-center">Nom</th>'
        '<th rowspan="2" class="align-middle text-center">Prénom</th>'
        '<th colspan="2" class="text-center border-bottom-group">Club</th>'
        '<th colspan="2" class="text-center border-bottom-group">Numéro</th>'
        '<th colspan="3" class="text-center border-bottom-group">Catégorie</th>'
        "</tr>"
        "<tr>"
        '<th class="text-center">FSGT</th>'
        '<th class="text-center">FFC</th>'
        '<th class="text-center">FSGT</th>'
        '<th class="text-center">FFC</th>'
        '<th class="text-center">FSGT (valeur)</th>'
        '<th class="text-center">FSGT (âge)</th>'
        '<th class="text-center">FFC</th>'
        "</tr>"
        "</thead><tbody>"
    )
    for _, row in df_licences.iterrows():
        html_table += "<tr>"
        html_table += f"<td class='text-center'>{row['Nom'].upper()}</td>"
        html_table += f"<td class='text-center'>{row['Prénom'].capitalize()}</td>"
        html_table += f"<td class='text-center'>{row['Club FSGT']}</td>"
        html_table += f"<td class='text-center'>{row['Club FFC']}</td>"
        if pd.notna(row["Numéro de licence FSGT"]):
            html_table += (
                f"<td class='text-center'>{int(row['Numéro de licence FSGT'])}</td>"
            )
        else:
            html_table += f"<td class='text-center'></td>"
        if pd.notna(row["Numéro de licence FFC"]):
            html_table += (
                f"<td class='text-center'>{int(row['Numéro de licence FFC'])}</td>"
            )
        else:
            html_table += f"<td class='text-center'></td>"
        if pd.notna(row["Catégorie FSGT"]):
            html_table += f"<td class='text-center'>{row['Catégorie FSGT']}</td>"
        else:
            html_table += f"<td class='text-center'></td>"
        if pd.notna(row["Catégorie d'âge FSGT"]):
            category = row["Catégorie d'âge FSGT"]
            html_table += f"<td class='text-center'>{category}</td>"
        else:
            html_table += f"<td class='text-center'></td>"
        if pd.notna(row["Catégorie FFC"]):
            html_table += f"<td class='text-center'>{row['Catégorie FFC']}</td>"
        else:
            html_table += f"<td class='text-center'></td>"
        html_table += "</tr>"
    html_table += "</tbody></table>"
    return html_table


def generate_markdown_webpage(filename, service_account_info):
    """Generate the markdown webpage for the calendar.

    Parameters
    ----------
    filename: str
        The filename to write the markdown webpage to.
    service_account_info : dict
        Google service account credentials information.
    """

    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    drive_service = build("drive", "v3", credentials=credentials)

    request = drive_service.files().get_media(fileId=SHEET_ID)
    file_handle = io.BytesIO()
    downloader = MediaIoBaseDownload(file_handle, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    file_handle.seek(0)

    df_licences = pd.read_excel(file_handle, sheet_name=SHEET_NAME, usecols="A:I")
    with open(filename, "w") as f:
        metadata = """---
title: Listing coureurs FSGT 2025
url: double_licences/index.html
save_as: double_licences/index.html
template: page
---
"""

        title = (
            '## <i class="fas fa-id-card"></i> Listing des coureurs double '
            "licenciés 2025\n\n"
        )

        # Search bar
        licences_table = """<div class="mb-3">
    <input type="text"
        class="form-control"
        id="doubleLicencesSearch"
        placeholder="Rechercher un coureur..."
        aria-label="Rechercher un coureur">
</div>
"""
        licences_table += generate_html_table(df_licences)

        f.write(metadata + title + licences_table)


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
        generate_markdown_webpage(
            "content/pages/double_licences.md", service_account_info
        )
