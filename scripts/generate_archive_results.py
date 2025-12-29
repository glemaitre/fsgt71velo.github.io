import locale

import pandas as pd

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

MONTH_TRANSLATION = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre",
}

# Calendar from 2024 to 2020
SHEETS_ID = {
    "2025": "1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M",
    "2024": "14m1CGSv-_TaQXwQWf-8foIShbc5NdhMppZ8pOD513qY",
    "2023": "1pY9Xb3aYTNTPrzxhAsI43nQceGJYNYdCpqr1oINb2-g",
    "2022": "11UB3aazn4lnCTXpeVnchWmhf0Go5x9yl8dmcbOn_ysg",
    "2021": "10DasdhRIGPElirsxeJmtVo41nO71mAKJ_8P0AqxE0ko",
    "2020": "1hcuMCqaD-Qu6jEAbMgDYx-YOfOtrrA5QSbZij_CQCFY",
}
URL_CALENDAR = (
    "https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
    "tq?tqx=out:csv&sheet=calendar"
)


def generate_html_table(df_calendar):
    """Generate the HTML table for the results.

    Parameters
    ----------
    df_calendar : pd.DataFrame
        The dataframe containing the results data.

    Returns
    -------
    str
        The HTML table for the results.
    """
    # Filter rows that have at least one result
    mask = df_calendar["Résultats TC"].notna() | df_calendar["Résultats école"].notna()
    df_calendar = df_calendar[mask].copy()

    if len(df_calendar) == 0:
        # If no results at all, return empty table structure
        return (
            '<table class="table" id="calendarTable"><thead><tr>'
            "<th>Dates</th>"
            "<th>Courses</th>"
            "<th>Club</th>"
            "<th>Résultats</th>"
            "</tr></thead><tbody></tbody></table>"
        )

    df_calendar["Month"] = df_calendar["Date"].dt.month_name().map(MONTH_TRANSLATION)

    html_table = (
        '<table class="table" id="calendarTable"><thead><tr>'
        "<th>Dates</th>"
        "<th>Courses</th>"
        "<th>Club</th>"
        "<th>Résultats</th>"
        "</tr></thead><tbody>"
    )

    # Only process months that have races with results
    for month, df_month in df_calendar.groupby("Month", sort=False):
        if len(df_month) > 0:
            # This check is technically redundant now but kept for clarity
            html_table += (
                f"<tr><td colspan='4' class='text-center'>"
                f"<strong>{month.upper()}</strong>"
                "</td></tr>"
            )
            for _, row in df_month.iterrows():
                html_table += "<tr>"
                html_table += f"<td>{row['Date'].strftime('%a %d %b').title()}</td>"
                html_table += f"<td>{row['Course']}</td>"
                html_table += f"<td>{row['Club'] if pd.notna(row['Club']) else ''}</td>"

                results = []
                if pd.notna(row["Résultats TC"]):
                    results.append(
                        f'<a href="{row["Résultats TC"]}" target="_blank" '
                        f'class="btn btn-sm btn-outline-primary mb-1 mb-md-0 me-md-2">'
                        f'<i class="fas fa-file-alt me-1"></i>Toutes catégories</a>'
                    )
                if pd.notna(row["Résultats école"]):
                    results.append(
                        f'<a href="{row["Résultats école"]}" target="_blank" '
                        f'class="btn btn-sm btn-outline-primary">'
                        f'<i class="fas fa-child me-1"></i>Écoles de vélo</a>'
                    )
                html_table += (
                    f'<td><div class="d-flex flex-column flex-md-row">'
                    f'{" ".join(results)}</div></td>'
                )

                html_table += "</tr>"
    html_table += "</tbody></table>"
    return html_table


def generate_markdown_webpage(filename, year, sheet_id):
    """Generate the markdown webpage for the results.

    Parameters
    ----------
    filename: str
        The filename to write the markdown webpage to.
    """
    with open(filename, "w") as f:
        metadata = f"""---
title: Résultats des courses FSGT 71 - {year}
url: resultats/{year}.html
save_as: resultats/{year}.html
template: page
---

"""
        title = f'## <i class="fas fa-trophy"></i> Résultats des courses {year}\n\n'

        # Search bar
        results_table = """<div class="mb-3">
    <input type="text"
           class="form-control"
           id="resultsSearch"
           placeholder="Rechercher un résultat..."
           aria-label="Rechercher un résultat">
</div>
"""
        url_calendar = URL_CALENDAR.format(SHEET_ID=sheet_id)
        df_calendar = pd.read_csv(url_calendar, dayfirst=True, parse_dates=["Date"])
        results_table += generate_html_table(df_calendar)

        f.write(metadata + title + results_table)


if __name__ == "__main__":
    """Entry point for the pixi task."""
    for year, sheet_id in SHEETS_ID.items():
        generate_markdown_webpage(f"content/pages/results{year}.md", year, sheet_id)
