import io
import json
import os
import warnings
from numbers import Real

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]
SHEET_ID = "1PEstKqoGVa7FgkAcg090mhRVr3Hs2s9G"
SHEET_NAME = "Licenciés FSGT"


def _filter_licences(df_licences):
    """Filter only the interested columns and rows."""
    # drop empty rows available due to row validation in Google Sheets
    # ensure a copy is made to avoid modifying the original dataframe
    df_licences = df_licences.copy().dropna(subset=["Nom"])
    # filter licences validated and with an affected category
    mask_date_licence = df_licences["Date"].notna()
    mask_category_2025 = df_licences[2025].notna()
    df_licences = df_licences[mask_date_licence & mask_category_2025]
    return df_licences


def generate_html_table(df_licences):
    """Generate the HTML table for the licences.

    Parameters
    ----------
    df_licences : pd.DataFrame
        The dataframe containing the licences data.

    Returns
    -------
    str
        The HTML table for the licences.
    """
    html_table = (
        '<table class="table" id="licencesTable"><thead><tr>'
        "<th>Nom</th>"
        "<th>Prénom</th>"
        "<th>Club</th>"
        "<th>Catégories</th>"
        "</tr></thead>"
        "<tbody>"
    )
    for _, row in df_licences.iterrows():
        html_table += "<tr>"
        html_table += f"<td>{row['Nom'].upper()}</td>"
        html_table += f"<td>{row['Prénom'].capitalize()}</td>"
        html_table += f"<td>{row['Club']}</td>"
        if pd.notna(row["M/D"]):
            cat = int(row["M/D"]) if isinstance(row["M/D"], Real) else row["M/D"]
            html_table += f"<td>{cat}</td>"
        else:
            html_table += f"<td>{row[2025]}</td>"
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

    df_licences = pd.read_excel(
        file_handle, sheet_name=SHEET_NAME, skiprows=2, usecols="B:S"
    )
    df_licences["Date"] = pd.to_datetime(df_licences["Date"], dayfirst=True)
    df_licences = _filter_licences(df_licences)

    today = pd.Timestamp.today()
    last_tuesday = None
    if today.month in range(3, 8):
        # Special handling for the first week of March
        if today.month == 3 and today.day >= 6 and today.day < 11:
            # Between March 6-11, use March 6th as the cutoff date
            last_tuesday = pd.Timestamp(today.year, 3, 6)
            last_tuesday = last_tuesday.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        # Normal Tuesday schedule for rest of the season
        elif today.month > 3 or today.day >= 11:
            if today.weekday() != 1:  # not a Tuesday
                # Find last Tuesday by calculating days since last Tuesday
                days_since_tuesday = (today.weekday() - 1) % 7
                last_tuesday = today - pd.Timedelta(days=days_since_tuesday)
                last_tuesday = last_tuesday.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            df_licences = df_licences[df_licences["Date"] <= last_tuesday]

    table_update_date = last_tuesday if last_tuesday else today
    # Calculate next Tuesday
    days_until_next_tuesday = (1 - table_update_date.weekday() + 7) % 7
    table_next_update_date = table_update_date + pd.Timedelta(
        days=days_until_next_tuesday
    )
    n_riders = len(df_licences)

    with open(filename, "w") as f:
        metadata = """---
title: Listing coureurs FSGT 2025
url: licences_fsgt/index.html
save_as: licences_fsgt/index.html
template: page
---
"""

        title = '## <i class="fas fa-id-card"></i> Listing des licenciés FSGT 2025\n\n'

        info = f"""<div class="alert alert-info small" role="alert">
<i class="fas fa-info-circle"></i> En cas de
problème, merci de contacter Eric Rabut :
<a href="mailto:eric.rabut@orange.fr">eric.rabut@orange.fr</a>.
<strong>Uniquement pour les coureurs FSGT71</strong>.
</div>
<div class="alert alert-warning small" role="alert">
<i class="fas fa-exclamation-triangle"></i> Durant la saison cycliste, ce tableau est
mis à jour tous les <strong>mardis</strong>. Seuls les coureurs apparaissant dans ce
tableau pourront participer aux courses du week-end.
</div>
<div class="alert alert-success small" role="alert">
<i class="fas fa-calendar-check"></i> Dernière mise à jour le
<strong>{table_update_date.strftime("%d/%m/%Y")}</strong>.
Prochaine mise à jour le
<strong>{table_next_update_date.strftime("%d/%m/%Y")}</strong>.
Il y a actuellement
<strong>{n_riders} coureurs</strong> enregistrés.
</div>
"""

        # Search bar
        licences_table = """<div class="mb-3">
    <input type="text"
        class="form-control"
        id="licencesSearch"
        placeholder="Rechercher un coureur..."
        aria-label="Rechercher un coureur">
</div>
"""
        licences_table += generate_html_table(df_licences)

        f.write(metadata + title + info + licences_table)


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
            "content/pages/licences_fsgt.md", service_account_info
        )
