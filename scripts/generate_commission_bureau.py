import os

import pandas as pd

SHEET_ID = "11zy08a30aMAZPkxHSWJ0TxMI6Su9LFzi1RdNCceeXuQ"
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
        address = row["Addresse"].replace("\n", "<br>")
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


def generate_printable_person_info_html(row):
    """Create an HTML formatted string of a person's contact information.

    Parameters
    ----------
    row : pd.Series
        Row from the dataframe containing contact information.

    Returns
    -------
    str
        The HTML formatted contact information string.
    """
    info = ""
    if not pd.isna(row["Addresse"]):
        address = row["Addresse"].replace(chr(10), "<br>")
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


def generate_printable_bureau_html(df):
    """Create a printable HTML table of the bureau listing.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the bureau data.

    Returns
    -------
    str
        The HTML document formatted for printing.
    """
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Commission Cycliste FSGT 71</title>
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
            background-color: #f8f9fa;
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
            * {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
        }
    </style>
</head>
<body>
    <h1>Commission Cycliste FSGT 71</h1>
    <table>
        <thead>
            <tr>
                <th style="width: 20%;">Nom</th>
                <th style="width: 40%;">Coordonnées</th>
                <th style="width: 40%;">Responsabilités</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df.iterrows():
        full_name = f"{row['Prénom']} {row['Nom']}"
        contact_info = generate_printable_person_info_html(row)
        responsibilities = row["Responsabilité"].replace("\n", "<br>• ")
        if responsibilities:
            responsibilities = "• " + responsibilities

        html += f"""
            <tr>
                <td><strong>{full_name}</strong></td>
                <td>{contact_info}</td>
                <td>{responsibilities}</td>
            </tr>"""

    html += """
        </tbody>
    </table>
</body>
</html>
    """
    return html


def generate_markdown_webpage(filename):
    """Generate the markdown webpage for the bureau listing.

    Parameters
    ----------
    filename : str
        The filename to write the markdown webpage to.

    Returns
    -------
    str
        The markdown content for the webpage.
    """
    df = pd.read_csv(URL_SHEET)

    metadata = f"""---
title: Commission Cycliste FSGT 71
url: bureau/index.html
save_as: bureau/index.html
template: page
---

## <i class="fas fa-users fas-title"></i> Commission Cycliste FSGT 71 {pd.Timestamp.today().year}

<div class="h2-spacer"></div>

"""
    table = generate_bureau_listing(df)
    return metadata + table, df


if __name__ == "__main__":
    markdown_content, df = generate_markdown_webpage("content/pages/bureau.md")

    # Write the markdown file
    with open("content/pages/bureau.md", "w") as f:
        f.write(markdown_content)

    # Generate and write the printable HTML version
    html_content = generate_printable_bureau_html(df)
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/bureau_printable.html", "w", encoding="utf-8") as f:
        f.write(html_content)
