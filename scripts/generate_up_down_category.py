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

category_mapping = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "F": 7,
}


def _filter_licences(df_licences):
    """Filter only the interested columns and rows."""
    # drop empty rows available due to row validation in Google Sheets
    # ensure a copy is made to avoid modifying the original dataframe
    df_licences = df_licences.copy().dropna(subset=["Nom"])
    # filter licences validated and with an affected category
    mask_date_licence = df_licences["Date"].notna()
    mask_category_2025 = df_licences[2025].notna()
    df_licences = df_licences[mask_date_licence & mask_category_2025]
    mask_up_down_category = df_licences["M/D"].notna()
    df_licences = df_licences[mask_up_down_category]
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

    # Add search control
    html_table = """<div class="mb-3">
        <div class="row">
            <div class="col-md-8">
                <input type="text"
                    class="form-control"
                    id="categorySearch"
                    placeholder="Rechercher un coureur..."
                    aria-label="Rechercher un coureur">
            </div>
        </div>
    </div>"""

    # Modified legend section with filter controls
    html_table += """<div class="mb-3">
    <button class="btn btn-info w-100" type="button" data-bs-toggle="collapse"
    data-bs-target="#legendCollapse" aria-expanded="false"
    aria-controls="legendCollapse">
        <i class="fas fa-filter"></i> Filtrer les changements de catégorie
        <i class="fas fa-chevron-down"></i>
    </button>
    <div class="collapse" id="legendCollapse">
        <div class="row mt-3">
            <div class="col-md-6 mx-auto">
                <div class="card">
                    <div class="card-header text-center">
                        <strong>Type de changement de catégorie</strong>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-around">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showUpgrades" checked>
                                <label class="form-check-label" for="showUpgrades">
                                    <span class="badge category-up">&nbsp;</span> Montées
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showDowngrades" checked>
                                <label class="form-check-label" for="showDowngrades">
                                    <span class="badge category-down">&nbsp;</span> Descentes
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>"""

    # Main table
    html_table += (
        '<table class="table" id="categoryTable"><thead><tr>'
        "<th>Nom</th>"
        "<th>Prénom</th>"
        "<th>Club</th>"
        "<th>Numéro Licence</th>"
        "<th>Catégorie originale</th>"
        "<th>Nouvelle catégorie</th>"
        "<th>Changement</th>"
        "</tr></thead>"
        "<tbody>"
    )

    for _, row in df_licences.iterrows():
        try:
            category_original = str(int(row[2025]))
        except ValueError:
            category_original = str(row[2025])

        try:
            category_new = str(int(row["M/D"]))
        except ValueError:
            category_new = str(row["M/D"])

        is_up = category_mapping[category_original] > category_mapping[category_new]
        row_class = "category-up" if is_up else "category-down"
        arrow = (
            '<i class="fas fa-arrow-up"></i>'
            if is_up
            else '<i class="fas fa-arrow-down"></i>'
        )

        html_table += f'<tr class="{row_class}">'
        html_table += f"<td>{row['Nom'].upper()}</td>"
        html_table += f"<td>{row['Prénom'].capitalize()}</td>"
        html_table += f"<td>{row['Club']}</td>"
        html_table += f"<td>{row['Numéro']}</td>"
        html_table += f"<td>{category_original}</td>"
        html_table += f"<td>{category_new}</td>"
        html_table += f"<td class='text-center'>{arrow}</td>"
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
    if today.month in range(2, 8) and (today.month > 2 or today.day >= 25):
        # During the race period (from 25/02 to 31/07), we should drop riders whose
        # registration was performed after a Tuesday.
        if today.weekday() != 1:  # not a Tuesday
            # Find last Tuesday by calculating days since last Tuesday
            days_since_tuesday = (today.weekday() - 1) % 7
            last_tuesday = today - pd.Timedelta(days=days_since_tuesday)
            last_tuesday = last_tuesday.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            df_licences = df_licences[df_licences["Date"] <= last_tuesday]

    with open(filename, "w") as f:
        metadata = """---
title: Listing des montées et descentes de catégorie 2025
url: up_down_category/index.html
save_as: up_down_category/index.html
template: page
---
"""
        title = (
            '## <i class="fas fa-id-card"></i> Listing des changements de '
            "catégorie 2025\n\n"
        )

        # Generate single table
        category_table = generate_html_table(df_licences)

        f.write(metadata + title + category_table)


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
            "content/pages/up_down_category.md", service_account_info
        )
