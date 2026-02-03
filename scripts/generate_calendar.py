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

SHEET_ID = "1Nrau-4Qwbp91pQ8fSi7HCf-OsL67-b2JcKIvnimh2F8"
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
    # So we manually translate the month names. Group by year and month for dates
    # that can span into the next year (e.g. 2026 calendar with a few 2027 dates).
    # Sort by Date so that groupby(..., sort=False) iterates in chronological order
    # (January, February, ... December, then next year); sort=True would order
    # by month name alphabetically (e.g. Août before Janvier).
    df_calendar["Year"] = df_calendar["Date"].dt.year
    df_calendar["Month"] = df_calendar["Date"].dt.month_name().map(MONTH_TRANSLATION)
    df_calendar = df_calendar.sort_values("Date")
    html_table = (
        '<table class="table" id="calendarTable"><thead><tr>'
        '<th class="text-center">Dates</th>'
        '<th class="text-center">Courses</th>'
        '<th class="text-center">Catégories</th>'
        '<th class="text-center">Club</th>'
        "</tr></thead>"
        "<tbody>"
    )
    for (year, month), df_month in df_calendar.groupby(["Year", "Month"], sort=False):
        html_table += (
            f"<tr>"
            f'<td colspan="4" class="text-center"><strong>{month.upper()} {year}</strong></td>'
            "</tr>"
        )
        for _, row in df_month.iterrows():
            html_table += "<tr>"
            class_td_duration = COLOR_DURATION_RACE.get(row["Durée organisation"], "")
            class_attr = f" class='{class_td_duration}'" if class_td_duration else ""
            class_to_duration = " " + class_td_duration if class_td_duration else ""
            html_table += (
                f"<td{class_attr} class='text-center{class_to_duration}'>"
                f"{row['Date'].strftime('%a %d %b %Y').title()}"
                "</td>"
            )
            class_td_type_of_race = COLOR_TYPE_OF_RACE.get(row["Type de course"])
            course_content = row["Course"]
            if pd.notna(row["Affiche"]):
                course_content = (
                    f'<a href="{row["Affiche"]}" target="_blank">{course_content}</a>'
                )
            if pd.notna(row["Annulé"]):
                course_content = f"<strong>ANNULÉ : </strong><s>{course_content}</s>"
            html_table += (
                f"<td class='text-center {class_td_type_of_race}'>{course_content}</td>"
            )
            class_td_circuit_length = COLOR_CIRCUIT_LENGTH.get(
                row["Longeur circuit"],
            )
            class_to_circuit_length = (
                " " + class_td_circuit_length if class_td_circuit_length else ""
            )
            html_table += (
                f"<td class='text-center{class_to_circuit_length}'>"
                f"{row['Catégories'] if pd.notna(row['Catégories']) else ''}"
                "</td>"
            )
            club = row["Club"] if pd.notna(row["Club"]) else ""
            html_table += f"<td class='text-center'>{club}</td>"
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
            f'## <i class="fas fa-calendar-alt fas-title"></i> Calendrier des événements '
            f'{pd.Timestamp.today().year}\n\n<div class="h2-spacer"></div>\n\n'
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
        calendar_table += """<div class="mb-3">
    <button class="btn btn-info w-100" type="button" data-bs-toggle="collapse"
    data-bs-target="#legendCollapse" aria-expanded="false"
    aria-controls="legendCollapse">
        <i class="fas fa-info-circle"></i> Guide des codes couleurs des épreuves
        <i class="fas fa-chevron-down"></i>
    </button>
    <div class="collapse" id="legendCollapse">
        <div class="row mt-3">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header text-center">
                        <strong>Durée de l'épreuve</strong>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
"""
        for duration, color in COLOR_DURATION_RACE.items():
            calendar_table += f"""
                            <li><span class="badge {color}">&nbsp;</span> {duration}
                            </li>
"""
        calendar_table += """
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header text-center">
                        <strong>Type de course</strong>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
"""
        for race_type, color in COLOR_TYPE_OF_RACE.items():
            calendar_table += f"""
                            <li><span class="badge {color}">&nbsp;</span> {race_type}
                            </li>
"""
        calendar_table += """
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header text-center">
                        <strong>Longueur du circuit</strong>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
"""
        for circuit_length, color in COLOR_CIRCUIT_LENGTH.items():
            calendar_table += f"""
                            <li><span class="badge {color}">&nbsp;</span>
                            {circuit_length}</li>
"""
        calendar_table += """
                        </ul>
                    </div>
                </div>
            </div>
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
