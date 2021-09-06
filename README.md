# Visualization of Community Mobility with Covid-19 confirmed cases and death

As Google published [Community Mobility Reports](https://www.google.com/covid19/mobility/?hl=en-GB) which gives insights into movement trends over time by geography due to COVID-10, I became curious about how countries react to the evolvement of COVID-19 confirmed cases and death in terms of movement patterns, or if they were really affected at all.

This project is my attempt to merge [the Community Mobility dataset (of Google)](https://www.google.com/covid19/mobility/?hl=en-GB) and [the COVID-19 Data Repository (of CSSE at Johns Hopkins University)](https://github.com/CSSEGISandData/COVID-19) and visualize the relationships between these 2 datasets using Python libraries: pandas, matplotlib. My main interest was to look for how Vietnam, Taiwan, and the US moved differently as these are the 3 communities I actually get to live in during different stages of the pandemic. 

The datasets also give interesting insights to 190+ countries rather than just the 3 countries I look into, I took one step further to create interactive charts with [Plotly Dash](https://dash.plotly.com/), so that my friends and families accross the globe could look up the information about the communities they care for.

Period: Jan 22, 2020 - June 4, 2020

-----

## 1. Merging datasets

The processed and merged datasets are located in `dfs` the folder. 

The original 2 datasets provide daily data of movement categories and cases of each country. Continent information is also further added to compare trends accross or within continents.

A glance of what the combined dataframe looks like:
<img src="https://github.com/ptmphuong/mobility/blob/master/demo/for-blog/combined_df.png" width="700">

## 2. Personal finding

My personal findings are presented in the `mobility.ipynb` Jupyter notebooks file in the form of dataframe queries, tables and charts.

Example of findings are which dates have the most extreme changes in movement, or which countries have the most/least change in movement overall.
Possible reasons could be derived from the number of COVID-19 confirmed cases and death. 

<img src="https://github.com/ptmphuong/mobility/blob/master/demo/for-blog/most-extremem-date-white-bg.png" width="700">
<img src="https://github.com/ptmphuong/mobility/blob/master/demo/for-blog/mobility_by_continent(1).png" width="700">
<img src="https://github.com/ptmphuong/mobility/blob/master/demo/for-blog/us_new_case_vs_mobility.png" width="700">

## 3. Further exploring with interactive charts

3 interactives are created using Plotly Dash. Demo of the charts:

a. Weekly mobility trends accross continents

![](https://github.com/ptmphuong/mobility/blob/master/demo/gifs/slider-country.gif)


b. Daily mobility trend and covid-19 cases - COUNTRY LEVEL

![](https://github.com/ptmphuong/mobility/blob/master/demo/gifs/graph3-gif.gif)


c. Daily mobility trend and covid-19 cases - US STATE LEVEL

![](https://github.com/ptmphuong/mobility/blob/master/demo/gifs/slider-us.gif)


To run the charts: 
1. Make sure Python3 is installed.
2. Install [Plotly Dash](https://dash.plotly.com/installation).
3. Run the files: `dateslider.py` (chart a), `dropdown.py` (chart b), `dropdown_us.py` (chart c)



