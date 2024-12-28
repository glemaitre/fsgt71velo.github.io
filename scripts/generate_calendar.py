# %%
import pandas as pd
import locale

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
    df_calendar["Month"] = df_calendar["Date"].dt.month_name()
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
            f'<tr>'
            f'<td colspan="4" class="text-center"><strong>{month.upper()}</strong></td>'
            "</tr>"
        )
        for _, row in df_month.iterrows():
            html_table += f"<tr><td>{row['Date'].strftime('%a %d %b %Y').title()}</td>"
            html_table += f"<td>{row['Course']}</td>"
            html_table += f"<td>{row['Catégories']}</td>"
            html_table += f"<td>{row['Clubs']}</td></tr>"
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

        # add a search bar
        calendar_table = """<div class="mb-3">
    <input type="text"
           class="form-control"
           id="calendarSearch"
           placeholder="Rechercher un événement..."
           aria-label="Rechercher un événement">
</div>
"""
        calendar_table += generate_html_table(df_calendar)

        f.write(metadata + title + calendar_table)


# %%
if __name__ == "__main__":
    generate_markdown_webpage("content/pages/calendar.md")

# %%
