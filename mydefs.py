"""

This program contains helper functions for mobility.ipynb (visualization of findings).
There are two main groups of helper functions:
    Query from dataframes (specific country, date, continent, etc)
    Plot findings with matplotlib.

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from pandas.plotting import register_matplotlib_converters

country_continent_path = r"data-in\countryContinent.csv"
filename = r"data-in\Global_Mobility_Report.csv"

def get_df(filename):    
    df = pd.read_csv(filename)
    rename_columns = {"country_region_code": "country_code",
                      "country_region": "country",
                      "retail_and_recreation_percent_change_from_baseline": "retail_and_recreation",
                      "grocery_and_pharmacy_percent_change_from_baseline": "grocery_and_pharmacy",
                      "parks_percent_change_from_baseline": "parks",
                      "transit_stations_percent_change_from_baseline": "transit_stations",
                      "workplaces_percent_change_from_baseline": "workplaces",
                      "residential_percent_change_from_baseline": "residential"}
    df = df.rename(columns=rename_columns)

    df["outdoor"] = (df["retail_and_recreation"] + df["grocery_and_pharmacy"] + df["parks"] + df["transit_stations"] + df["workplaces"])/5

    df_country = df[df["sub_region_1"].isnull()]  # get only countries data
    df_country["country_code"].fillna("NA", inplace=True) #fix country code for Namibia

    to_drop_cols = ["sub_region_1", "sub_region_2"]
    df_country = df_country.drop(to_drop_cols, axis=1)

    # #drop countries with null values
    df_country_na = df_country[pd.isnull(df_country).any(axis=1)]
    countries_to_drop = df_country_na["country"].unique().tolist()

    #drop countries not in nCov time series file
    more_countries_to_drop = ["Côte d'Ivoire", "Puerto Rico"]
    # for c in ["Côte d'Ivoire", "Puerto Rico"]:
    #     countries_to_drop.append(c)

    df_country = df_country[~df_country["country"].isin(countries_to_drop)]
    df_country = df_country[~df_country["country"].isin(more_countries_to_drop)]

 
    # #convert date
    df_country["date"] = pd.to_datetime(df_country["date"])

    country_continent = pd.read_csv(country_continent_path, encoding="latin-1")
    country_continent["code_2"] = np.where(country_continent["country"] == "Namibia", "NA", country_continent["code_2"])

    map_continent1 = country_continent[["continent", "code_2"]]
    df_country = df_country.merge(map_continent1, left_on="country_code", right_on="code_2", how="left")
    df_country = df_country.sort_values(["country", "date"]).reset_index(drop=True)

    southeast_asia = ["Brunei", "Myanmar", "Cambodia", "Timor-Leste", "Indonesia", "Taiwan",
                      "Laos", "Malaysia", "Philippines", "Singapore", "Thailand", "Vietnam"]

    df_sea = df_country[df_country["country"].isin(southeast_asia)].drop(["continent", "country_code", "code_2"], axis=1)
    df_country = df_country.drop(["continent", "country_code", "code_2"], axis=1)
    return df_country, df_sea


def get_specific_dates(df, date_ymd):
    date_ymd = pd.to_datetime(date_ymd)
    df = df[df["date"] == date_ymd].reset_index(drop=True).set_index("country")
    df = df[["retail_and_recreation", "grocery_and_pharmacy", "parks",
             "transit_stations", "workplaces", "outdoor", "residential"]]
    return df


### Query EXTREMES ###

def top_decrease(df, category):
    df_group = df.groupby("country")[f"{category}"].min().reset_index()

    df_cropped = df.merge(df_group, left_on="country", right_on="country")
    df_cropped = df_cropped[df_cropped[f"{category}_x"]
                            == df_cropped[f"{category}_y"]]
    df_cropped = df_cropped[["country", "date", f"{category}_x"]]
    df_cropped.columns = ["country", "date", f"{category}"]
    df_cropped.sort_values(f"{category}", ascending=True, inplace=True)
    df_cropped.drop_duplicates("country", inplace=True)

    df_groupby_day = df_cropped.groupby("date")[f'{category}'].agg(["count", "sum", "mean"]).sort_values("count", ascending=False)

    return df_cropped, df_groupby_day


def top_increase(df, category):
    df_group = df.groupby("country")[f"{category}"].max().reset_index()

    df_cropped = df.merge(df_group, left_on="country", right_on="country")
    df_cropped = df_cropped[df_cropped[f"{category}_x"]
                            == df_cropped[f"{category}_y"]]
    df_cropped = df_cropped[["country", "date", f"{category}_x"]]
    df_cropped.columns = ["country", "date", f"{category}"]
    df_cropped.sort_values(f"{category}", ascending=False, inplace=True)
    df_cropped.drop_duplicates("country", inplace=True)

    df_groupby_day = df_cropped.groupby(
        "date")[f'{category}'].agg(["count", "sum", "mean"]).sort_values("count", ascending=False)

    return df_cropped, df_groupby_day


def extreme_date(extreme_df):
    extreme_date = extreme_df.groupby("date")["country"].count().sort_values(ascending=False)[:10]
    extreme_date = pd.DataFrame(extreme_date)
    extreme_date.columns = ["count"]
    count_sum = sum(extreme_date["count"])
    extreme_date["%"] = extreme_date["count"]/count_sum*100
    return extreme_date


### PLOTS ###


def plot_mobility(filename, date, action):

    def get_df(filename):
        df = pd.read_csv(filename)
        rename_columns = {"country_region_code": "country_code",
                          "country_region": "country",
                          "retail_and_recreation_percent_change_from_baseline": "retail_and_recreation",
                          "grocery_and_pharmacy_percent_change_from_baseline": "grocery_and_pharmacy",
                          "parks_percent_change_from_baseline": "parks",
                          "transit_stations_percent_change_from_baseline": "transit_stations",
                          "workplaces_percent_change_from_baseline": "workplaces",
                          "residential_percent_change_from_baseline": "residential"}
        df = df.rename(columns=rename_columns)
        df["outdoor"] = (df["retail_and_recreation"] + df["grocery_and_pharmacy"] + df["parks"] + df["transit_stations"] + df["workplaces"])/5
        df_country = df[df["sub_region_1"].isnull()]
        df_country["country_code"].fillna("NA", inplace=True)
        to_drop_cols = ["sub_region_1", "sub_region_2"]
        df_country = df_country.drop(to_drop_cols, axis=1)

        df_country_na = df_country[pd.isnull(df_country).any(axis=1)]
        countries_to_drop = df_country_na["country"].unique()
        more_to_drop = ["Côte d'Ivoire", "Puerto Rico"]
            
        df_country = df_country[~df_country["country"].isin(countries_to_drop)]
        df_country = df_country[~df_country["country"].isin(more_to_drop)]

        df_country["date"] = pd.to_datetime(df_country["date"])

        country_continent = pd.read_csv(country_continent_path, encoding="latin-1")
        country_continent["code_2"] = np.where(country_continent["country"] == "Namibia", "NA", country_continent["code_2"])

        map_continent1 = country_continent[["continent", "code_2"]]
        df_country = df_country.merge(
            map_continent1, left_on="country_code", right_on="code_2", how="left")

        southeast_asia = ["Brunei", "Myanmar", "Cambodia", "Timor-Leste", "Indonesia",
                          "Laos", "Malaysia", "Philippines", "Singapore", "Thailand", "Vietnam"]

        df_asia = df_country[df_country["continent"].isin(["Asia", "Oceania"])].drop(
            ["continent", "country_code", "code_2"], axis=1)
        df_africa = df_country[df_country["continent"].isin(["Africa"])].drop(
            ["continent", "country_code", "code_2"], axis=1)
        df_america = df_country[df_country["continent"].isin(["Americas"])].drop(
            ["continent", "country_code", "code_2"], axis=1)
        df_europe = df_country[df_country["continent"].isin(["Europe"])].drop(
            ["continent", "country_code", "code_2"], axis=1)
        df_sea = df_country[df_country["country"].isin(southeast_asia)].drop(
            ["continent", "country_code", "code_2"], axis=1)
        df_country = df_country.drop(
            ["continent", "country_code", "code_2"], axis=1)

        return df_country, df_asia, df_africa, df_america, df_europe, df_sea

    def get_specific_dates(df, date_ymd):
        date_ymd = pd.to_datetime(date_ymd)
        df = df[df["date"] == date_ymd].reset_index(drop=True).set_index("country")
        df = df[["retail_and_recreation", "grocery_and_pharmacy", "parks",
                 "transit_stations", "workplaces", "outdoor", "residential"]]
        return df

    def dot_plot_df(df_list, date, action):
        rows = 1
        columns = len(df_list[0].columns)
        fig, axes = plt.subplots(nrows=rows, ncols=columns, sharey=True, sharex=True)
        to_continent = pd.read_csv(r"C:\programming\mobility\data-in\countryContinent.csv", encoding="latin-1")
        to_continent = to_continent[["country", "continent"]]
        to_continent["continent"] = np.where(to_continent["continent"].isin(["Asia", "Oceania"]), "Asia & Oceania", to_continent["continent"])

        color_list = ["r", "b", "g", "y", "grey", "purple", "orange"]
        for i in range(0, columns):
            axes[i].axhline(0, color='black', linewidth=1.5)
            axes[i].set_ylim([-100, 00])
            line_list = []
            for j in range(len(df_list)):
                line = axes[i].plot(len(df_list[j]) * [j], df_list[j].iloc[:, i], "o", c=color_list[j], alpha=0.3, label=(to_continent.loc[to_continent["country"]==df_list[j].index[0], ["continent"]].iloc[0].values[0]))
                line_list.append(line)
            axes[i].set_xlabel(f"{df_list[0].columns[i]}")

            axes[i].grid(alpha=0.7)
            plt.xticks([])
            # plt.legend(bbox_to_anchor=(1.05, 1),loc='upper left', borderaxespad=0.)
            plt.suptitle(f"{date}")

        axes[columns-1].legend(bbox_to_anchor=(1.05, 1),loc='upper left', borderaxespad=0.)
        fig.set_size_inches(18, 10, forward=True)

        if action == "save":
            plt.savefig(f"data-out/pngs/{date}.png")
        elif action == "show":
            plt.show()


    df_global, df_asia, df_africa, df_america, df_europe, df_sea = get_df(
        filename)
    asia = get_specific_dates(df_asia, date)
    africa = get_specific_dates(df_africa, date)
    america = get_specific_dates(df_america, date)
    europe = get_specific_dates(df_europe, date)

    df_list = asia, africa, america, europe

    return dot_plot_df(df_list, date, action)


def save_all_mobility_plot():
    df_global = get_df(filename)[0] 
    date_list = df_global["date"].unique()

    for date in date_list:
        date = str(date)[:10]
        plot_mobility(filename, date, action="save")
        print(f"Date {date} done")


# save_all_mobility_plot()

def plot_extremes(x, y, d):
    fig, ax = plt.subplots(figsize=(14,8))
    plt.bar(x, y, alpha=0.5)
    for i, v in enumerate(y):
        ax.text(i, v-2, v, horizontalalignment="center")
    ax.set_yticklabels([])
    x_label = [f"{c}\n({str(d)[5:10]})" for c, d in zip(x, d)]
    ax.set_xticklabels(x_label)
    plt.show()

# def plot_mnc(country_name, special_col):
#     register_matplotlib_converters()
#     country_df = df_country[df_country["country"]==country_name]
    
#     def get_new_case(df):
#         l_new = df.loc[country_name].values.tolist()
#         new = [l_new[0]]
#         for i in range(1, len(l_new)):
#             new.append(l_new[i]-l_new[i-1])
#         return new
#     new_case = get_new_case(cases_synced_df)
#     new_death = get_new_case(death_synced_df)

#     fig, ax0 = plt.subplots(figsize=(12,8))
#     for col in country_df.columns[-2:]:
#         ax0.plot(country_df["date"], country_df[[col]], label=f"{col}", linewidth=3)

#     if special_col == 0:
#         pass
#     elif special_col == 1:
#         for col in country_df.columns[2:-2]:
#             ax0.plot(country_df["date"], country_df[[col]], label=f"{col}", alpha=0.9, linewidth=0.7)
#     else:
#         for col in special_col:
#             ax0.plot(country_df["date"], country_df[col], label=col, alpha=0.9, linewidth=0.7)
    
#     ax0.set_ylim([-100, 100])
#     ax0.axhline(0, color="grey", linewidth=1, alpha=0.8)
#     ax0.legend(loc="upper left")

#     ax1 = ax0.twinx()
#     plt.bar(country_df["date"], new_case, label="daily new CASE", alpha=0.2)
#     plt.bar(country_df["date"], new_death, label="daily new DEATH", color="grey", alpha=0.5)

# #     ax1.yaxis.set_ticks(np.arange(min(new), max(new), 10))
#     plt.title(f"Mobility vs Daily New Case in: {country_name.upper()}")
#     plt.legend(loc="upper right")
#     plt.grid()
#     plt.show()
