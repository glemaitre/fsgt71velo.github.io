# %%
import datetime
import json
import os
import warnings
from pathlib import Path

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1TDq1ffECjsfuxY8ITAxhU8YCh3wY_Mim91b7qSh3DjM"
RANGE_NAME = "Form Responses 1!A:AN"

template_rider_info_txt = """
Nom: {Nom}
Prénom: {Prénom}
Email: {Email Address}
Date de naissance: {Date de naissance}
Club: {Club}
Département: {Département}

************ LICENCE FSGT **************
Numéro de licence: {Numéro de licence FSGT}
Catégorie: {Catégorie FSGT}
Lien vers la licence: {Téléversez licence FSGT}
****************************************

************ LICENCE UFOLEP **************
Numéro de licence: {Numéro de licence UFOLEP}
Catégorie: {Catégorie UFOLEP}
Lien vers la licence: {Téléversez licence UFOLEP}
****************************************

************ LICENCE FFC **************
Numéro de licence: {Numéro de licence FFC}
Catégorie: {Catégorie FFC}
Lien vers la licence: {Téléversez licence FFC}
****************************************
"""

template_rider_info_html = """
<div>
    <h3>Informations du coureur</h3>
    <p><strong>Nom:</strong> {Nom}<br>
    <strong>Prénom:</strong> {Prénom}<br>
    <strong>Email:</strong> {Email Address}<br>
    <strong>Date de naissance:</strong> {Date de naissance}<br>
    <strong>Club:</strong> {Club}<br>
    <strong>Département:</strong> {Département}</p>

    <div style="margin: 20px 0; padding: 10px; border: 1px solid #ddd;">
        <h4>LICENCE FSGT</h4>
        <p><strong>Numéro de licence:</strong> {Numéro de licence FSGT}<br>
        <strong>Catégorie:</strong> {Catégorie FSGT}<br>
        <strong>Lien vers la licence:</strong>
        <a href="{Téléversez licence FSGT}">{Téléversez licence FSGT}</a></p>
    </div>

    <div style="margin: 20px 0; padding: 10px; border: 1px solid #ddd;">
        <h4>LICENCE UFOLEP</h4>
        <p><strong>Numéro de licence:</strong> {Numéro de licence UFOLEP}<br>
        <strong>Catégorie:</strong> {Catégorie UFOLEP}<br>
        <strong>Lien vers la licence:</strong>
        <a href="{Téléversez licence UFOLEP}">{Téléversez licence UFOLEP}</a></p>
    </div>

    <div style="margin: 20px 0; padding: 10px; border: 1px solid #ddd;">
        <h4>LICENCE FFC</h4>
        <p><strong>Numéro de licence:</strong> {Numéro de licence FFC}<br>
        <strong>Catégorie:</strong> {Catégorie FFC}<br>
        <strong>Lien vers la licence:</strong>
        <a href="{Téléversez licence FFC}">{Téléversez licence FFC}</a></p>
    </div>
</div>
"""


def create_pivot_for_row(row):
    """Create a pivot table for a single row of history data.

    Parameters
    ----------
    row : pandas.Series
        A single row of history data containing federation history columns.

    Returns
    -------
    pandas.DataFrame
        A pivot table with federations as index, years as columns, and
        categories as values. The table includes data for FFC, FSGT, and UFOLEP
        federations for the past 6 years.
    """
    current_year = datetime.datetime.now().year
    year_range = range(current_year - 6, current_year)

    # Convert the row to a dataframe
    df_row = pd.DataFrame([row])

    # Melt the dataframe
    df_melted = df_row.melt()

    # Extract components from column names
    df_melted["federation"] = df_melted["variable"].str.extract(r"Historique (\w+)")
    df_melted["category"] = df_melted["variable"].str.extract(r"\[(.*?)\]")

    # Split the years and explode
    df_melted["year"] = df_melted["value"].str.split(",")
    df_melted = df_melted.explode("year")

    # Clean up years
    df_melted["year"] = df_melted["year"].str.strip()
    df_melted = df_melted[df_melted["year"].notna()]
    df_melted["year"] = pd.to_numeric(df_melted["year"], downcast="integer")

    # Create pivot table
    pivot = df_melted.pivot_table(
        index="federation",
        columns="year",
        values="category",
        aggfunc=lambda x: ", ".join(x.dropna().unique()),
    )

    # Ensure all years are present
    for year in year_range:
        if year not in pivot.columns:
            pivot[year] = ""

    # Sort columns and fill NaN
    pivot = pivot.reindex(columns=sorted(pivot.columns)).fillna("")

    # Ensure all federations are present
    all_federations = ["FFC", "FSGT", "UFOLEP"]
    pivot = pivot.reindex(index=all_federations, fill_value="")

    # Convert columns to integers
    pivot.columns = pivot.columns.astype(int)

    return pivot


def format_history_table(history_table, format_type="txt"):
    """Generate formatted history table in either HTML or text format.

    Parameters
    ----------
    history_table : pandas.DataFrame
        Pivot table containing federation history data.
    format_type : str, optional
        Output format, either "html" or "txt" (default).

    Returns
    -------
    str
        Formatted table as either HTML or markdown text.
    """
    years = sorted(history_table.columns)

    if format_type == "html":
        html_parts = [
            '<div style="margin: 20px 0;">',
            "<h3>Historique</h3>",
            '<table style="border-collapse: collapse; width: 100%;">',
            "<tr>",
            '<th style="border: 1px solid #ddd; padding: 8px; text-align: left;">'
            "Fédération</th>",
        ]

        for year in years:
            html_parts.append(
                f'<th style="border: 1px solid #ddd; padding: 8px;">{year}</th>'
            )
        html_parts.append("</tr>")

        for federation in history_table.index:
            html_parts.append("<tr>")
            html_parts.append(
                f'<td style="border: 1px solid #ddd; padding: 8px;">'
                f"<strong>{federation}</strong></td>"
            )
            for year in years:
                category = history_table.loc[federation, year]
                html_parts.append(
                    f'<td style="border: 1px solid #ddd; padding: 8px; '
                    f'text-align: center;">{category if category else "-"}</td>'
                )
            html_parts.append("</tr>")

        html_parts.extend(["</table>", "</div>"])
        return "\n".join(html_parts)

    else:  # txt format with markdown table
        header = "| Fédération | " + " | ".join(str(year) for year in years) + " |"
        separator = "|------------|" + "|".join("-" * 6 for _ in years) + "|"

        rows = []
        for federation in history_table.index:
            row_values = [federation]
            for year in years:
                category = history_table.loc[federation, year]
                row_values.append(category if category else "-")
            rows.append("| " + " | ".join(row_values) + " |")

        return (
            "\n## Historique\n\n" + header + "\n" + separator + "\n" + "\n".join(rows)
        )


def format_rider_information(df, format_type="txt"):
    """Generate formatted information for each rider including their history.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing rider information and history data.
    format_type : str, optional
        Output format, either "html" or "txt" (default).

    Returns
    -------
    list[str]
        List of formatted entries for each rider, including personal information
        and federation history in the specified format.
    """
    history_cols = [col for col in df.columns if col.startswith("Historique")]
    df_history = df[history_cols]
    pivot_tables = {
        index: create_pivot_for_row(row) for index, row in df_history.iterrows()
    }

    formatted_entries = []
    template = (
        template_rider_info_html if format_type == "html" else template_rider_info_txt
    )

    for idx, row in df.iterrows():
        # Convert date format if it exists and is not empty
        if pd.notna(row["Date de naissance"]):
            try:
                date = pd.to_datetime(row["Date de naissance"])
                row = row.copy()  # Create a copy to avoid modifying the original
                row["Date de naissance"] = date.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                pass  # Keep original value if conversion fails

        rider_info = template.format(**row)
        history_table = pivot_tables[idx]
        history_text = format_history_table(history_table, format_type)
        complete_entry = rider_info + "\n" + history_text
        formatted_entries.append(complete_entry)

    return formatted_entries


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


def generate_listing(path_name, service_account_info):
    """Generate text and HTML files containing rider information from recent
    submissions.

    Parameters
    ----------
    path_name : str
        The directory path where the output files will be saved.
    service_account_info : dict
        Google service account credentials information.

    Notes
    -----
    This function:
    - Connects to a Google Sheet containing rider declarations
    - Downloads all entries and filters for submissions from the last day
    - For each rider, generates three files in the specified directory:
        - rider_N.txt: Text format of rider information and history
        - rider_N.html: HTML format of rider information and history
        - rider_N_subject.txt: Email subject line with rider's name
    where N is the index number of the rider.
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
            row += [""] * (len(headers) - len(row))

    df = pd.DataFrame(data, columns=headers)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # one_day_ago = pd.Timestamp.now() - pd.Timedelta(days=1)
    # df_last_day = df[df["Timestamp"] >= one_day_ago]
    # if df_last_day.empty:
    #     return

    # Temporary specific time range filter
    start_time = pd.Timestamp("2025-02-08 15:00:00")
    end_time = pd.Timestamp("2025-02-08 23:59:59")
    df_last_day = df[(df["Timestamp"] >= start_time) & (df["Timestamp"] <= end_time)]
    if df_last_day.empty:
        return

    path_name = Path(path_name).resolve()
    path_name.mkdir(parents=True, exist_ok=True)

    formatted_riders_txt = format_rider_information(df_last_day, format_type="txt")
    formatted_riders_html = format_rider_information(df_last_day, format_type="html")

    for idx, (txt, html) in enumerate(zip(formatted_riders_txt, formatted_riders_html)):
        # Text file
        txt_file = path_name / f"rider_{idx}.txt"
        txt_file.write_text(txt)

        # HTML file
        html_file = path_name / f"rider_{idx}.html"
        html_file.write_text(html)

        # Subject file
        record_rider = df_last_day.iloc[idx]
        subject_file = path_name / f"rider_{idx}_subject.txt"
        subject_file.write_text(
            "Enregistrement coureur extérieur : "
            f"{record_rider['Nom']} {record_rider['Prénom']}"
        )


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
        generate_listing("./scratch/external_riders", service_account_info)
