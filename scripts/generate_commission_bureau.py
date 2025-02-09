import pandas as pd

SHEET_ID = "1AnPafo45pd15SD7v3szeC4wgSXRBKJ1DYzVk3UfTgFI"
SHEET_NAME = "Commission"
URL_SHEET = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
    f"tq?tqx=out:csv&sheet={SHEET_NAME}"
)


def generate_contact_info(row):
    """Generate the HTML contact info table for a person.

    Parameters
    ----------
    row : pd.Series
        Row from the dataframe containing contact information.

    Returns
    -------
    str
        HTML formatted contact information.
    """
    template = '<table class="contact-info-table" border="0">'

    if not pd.isna(row["Addresse"]):
        template += (
            "<tr>"
            '<td><i class="fas fa-map-marker-alt"></i></td>'
            f'<td>{row["Addresse"].replace("\n", "<br>")}</td>'
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
            '<td><i class="fas fa-phone"></i></td>'
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
    template += "</table>"
    return template


def generate_bureau_listing(df):
    """Generate the markdown table for the bureau listing.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the bureau data.

    Returns
    -------
    str
        Markdown formatted table.
    """
    table = "| Nom | Coordonnées | Responsabilités |\n"
    table += "|-----|-------------|------------------|\n"

    for _, row in df.iterrows():
        full_name = f"{row['Prénom']} {row['Nom']}"
        contact_info = generate_contact_info(row)
        responsibilities = row["Responsabilité"].replace("\n", "<br>• ").strip()
        if responsibilities:
            responsibilities = "• " + responsibilities

        table += f"| {full_name} | {contact_info} | {responsibilities} |\n"

    return table


def generate_markdown_webpage(filename):
    """Generate the markdown webpage for the bureau listing.

    Parameters
    ----------
    filename : str
        The filename to write the markdown webpage to.
    """
    df = pd.read_csv(URL_SHEET)

    with open(filename, "w") as f:
        metadata = """---
title: Commission Cycliste FSGT 71
url: bureau/index.html
save_as: bureau/index.html
template: page
---

## <i class="fas fa-users"></i> Commission Cycliste FSGT 71 2024-2025

"""
        table = generate_bureau_listing(df)
        f.write(metadata + table)


if __name__ == "__main__":
    generate_markdown_webpage("content/pages/bureau.md")
