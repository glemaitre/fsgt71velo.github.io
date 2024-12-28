# %%
import pandas as pd
import locale

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
}
COLOR_CIRCUIT_LENGTH = {
    "Circuit < 5km": "race-type-circuit-lt-5km",
    "Circuit >= 5 km": "race-type-circuit-gte-5km",
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
    # The `locale` in `month_name` cannot be set when using the GitHub Actions runner
    # So we manually translate the month names
    df_calendar["Month"] = df_calendar["Date"].dt.month_name().map(MONTH_TRANSLATION)
    html_table = (
        '<table class="table" id="calendarTable"><thead><tr>'
        "<th>Dates</th>"
        "<th>Courses</th>"
        "<th>Catégories</th>"
        "<th>Clubs</th>"
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
            html_table += f"<tr><td>{row['Date'].strftime('%a %d %b %Y').title()}</td>"
            class_td_type_of_race = COLOR_TYPE_OF_RACE.get(row["Type de course"])
            html_table += f"<td class='{class_td_type_of_race}'>{row['Course']}</td>"
            class_td_circuit_length = COLOR_CIRCUIT_LENGTH.get(
                row["Longeur circuit"],
            )
            html_table += (
                f"<td class='{class_td_circuit_length}'>"
                f"{row['Catégories'] if pd.notna(row['Catégories']) else ''}"
                "</td>"
            )
            html_table += (
                f"<td>{row['Clubs'] if pd.notna(row['Clubs']) else ''}</td></tr>"
            )
    html_table += "</tbody></table>"
    return html_table


# %%


def generate_markdown_webpage(filename):
    with open(filename, "w") as f:
        metadata = """---
title: Calendrier des événements FSGT 71
url: calendrier/index.html
save_as: calendrier/index.html
template: page
---

"""
        title = '## <i class="fas fa-calendar-alt"></i> Calendrier des événements\n\n'

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
    <div class="col-md-6">
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
    <div class="col-md-6">
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
        calendar_table += generate_html_table(df_calendar)

        f.write(metadata + title + calendar_table)


# %%
if __name__ == "__main__":
    generate_markdown_webpage("content/pages/calendar.md")

# %%
