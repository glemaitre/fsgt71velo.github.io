# Site internet de la FSGT 71

## Prérequis

Pour pouvoir générer le site web localement, vous avez uniquement besoin d'installer
`pixi`. Vous pouvez vous référer à la documentation officielle pour l'installer :
[https://pixi.sh/latest/#installation](https://pixi.sh/latest/#installation).

## Générer le site web localement

Vous pouvez générer localement le site web en utilisant `pixi` :

```shell
pixi run build
```

Si vous souhaitez également lancer un serveur local, vous pouvez directement exécuter :

```shell
pixi run preview
```

et consulter le site web à l'adresse [http://localhost:8000](http://localhost:8000).

## Détails concernant certains fichiers internes

Certaines pages web du site sont générées automatiquement en exécutant des scripts
Python. Généralement, les pages web obtiennent les données nécessaires à partir de
différents Google Sheets. Cela signifie que vous devez modifier le contenu de la feuille
de calcul puis exécuter le script pour générer la page web (c'est-à-dire exécuter `pixi
run build`).

### Génération du calendrier

Le script `scripts/generate_calendar.py` génère la page du calendrier basée sur le
Google Sheet suivant :

https://docs.google.com/spreadsheets/d/1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M/edit?usp=sharing

### Génération de la liste des clubs

Le script `scripts/generate_clubs.py` génère la page de la liste des clubs basée sur le
Google Sheet suivant :

https://docs.google.com/spreadsheets/d/1ocHqS1lCjGVwKTd_ES_L06eOFDN90Jd_Kap3OtZhgVM/edit?gid=0#gid=0

### Génération de la page contenant les rapports des commissions

Les rapports des commissions sont stockés dans un dossier Google Drive dédié avec
un accès en lecture restreint. Le script `scripts/generate_report.py` générera la
page contenant les rapports des commissions. L'intégration continue dispose d'un
accès en lecture seule au dossier Google Drive pour générer la page automatiquement.

Les fichiers dans ces dossiers doivent être nommés selon le format suivant
`JJ_MM_AAAA.pdf` et placés dans le dossier `FSGT 71/Rapport Commission/AAAA`.

## Déclencher une construction du site web sur GitHub Actions

Le site web est automatiquement construit sur GitHub Actions lorsqu'un push est effectué
sur la branche `main`.

Alternativement, vous pouvez déclencher une construction manuellement en allant sur le
[workflow de déploiement](https://github.com/glemaitre/fsgt71velo.github.io/actions/workflows/deploy.yml)
et en cliquant sur le bouton "Run workflow" comme montré ci-dessous :

![Exécuter le workflow](.github/workflows/run_workflow.png)
