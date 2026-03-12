import os

import pandas as pd

SHEET_ID = "119yxSJ-GrGMWzlg1pS57MaD7dzNkqNUQHcAyO0GMt0I"
SHEET_LISTING = "Listing"
SHEET_DIRECTORY = "Annuaire"
URL_LISTING = (
    "https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_LISTING}"
)
URL_DIRECTORY = (
    "https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_DIRECTORY}"
)


def generate_person_dropdown(df, *, first_name, last_name, counter_unique_dropdown):
    """Create an HTML table of a person contact by fetching data based on first and
    last name.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the directory data.
    first_name : str
        The first name to search for.
    last_name : str
        The last name to search for.
    counter_unique_dropdown : int
        The counter for the unique dropdown.

    Returns
    -------
    str
        The HTML table for the directory.
    """
    if pd.isna(first_name) or pd.isna(last_name):
        return ""

    row = df.query(f"Prénom == '{first_name}' and Nom == '{last_name}'").iloc[0]
    template = '<div class="dropdown">'
    template += (
        f'<button class="btn btn-link dropdown-toggle" type="button" '
        f'id="contactDropdown{counter_unique_dropdown}" data-bs-toggle="dropdown" '
        f'aria-expanded="false">{row["Prénom"]} {row["Nom"]}</button>'
    )
    template += (
        f'<div class="dropdown-menu p-3" '
        f'aria-labelledby="contactDropdown{counter_unique_dropdown}">'
        '<table class="contact-info-table">'
    )
    if not pd.isna(row["Adresse"]):
        address = row["Adresse"].replace("\n", "<br>")
        template += (
            "<tr>"
            '<td><i class="fas fa-map-marker-alt"></i></td>'
            f"<td>{address}</td>"
            "</tr>"
        )
    if not pd.isna(row["Téléphone"]):
        template += (
            "<tr>"
            '<td><i class="fas fa-phone"></i></td>'
            f'<td>{row["Téléphone"]}</td>'
            "</tr>"
        )
    if not pd.isna(row["Mobile"]):
        template += (
            "<tr>"
            '<td><i class="fas fa-mobile-alt"></i></td>'
            f'<td>{row["Mobile"]}</td>'
            "</tr>"
        )
    if not pd.isna(row["Email"]):
        template += (
            "<tr>"
            '<td><i class="fas fa-envelope"></i></td>'
            f'<td><a href="mailto:{row["Email"]}">{row["Email"]}</a></td>'
            "</tr>"
        )
    template += "</table></div></div>"
    return template.replace("\n", "")


def generate_club_listing(df_listing, df_directory):
    """Create the first table of the clubs page.

    Parameters
    ----------
    df_listing : pd.DataFrame
        The dataframe containing the listing data.
    df_directory : pd.DataFrame
        The dataframe containing the directory data.

    Returns
    -------
    str
        The HTML table for the clubs listing.
    """
    counter_unique_dropdown = 0
    html_table = (
        '<table class="table" id="clubTable"><thead><tr>'
        "<th>Club</th>"
        "<th>Contacts</th>"
        "</tr></thead>"
        "<tbody>"
    )
    for _, sub_df in df_listing.groupby("Ville", sort=True):
        for row_id, row in sub_df.iterrows():
            html_table += f'<tr><td>{row["Nom du club"]}</td>'
            html_table += f"<td>"
            if (
                president := generate_person_dropdown(
                    df_directory,
                    first_name=row["Président Prénom"],
                    last_name=row["Président Nom"],
                    counter_unique_dropdown=counter_unique_dropdown,
                )
            ) != "":
                html_table += f"<strong>Président</strong> : {president}<br>"
                counter_unique_dropdown += 1
            if (
                responsable_cyclisme := generate_person_dropdown(
                    df_directory,
                    first_name=row["Responsable cyclisme Prénom"],
                    last_name=row["Responsable cyclisme Nom"],
                    counter_unique_dropdown=counter_unique_dropdown,
                )
            ) != "":
                html_table += (
                    f"<strong>Responsable cyclisme</strong> : "
                    f"{responsable_cyclisme}<br>"
                )
                counter_unique_dropdown += 1
            if (
                cyclotouriste := generate_person_dropdown(
                    df_directory,
                    first_name=row["Responsable cyclotouriste Prénom"],
                    last_name=row["Responsable cyclotouriste Nom"],
                    counter_unique_dropdown=counter_unique_dropdown,
                )
            ) != "":
                html_table += (
                    f"<strong>Responsable cyclotouriste</strong> : {cyclotouriste}<br>"
                )
                counter_unique_dropdown += 1
            if (
                correspondant_vtt := generate_person_dropdown(
                    df_directory,
                    first_name=row["Correspondant VTT Prénom"],
                    last_name=row["Correspondant VTT Nom"],
                    counter_unique_dropdown=counter_unique_dropdown,
                )
            ) != "":
                html_table += (
                    f"<strong>Correspondant VTT</strong> : {correspondant_vtt}<br>"
                )
                counter_unique_dropdown += 1
            if (
                correspondant_velos_enfants := generate_person_dropdown(
                    df_directory,
                    first_name=row["Correspondant vélos enfants Prénom"],
                    last_name=row["Correspondant vélos enfants Nom"],
                    counter_unique_dropdown=counter_unique_dropdown,
                )
            ) != "":
                html_table += (
                    f"<strong>Correspondant vélos enfants</strong> : "
                    f"{correspondant_velos_enfants}<br>"
                )
                counter_unique_dropdown += 1
            html_table += "</td>"
            html_table += "</tr>\n"
    html_table += "</tbody></table>"
    return html_table


def generate_printable_person_info(df, *, first_name, last_name):
    """Create a formatted string of a person's contact information.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the directory data.
    first_name : str
        The first name to search for.
    last_name : str
        The last name to search for.

    Returns
    -------
    str
        The formatted contact information string.
    """
    if pd.isna(first_name) or pd.isna(last_name):
        return ""

    row = df.query(f"Prénom == '{first_name}' and Nom == '{last_name}'").iloc[0]
    info = f"{row['Prénom']} {row['Nom']}\n"

    if not pd.isna(row["Adresse"]):
        info += f"Adresse: {row['Adresse']}\n"
    if not pd.isna(row["Téléphone"]):
        info += f"Tél: {row['Téléphone']}\n"
    if not pd.isna(row["Mobile"]):
        info += f"Mobile: {row['Mobile']}\n"
    if not pd.isna(row["Email"]):
        info += f"Email: {row['Email']}\n"

    return info.rstrip()


def generate_printable_club_listing_html(df_listing, df_directory):
    """Create a printable HTML table of the clubs listing with left-aligned card-based layout.

    Parameters
    ----------
    df_listing : pd.DataFrame
        The dataframe containing the listing data.
    df_directory : pd.DataFrame
        The dataframe containing the directory data.

    Returns
    -------
    str
        The HTML table formatted for printing.
    """
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Liste des clubs FSGT 71</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        @page {
            size: landscape;
            margin: 2cm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 10pt;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid;
            padding: 8px;
            vertical-align: top;
            text-align: left;
        }
        th {
            font-weight: bold;
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            text-align: left;
        }
        .contact-card {
            border: 1px solid;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 5px;
            text-align: left;
        }
        .contact-card-header {
            border-bottom: 1px solid;
            padding-bottom: 5px;
            margin-bottom: 8px;
            font-weight: bold;
            text-align: left;
        }
        .contact-info {
            margin: 5px 0;
            text-align: left;
            display: flex;
            align-items: flex-start;
        }
        .icon {
            width: 20px;
            text-align: center;
            margin-right: 5px;
            flex-shrink: 0;
        }
        .contact-text {
            flex-grow: 1;
            word-break: break-word;
            overflow-wrap: break-word;
            max-width: 100%;
        }
        h1 {
            text-align: left;
        }

        @media print {
            @page {
                size: A4 landscape;
                margin: 2cm;
            }

            body {
                width: 100%;
                margin: 0;
                padding: 0;
            }

            .contact-card {
                break-inside: avoid;
            }

            /* Ensure good printing of background colors */
            * {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
        }
    </style>
</head>
<body>
    <h1>Liste des clubs FSGT 71</h1>
    <table>
        <thead>
            <tr>
                <th style="width: 30%;">Club</th>
                <th style="width: 70%;">Contacts</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, sub_df in df_listing.groupby("Ville", sort=True):
        for _, row in sub_df.iterrows():
            html += f'<tr><td>{row["Nom du club"]}</td><td>'
            html += '<div class="cards-grid">'

            # President
            if president := generate_printable_person_info_html(
                df_directory,
                first_name=row["Président Prénom"],
                last_name=row["Président Nom"],
            ):
                html += """
                <div class="contact-card">
                    <div class="contact-card-header">Président</div>
                    {president}
                </div>
                """.format(president=president)

            # Responsable cyclisme
            if resp_cyclisme := generate_printable_person_info_html(
                df_directory,
                first_name=row["Responsable cyclisme Prénom"],
                last_name=row["Responsable cyclisme Nom"],
            ):
                html += """
                <div class="contact-card">
                    <div class="contact-card-header">Responsable cyclisme</div>
                    {resp_cyclisme}
                </div>
                """.format(resp_cyclisme=resp_cyclisme)

            # Responsable cyclotouriste
            if resp_cyclotouriste := generate_printable_person_info_html(
                df_directory,
                first_name=row["Responsable cyclotouriste Prénom"],
                last_name=row["Responsable cyclotouriste Nom"],
            ):
                html += """
                <div class="contact-card">
                    <div class="contact-card-header">Responsable cyclotouriste</div>
                    {resp_cyclotouriste}
                </div>
                """.format(resp_cyclotouriste=resp_cyclotouriste)

            # Correspondant VTT
            if resp_vtt := generate_printable_person_info_html(
                df_directory,
                first_name=row["Correspondant VTT Prénom"],
                last_name=row["Correspondant VTT Nom"],
            ):
                html += """
                <div class="contact-card">
                    <div class="contact-card-header">Correspondant VTT</div>
                    {resp_vtt}
                </div>
                """.format(resp_vtt=resp_vtt)

            # Correspondant vélos enfants
            if resp_velos_enfants := generate_printable_person_info_html(
                df_directory,
                first_name=row["Correspondant vélos enfants Prénom"],
                last_name=row["Correspondant vélos enfants Nom"],
            ):
                html += """
                <div class="contact-card">
                    <div class="contact-card-header">Correspondant vélos enfants</div>
                    {resp_velos_enfants}
                </div>
                """.format(resp_velos_enfants=resp_velos_enfants)

            html += "</div></td></tr>"

    html += """
        </tbody>
    </table>
</body>
</html>
    """
    return html


def generate_printable_person_info_html(df, *, first_name, last_name):
    """Create an HTML formatted string of a person's contact information.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the directory data.
    first_name : str
        The first name to search for.
    last_name : str
        The last name to search for.

    Returns
    -------
    str
        The HTML formatted contact information string.
    """
    if pd.isna(first_name) or pd.isna(last_name):
        return ""

    row = df.query(f"Prénom == '{first_name}' and Nom == '{last_name}'").iloc[0]
    info = (
        f'<div class="contact-info"><strong>{row["Prénom"]} {row["Nom"]}</strong></div>'
    )

    if not pd.isna(row["Adresse"]):
        address = row["Adresse"].replace(chr(10), "<br>")
        info += (
            f'<div class="contact-info">'
            f'<span class="icon"><i class="fas fa-map-marker-alt"></i></span>'
            f'<span class="contact-text">{address}</span></div>'
        )
    if not pd.isna(row["Téléphone"]):
        info += (
            f'<div class="contact-info">'
            f'<span class="icon"><i class="fas fa-phone"></i></span>'
            f'<span class="contact-text">{row["Téléphone"]}</span></div>'
        )
    if not pd.isna(row["Mobile"]):
        info += (
            f'<div class="contact-info">'
            f'<span class="icon"><i class="fas fa-mobile-alt"></i></span>'
            f'<span class="contact-text">{row["Mobile"]}</span></div>'
        )
    if not pd.isna(row["Email"]):
        info += (
            f'<div class="contact-info">'
            f'<span class="icon"><i class="fas fa-envelope"></i></span>'
            f'<span class="contact-text">{row["Email"]}</span></div>'
        )

    return info


def generate_markdown_webpage(filename):
    """Generate the markdown webpage for the clubs listing.

    Parameters
    ----------
    filename: str
        The filename to write the markdown webpage to.
    """
    with open(filename, "w") as f:
        metadata = """---
title: Liste des clubs FSGT 71
url: clubs/index.html
save_as: clubs/index.html
template: page
---

"""
        title = '## <i class="fas fa-bicycle fas-title"></i> Liste des clubs\n\n<div class="h2-spacer"></div>\n\n'

        listing_clubs_roads = "### Correspondants\n\n"
        # add a search bar
        listing_clubs_roads += """<div class="mb-3">
    <input type="text"
           class="form-control"
           id="clubSearch"
           placeholder="Rechercher un club ou un contact..."
           aria-label="Rechercher un club">
</div>
<div class="alert alert-info small" role="alert">
    <i class="fas fa-info-circle"></i> Cliquez sur le nom d'un correspondant pour
    afficher ses coordonnées détaillées (adresse, téléphone, email).
</div>
"""
        df_listing, df_directory = pd.read_csv(URL_LISTING), pd.read_csv(URL_DIRECTORY)
        listing_clubs_roads += generate_club_listing(df_listing, df_directory)
        listing_clubs_roads += "\n\n"

        f.write(metadata + title + listing_clubs_roads)


if __name__ == "__main__":
    """Entry point for the pixi task."""
    generate_markdown_webpage("content/pages/clubs.md")

    df_listing, df_directory = pd.read_csv(URL_LISTING), pd.read_csv(URL_DIRECTORY)
    html_content = generate_printable_club_listing_html(df_listing, df_directory)
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/clubs_printable.html", "w", encoding="utf-8") as f:
        f.write(html_content)
