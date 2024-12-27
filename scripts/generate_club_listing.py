# %%
import pandas as pd

sheet_id = "1ocHqS1lCjGVwKTd_ES_L06eOFDN90Jd_Kap3OtZhgVM"
sheet_listing, sheet_directory = "Listing", "Annuaire"
url_listing = (
    f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/"
    f"tq?tqx=out:csv&sheet={sheet_listing}"
)
url_directory = (
    f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz"
    f"/tq?tqx=out:csv&sheet={sheet_directory}"
)

df_listing = pd.read_csv(url_listing)
df_listing

df_directory = pd.read_csv(url_directory)
df_directory


def generate_html_table(df, *, first_name, last_name, counter_unique_dropdown):
    """Create an HTML table by fetching data based on first and last name."""
    if pd.isna(first_name) or pd.isna(last_name):
        return ""

    row = df.query(f"Prénom == '{first_name}' and Nom == '{last_name}'").iloc[0]
    template = '<div class="dropdown">'
    template += (
        '<button class="btn btn-link dropdown-toggle" type="button" '
        f'id="contactDropdown{counter_unique_dropdown}" data-bs-toggle="dropdown" aria-expanded="false">'
        f'{row["Prénom"]} {row["Nom"]}</button>'
    )
    template += (
        f'<div class="dropdown-menu p-3" aria-labelledby="contactDropdown{counter_unique_dropdown}">'
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

    It contains only the road race information.
    """
    counter_unique_dropdown = 0
    html_table = (
        '<div class="table-responsive"><table class="table" id="clubTable"><thead><tr><th>Club</th><th>Président du Club</th>'
        '<th>Responsable Cyclisme</th><th>Responsable Cyclotourisme</th></tr></thead>'
        '<tbody>'
    )
    for town, sub_df in df_listing.groupby("Ville", sort=True):
        # FIXME: we can eventually revert the colspan but we need to generate a pure HTML
        # table
        # markdown_table += f"| **{town}** {{: colspan='4'}} |\n"
        for row_id, row in sub_df.iterrows():
            html_table += f'<tr><td>{row["Nom du club"]}</td>'
            html_table += f'<td>{generate_html_table(df_directory, first_name=row["Président Prénom"], last_name=row["Président Nom"], counter_unique_dropdown=counter_unique_dropdown)}</td>'
            counter_unique_dropdown += 1
            html_table += f'<td>{generate_html_table(df_directory, first_name=row["Responsable cyclisme Prénom"], last_name=row["Responsable cyclisme Nom"], counter_unique_dropdown=counter_unique_dropdown)}</td>'
            counter_unique_dropdown += 1
            html_table += f'<td>{generate_html_table(df_directory, first_name=row["Responsable cyclotouriste Prénom"], last_name=row["Responsable cyclotouriste Nom"], counter_unique_dropdown=counter_unique_dropdown)}</td>'
            counter_unique_dropdown += 1
            html_table += "</tr>\n"
    html_table += "</tbody></table></div>"
    return html_table


# def generate_mountain_bike_listing(df_listing, df_directory):
#     """Create the second table with the mountain bike information."""
#     index_only_mountain_bike = df_listing["Correspondant VTT Nom"].dropna().index
#     df_mountain_bike = df_listing.loc[index_only_mountain_bike]

#     for town, sub_df in df_mountain_bike.groupby("Ville", sort=True):
#         # FIXME: we can eventually revert the colspan but we need to generate a pure HTML
#         # table
#         # markdown_table += f"| **{town}** {{: colspan='4'}} |\n"
#         for row_id, row in sub_df.iterrows():
#             markdown_table += f"| {row["Nom du club"]} |"
#             markdown_table += f"{generate_html_table(df_directory, first_name=row["Président Prénom"], last_name=row["Président Nom"])}|"
#             markdown_table += f"{generate_html_table(df_directory, first_name=row["Responsable cyclisme Prénom"], last_name=row["Responsable cyclisme Nom"])}|"
#             markdown_table += f"{generate_html_table(df_directory, first_name=row["Responsable cyclotouriste Prénom"], last_name=row["Responsable cyclotouriste Nom"])}|"
#             markdown_table += "\n"
#     return markdown_table


# def generate_kids_listing(df_listing, df_directory):
#     """Create the third table with the kids information."""
#     index_only_kids = df_listing["Correspondant vélos enfants Nom"].dropna().index
#     df_kids = df_listing.loc[index_only_kids]

#     for town, sub_df in df_kids.groupby("Ville", sort=True):
#         # FIXME: we can eventually revert the colspan but we need to generate a pure HTML
#         # table
#         # markdown_table += f"| **{town}** {{: colspan='4'}} |\n"
#         for row_id, row in sub_df.iterrows():
#             markdown_table += f"| {row["Nom du club"]} |"
#             markdown_table += f"{generate_html_table(df_directory, first_name=row["Président Prénom"], last_name=row["Président Nom"])}|"
#             markdown_table += f"{generate_html_table(df_directory, first_name=row["Responsable cyclisme Prénom"], last_name=row["Responsable cyclisme Nom"])}|"
#             markdown_table += f"{generate_html_table(df_directory, first_name=row["Responsable cyclotouriste Prénom"], last_name=row["Responsable cyclotouriste Nom"])}|"
#             markdown_table += "\n"
#     return markdown_table


def generate_markdown_webpage(filename, *, df_listing, df_directory):
    with open(filename, "w") as f:
        metadata = """---
title: Liste des clubs FSGT 71
url: clubs/index.html
save_as: clubs/index.html
template: page
---

"""
        title = '## <i class="fas fa-bicycle"></i> Liste des clubs\n\n'

        listing_clubs_roads = "### Correspondants clubs & routes\n\n"
        # add a search bar
        listing_clubs_roads += """<div class="mb-3">
    <input type="text"
           class="form-control"
           id="clubSearch"
           placeholder="Rechercher un club ou un contact..."
           aria-label="Rechercher un club">
</div>
"""
        listing_clubs_roads += generate_club_listing(df_listing, df_directory)
        listing_clubs_roads += "\n\n"

        listing_clubs_mountain_bike = "### Correspondants VTT\n\n"

        listing_clubs_kids = "### Correspondants vélos enfants\n\n"

        f.write(
            metadata
            + title
            + listing_clubs_roads
            + listing_clubs_mountain_bike
            + listing_clubs_kids
        )


# %%
if __name__ == "__main__":
    generate_markdown_webpage(
        "content/pages/clubs.md", df_listing=df_listing, df_directory=df_directory
    )
