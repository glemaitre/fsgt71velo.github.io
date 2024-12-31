# %%
import locale

import pandas as pd

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
COLOR_TYPE_OF_RACE = {
    "Route": "race-type-route",
    "Championnat": "race-type-championship",
    "Contre-la-montre": "race-type-contre-la-montre",
    "Brevet et randonnée": "race-type-brevet-et-randonnee",
    "Cyclo-cross": "race-type-cyclo-cross",
    "Autres": "race-type-other",
}
COLOR_CIRCUIT_LENGTH = {
    "Circuit < 5km": "race-type-circuit-lt-5km",
    "Circuit >= 5 km": "race-type-circuit-gte-5km",
}
COLOR_DURATION_RACE = {
    "Demi-journée": "race-type-demi-journee",
    "Journée complète": "race-type-journee-complete",
}

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
sheet_id = "1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M"
sheet_calendar = "calendar"
url_calendar = (
    f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/"
    f"tq?tqx=out:csv&sheet={sheet_calendar}"
)
df_calendar = pd.read_csv(url_calendar, dayfirst=True, parse_dates=["Date"])
df_calendar


def generate_html_table(df_calendar):
    # Filter rows that have at least one result
    mask = df_calendar["Résultats TC"].notna() | df_calendar["Résultats école"].notna()
    df_calendar = df_calendar[mask].copy()

    # If no results at all, return empty table structure
    if len(df_calendar) == 0:
        return (
            '<table class="table" id="calendarTable"><thead><tr>'
            "<th>Dates</th><th>Courses</th><th>Club</th><th>Résultats</th>"
            "</tr></thead><tbody></tbody></table>"
        )

    df_calendar["Month"] = df_calendar["Date"].dt.month_name().map(MONTH_TRANSLATION)

    html_table = (
        '<table class="table" id="calendarTable"><thead><tr>'
        "<th>Dates</th><th>Courses</th><th>Club</th><th>Résultats</th>"
        "</tr></thead><tbody>"
    )

    # Only process months that have races with results
    for month, df_month in df_calendar.groupby("Month", sort=False):
        if (
            len(df_month) > 0
        ):  # This check is technically redundant now but kept for clarity
            html_table += f"<tr><td colspan='4' class='text-center'><strong>{month.upper()}</strong></td></tr>"
            for _, row in df_month.iterrows():
                html_table += "<tr>"
                # Date column
                html_table += f"<td>{row['Date'].strftime('%a %d %b').title()}</td>"

                # Course column (simplified, no poster link)
                html_table += f"<td>{row['Course']}</td>"

                # Club column
                html_table += f"<td>{row['Club'] if pd.notna(row['Club']) else ''}</td>"

                # Results column
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
                html_table += f'<td><div class="d-flex flex-column flex-md-row">{" ".join(results)}</div></td>'

                html_table += "</tr>"
    html_table += "</tbody></table>"
    return html_table


# %%


def generate_markdown_webpage(filename):
    with open(filename, "w") as f:
        metadata = """---
title: Résultats des courses FSGT 71
url: resultats/index.html
save_as: resultats/index.html
template: page
---

"""
        title = '## <i class="fas fa-trophy"></i> Résultats des courses 2025\n\n'

        # Search bar
        results_table = """<div class="mb-3">
    <input type="text"
           class="form-control"
           id="resultsSearch"
           placeholder="Rechercher un résultat..."
           aria-label="Rechercher un résultat">
</div>
"""
        results_table += generate_html_table(df_calendar)

        f.write(metadata + title + results_table)


# %%
if __name__ == "__main__":
    generate_markdown_webpage("content/pages/results.md")

# %%
