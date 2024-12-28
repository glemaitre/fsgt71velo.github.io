# Site internet de la FSGT 71

## Prerequisites

To be able to generate the website locally, you only need to install `pixi`.
You can refer to the official documentation to install it:
[https://pixi.sh/latest/#installation](https://pixi.sh/latest/#installation).

## Generate the website locally

You can generate locally the website using `pixi`:

```shell
pixi run build
```

In case you want also to launch a local server, you can directly run:

```sell
pixi run preview
```

and check the website at [http://localhost:8000](http://localhost:8000).

## Details regarding some internal files

Some webpages of the website are generated automatically by running some Python scripts.
Usually, the webpages get the necessary data from different Google Sheets. It means
that you need to change the content of the spreadsheet and then execute the script
to generate the webpage (i.e. run `pixi run build`).

### Calendar generation

The script `scripts/generate_calendar.py` generates the calendar page based on the
following Google Sheet:

https://docs.google.com/spreadsheets/d/1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M/edit?usp=sharing

### Clubs listing generation

The script `scripts/generate_clubs.py` generates the clubs listing page based on the
following Google Sheet:

https://docs.google.com/spreadsheets/d/1ocHqS1lCjGVwKTd_ES_L06eOFDN90Jd_Kap3OtZhgVM/edit?gid=0#gid=0

## Triggering a website build on GitHub Actions

The website is automatically built on GitHub Actions when a push is made on the `main`
branch.

Alternatively, you can trigger a build manually by going to the
[deploy workflow](https://github.com/glemaitre/fsgt71velo.github.io/actions/workflows/deploy.yml)
and clicking on the "Run workflow" button as shown below:

![Run workflow](.github/workflows/run_workflow.png)
