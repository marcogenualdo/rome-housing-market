# Analysis of the Rome housing market

This project is an attempt to carry out the full datascience workflow:

- The data was collected using the webscraper in `scraping` from the site [immobiliare.it](https://www.immobiliare.it/), which collected 41900 house listings and recorded 13 variables. The data is not available in this repository to keep it lightweight, but I'll happily send it if you contact me.

- In the Jupyter Notebook `data_analysis.ipynb` a first conspicuous section is dedicated to data cleaning and exploration.

- We try and understand the distribution of each variable, considering outliers and invalid entries.

- We then explore the relationships between the variables, trying to understand which ones influence the price the most. Special attention is resered to location (respecting the famous real estate motto), and an interactive geographical heatmap is provided at the end of the notebook.