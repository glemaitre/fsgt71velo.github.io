import json
import os
import warnings

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1_eD1mIZovYdXcHHxpTpGu7VoZ4bON0EtPdX8RdvsuTo"
SHEET_NAME = "Feuille 1"
URL_CALENDAR = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
    f"tq?tqx=out:csv&sheet={SHEET_NAME}"
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


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
        '<table class="table" id="externalRidersTable"><thead>'
        "<tr>"
        "<th rowspan='2' class='align-middle text-center'>Nom</th>"
        "<th rowspan='2' class='align-middle text-center'>Prénom</th>"
        "<th rowspan='2' class='align-middle text-center'>Date de naissance</th>"
        "<th rowspan='2' class='align-middle text-center'>Club</th>"
        "<th rowspan='2' class='align-middle text-center'>Département</th>"
        "<th rowspan='2' class='align-middle text-center'>Licence</th>"
        "<th colspan='5' class='text-center'>Catégories</th>"
        "<th rowspan='2' class='align-middle text-center'>Date d'inscription</th>"
        "</tr>"
        "<tr>"
        "<th class='text-center'>FFC</th>"
        "<th class='text-center'>UFOLEP</th>"
        "<th class='text-center'>FSGT (extérieur)</th>"
        "<th class='text-center'>FSGT 71</th>"
        "<th class='text-center'>Age</th>"
        "</tr></thead>"
        "<tbody>"
    )
    for _, row in df_licences.iterrows():
        html_table += "<tr>"
        html_table += f"<td class='text-center'>{row['Nom'].upper()}</td>"
        html_table += f"<td class='text-center'>{row['Prénom'].capitalize()}</td>"
        birth_date = row["Date de naissance"].strftime("%d/%m/%Y")
        html_table += f"<td class='text-center'>{birth_date}</td>"
        html_table += f"<td class='text-center'>{row['Club']}</td>"
        html_table += f"<td class='text-center'>{row['Département']}</td>"
        html_table += f"<td class='text-center'>{row['Numéro de licence FSGT']}</td>"
        if pd.notna(row["Catégorie FFC"]):
            html_table += f"<td class='text-center'>{row['Catégorie FFC']}</td>"
        else:
            html_table += f"<td class='text-center'></td>"
        if pd.notna(row["Catégorie UFOLEP"]):
            html_table += f"<td class='text-center'>{row['Catégorie UFOLEP']}</td>"
        else:
            html_table += f"<td class='text-center'></td>"
        category = row["Catégorie FSGT département d'origine"]
        html_table += f"<td class='text-center'>{category}</td>"
        html_table += (
            f"<td class='text-center'>{row['Catégorie autorisée FSGT 71']}</td>"
        )
        html_table += f"<td class='text-center'>{row['Catégorie âge']}</td>"
        date_inscription = row["Date d'inscription"]
        html_table += (
            f"<td class='text-center'>{date_inscription.strftime('%d/%m/%Y')}</td>"
        )
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
    sheets_service = build("sheets", "v4", credentials=credentials)

    values = (
        sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=SHEET_ID, range=SHEET_NAME)
        .execute()
    ).get("values", [])

    headers = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))

    df_licences = pd.DataFrame(data, columns=headers)
    df_licences["Date d'inscription"] = pd.to_datetime(
        df_licences["Date d'inscription"], dayfirst=True
    )
    df_licences["Date de naissance"] = pd.to_datetime(
        df_licences["Date de naissance"], dayfirst=True
    )
    df_licences = df_licences.dropna(subset=["Date d'inscription"])

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
            df_licences = df_licences[df_licences["Date d'inscription"] <= last_tuesday]

    with open(filename, "w") as f:
        metadata = """---
title: Listing coureurs extérieurs
url: external_riders/index.html
save_as: external_riders/index.html
template: page
---
"""

        title = '## <i class="fas fa-id-card"></i> Listing des coureurs extérieurs\n\n'

        info = """<div class="alert alert-info small" role="alert">
<i class="fas fa-info-circle"></i> En cas de
problème, merci de contacter les reponsables de la saisie des coureurs extérieurs :
<a href="mailto:coureursexterieur@fsgt71velo.fr">coureursexterieur@fsgt71velo.fr</a>.
<strong>Uniquement pour les coureurs extérieurs à la FSGT71</strong>.
</div>
<div class="alert alert-warning small" role="alert">
<i class="fas fa-exclamation-triangle"></i> Durant la saison cycliste, ce tableau est
mis à jour tous les <strong>mardis</strong>. Seuls les coureurs apparaissant dans ce
tableau pourront participer aux courses du week-end.
</div>
"""

        # Search bar
        licences_table = """<div class="mb-3">
    <input type="text"
        class="form-control"
        id="externalRidersSearch"
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
            "content/pages/external_riders.md", service_account_info
        )
