# %%
import json
import os
import warnings

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build


def get_folder_id(service, folder_name, parent_id=None):
    """Get the folder id from the folder name.

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        The service to use to get the folder id.
    folder_name : str
        The name of the folder to get the id from.
    parent_id : str, optional
        The id of the parent folder, by default None.

    Returns
    -------
    str
        The id of the folder.
    """
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = (
        service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    )

    items = results.get("files", [])
    return items[0]["id"] if items else None


def list_pdf_files(service_account_info):
    """List all reports stored as PDF files on the google drive.

    Parameters
    ----------
    service_account_info: dict
        The service account information.

    Returns
    -------
    pd.DataFrame
        The dataframe containing the reports.
    """
    filenames = []
    file_ids = []
    years = []

    # Create credentials
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    # Build the service
    service = build("drive", "v3", credentials=credentials)

    fsgt_folder_id = get_folder_id(service, "FSGT 71")
    if not fsgt_folder_id:
        raise ValueError("FSGT 71 folder not found")

    rapport_folder_id = get_folder_id(service, "Rapport Commission", fsgt_folder_id)
    if not rapport_folder_id:
        raise ValueError("Rapport Commission folder not found")

    # Query for all PDF files in year subfolders
    query = (
        f"'{rapport_folder_id}' in parents and mimeType="
        f"'application/vnd.google-apps.folder'"
    )
    year_folders = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
        .get("files", [])
    )

    for year_folder in year_folders:
        pdf_query = f"'{year_folder['id']}' in parents and mimeType='application/pdf'"
        pdf_files = (
            service.files()
            .list(
                q=pdf_query,
                spaces="drive",
                fields="files(name, id, createdTime)",
                orderBy="createdTime desc",
            )
            .execute()
            .get("files", [])
        )

        for file in pdf_files:
            filenames.append(file["name"])
            file_ids.append(file["id"])
            years.append(year_folder["name"])

    df = pd.DataFrame(
        {
            "year": years,
            "filename": filenames,
            "file_id": file_ids,
            "drive_url": [
                f"https://drive.google.com/file/d/{id}/view" for id in file_ids
            ],
        }
    )

    return df


def format_date_from_filename(filename):
    """Format the date from the filename.

    Parameters
    ----------
    filename : str
        The filename to format the date from.

    Returns
    -------
    str
        The formatted date.
    """
    date_str = filename.replace(".pdf", "").split("_")
    if len(date_str) != 3:
        return filename

    months = {
        "01": "Janvier",
        "02": "Février",
        "03": "Mars",
        "04": "Avril",
        "05": "Mai",
        "06": "Juin",
        "07": "Juillet",
        "08": "Août",
        "09": "Septembre",
        "10": "Octobre",
        "11": "Novembre",
        "12": "Décembre",
    }

    day, month, year = date_str
    return f"{int(day)} {months.get(month, month)} {year}"


def generate_markdown_webpage(filename, service_account_info):
    """Generate the markdown webpage for the report.

    Parameters
    ----------
    filename: str
        The filename to write the markdown webpage to.
    service_account_info: dict
        The service account information.
    """
    with open(filename, "w") as f:
        metadata = """---
title: Rapport des commissions cyclistes FSGT 71
url: rapport/index.html
save_as: rapport/index.html
template: page
---

"""
        title = (
            '## <i class="fas fa-file-alt"></i> Rapport des commissions '
            "cyclistes FSGT 71\n\n"
        )
        df = list_pdf_files(service_account_info)

        report_listing = '<div class="row">\n'
        for year, df_year in sorted(df.groupby("year"), reverse=True):
            report_listing += (
                '<div class="col-md-6 col-lg-4 mb-4">\n'
                '<div class="card h-100">\n'
                '<div class="card-header">\n'
                f'<h4 class="card-title mb-0 text-center">Année {year}</h4>\n'
                "</div>\n"
                '<div class="card-body">\n'
                '<ul class="list-unstyled mb-0">\n'
            )

            df_year = df_year.copy()  # Create copy to avoid SettingWithCopyWarning
            df_year["date"] = pd.to_datetime(
                df_year["filename"].apply(
                    lambda x: "_".join(x.replace(".pdf", "").split("_")[::-1])
                ),
                format="%Y_%m_%d",
                errors="coerce",
            )

            for _, row in df_year.sort_values("date", ascending=False).iterrows():
                report_listing += (
                    f'<li><a href="{row["drive_url"]}">'
                    f'Compte rendu du {format_date_from_filename(row["filename"])}'
                    "</a></li>\n"
                )
            report_listing += "</ul>\n</div>\n</div>\n</div>\n"  # Close column div

        report_listing += "</div>\n"  # Close row div
        f.write(metadata + title + report_listing)


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
        generate_markdown_webpage("content/pages/rapport.md", service_account_info)
