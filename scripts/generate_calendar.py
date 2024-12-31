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

SHEET_ID = "1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M"
SHEET_CALENDAR = "calendar"
URL_CALENDAR = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
    f"tq?tqx=out:csv&sheet={SHEET_CALENDAR}"
)


def generate_html_table(df_calendar):
    """Generate the HTML table for the calendar.

    Parameters
    ----------
    df_calendar : pd.DataFrame
        The dataframe containing the calendar data.

    Returns
    -------
    str
        The HTML table for the calendar.
    """
    # The `locale` in `month_name` cannot be set when using the GitHub Actions runner
    # So we manually translate the month names
    df_calendar["Month"] = df_calendar["Date"].dt.month_name().map(MONTH_TRANSLATION)
    html_table = (
        '<table class="table" id="calendarTable"><thead><tr>'
        "<th>Dates</th>"
        "<th>Courses</th>"
        "<th>Catégories</th>"
        "<th>Club</th>"
        "</tr></thead>"
        "<tbody>"
    )
    for month, df_month in df_calendar.groupby("Month", sort=False):
        html_table += (
            f"<tr>"
            f'<td colspan="4" class="text-center"><strong>{month.upper()}</strong></td>'
            "</tr>"
        )
        for _, row in df_month.iterrows():
            html_table += "<tr>"
            class_td_duration = COLOR_DURATION_RACE.get(row["Durée organisation"], "")
            class_attr = f" class='{class_td_duration}'" if class_td_duration else ""
            html_table += (
                f"<td{class_attr}>"
                f"{row['Date'].strftime('%a %d %b').title()}"
                "</td>"
            )
            class_td_type_of_race = COLOR_TYPE_OF_RACE.get(row["Type de course"])
            course_content = row["Course"]
            if pd.notna(row["Affiche"]):
                course_content = (
                    f'<a href="{row["Affiche"]}" target="_blank">{course_content}</a>'
                )
            html_table += f"<td class='{class_td_type_of_race}'>{course_content}</td>"
            class_td_circuit_length = COLOR_CIRCUIT_LENGTH.get(
                row["Longeur circuit"],
            )
            html_table += (
                f"<td class='{class_td_circuit_length}'>"
                f"{row['Catégories'] if pd.notna(row['Catégories']) else ''}"
                "</td>"
            )
            html_table += f"<td>{row['Club'] if pd.notna(row['Club']) else ''}</td>"
            html_table += "</tr>"
    html_table += "</tbody></table>"
    return html_table


def generate_markdown_webpage(filename):
    """Generate the markdown webpage for the calendar.

    Parameters
    ----------
    filename: str
        The filename to write the markdown webpage to.
    """
    with open(filename, "w") as f:
        metadata = """---
title: Calendrier des événements FSGT 71
url: calendrier/index.html
save_as: calendrier/index.html
template: page
---

"""
        title = (
            '## <i class="fas fa-calendar-alt"></i> Calendrier des événements 2025\n\n'
        )

        # Search bar
        calendar_table = """<div class="mb-3">
    <input type="text"
           class="form-control"
           id="calendarSearch"
           placeholder="Rechercher un événement..."
           aria-label="Rechercher un événement">
</div>
"""
        # Add legend section
        calendar_table += """<div class="row mb-3">
    <div class="col-md-4">
        <div class="alert alert-default border small">
            <strong>Durée de l'épreuve :</strong>
            <ul class="list-unstyled mb-0">
"""
        for duration, color in COLOR_DURATION_RACE.items():
            calendar_table += f"""
                <li><span class="badge {color}">&nbsp;</span> {duration}</li>
"""
        calendar_table += """
            </ul>
        </div>
    </div>
    <div class="col-md-4">
        <div class="alert alert-default border small">
            <strong>Type de course :</strong>
            <ul class="list-unstyled mb-0">
"""
        for race_type, color in COLOR_TYPE_OF_RACE.items():
            calendar_table += f"""
                <li><span class="badge {color}">&nbsp;</span> {race_type}</li>
"""
        calendar_table += """
            </ul>
        </div>
    </div>
    <div class="col-md-4">
        <div class="alert alert-default border small">
            <strong>Longueur du circuit :</strong>
            <ul class="list-unstyled mb-0">
"""
        for circuit_length, color in COLOR_CIRCUIT_LENGTH.items():
            calendar_table += f"""
                <li><span class="badge {color}">&nbsp;</span> {circuit_length}</li>
"""
        calendar_table += """
            </ul>
        </div>
    </div>
</div>
"""
        df_calendar = pd.read_csv(URL_CALENDAR, dayfirst=True, parse_dates=["Date"])
        calendar_table += generate_html_table(df_calendar)

        f.write(metadata + title + calendar_table)


if __name__ == "__main__":
    """Entry point for the pixi task."""
    generate_markdown_webpage("content/pages/calendar.md")
