import pandas as pd

SHEET_ID = "1ocHqS1lCjGVwKTd_ES_L06eOFDN90Jd_Kap3OtZhgVM"
SHEET_LISTING = "Listing"
SHEET_DIRECTORY = "Annuaire"
URL_LISTING = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
    f"tq?tqx=out:csv&sheet={SHEET_LISTING}"
)
URL_DIRECTORY = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz"
    f"/tq?tqx=out:csv&sheet={SHEET_DIRECTORY}"
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
        '<button class="btn btn-link dropdown-toggle" type="button" '
        f'id="contactDropdown{counter_unique_dropdown}" data-bs-toggle="dropdown" '
        f'aria-expanded="false">'
        f'{row["Prénom"]} {row["Nom"]}</button>'
    )
    template += (
        f'<div class="dropdown-menu p-3" '
        f'aria-labelledby="contactDropdown{counter_unique_dropdown}">'
        '<table class="contact-info-table">'
    )
    if not pd.isna(row["Adresse"]):
        template += (
            "<tr>"
            '<td><i class="fas fa-map-marker-alt"></i></td>'
            f'<td>{row["Adresse"].replace("\n", "<br>")}</td>'
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
        title = '## <i class="fas fa-bicycle"></i> Liste des clubs\n\n'

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
