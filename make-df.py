import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import random
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)
 
country_continent_path = r"C:\programming\mobility\data-in\countryContinent.csv"
mobility_path = r"C:\programming\mobility\data-in\Global_Mobility_Report.csv"
ncov_confirmed_path = r"C:\programming\mobility\data-in\time_series_covid_19_confirmed.csv"
ncov_death_path = r"C:\programming\mobility\data-in\time_series_covid_19_deaths.csv"
us_ncov_confirmed_path = r"C:\programming\mobility\data-in\time_series_covid_19_confirmed_US.csv"
us_ncov_death_path = r"C:\programming\mobility\data-in\time_series_covid_19_deaths_US.csv"

mob_df = pd.read_csv(mobility_path)
rename_columns = {"country_region_code": "country_code",
                      "country_region": "country",
                      "retail_and_recreation_percent_change_from_baseline": "retail_and_recreation",
                      "grocery_and_pharmacy_percent_change_from_baseline": "grocery_and_pharmacy",
                      "parks_percent_change_from_baseline": "parks",
                      "transit_stations_percent_change_from_baseline": "transit_stations",
                      "workplaces_percent_change_from_baseline": "workplaces",
                      "residential_percent_change_from_baseline": "residential"}
mob_df = mob_df.rename(columns=rename_columns)

def mobility_df():  
    df_country = mob_df[mob_df["sub_region_1"].isnull()]  # get only countries data
    # df_country["outdoor"] = 0
    for i in df_country.index:
        df_country.loc[i, "outdoor"] = (df_country.loc[i, "retail_and_recreation"] + df_country.loc[i, "grocery_and_pharmacy"] + df_country.loc[i, "parks"] + df_country.loc[i, "transit_stations"] + df_country.loc[i, "workplaces"])/5

    # df_country["outdoor"] = (df_country["retail_and_recreation"] + df_country["grocery_and_pharmacy"] + df_country["parks"] + df_country["transit_stations"] + df_country["workplaces"])/5
    df_country["country_code"].fillna("NA", inplace=True) #fix country code for Namibia

    to_drop_cols = ["sub_region_1", "sub_region_2"]
    df_country = df_country.drop(to_drop_cols, axis=1)

    # #drop countries with null values
    df_country_na = df_country[pd.isnull(df_country).any(axis=1)]
    countries_to_drop = df_country_na["country"].unique().tolist()

    #drop countries not in nCov time series file
    more_countries_to_drop = ["Côte d'Ivoire", "Puerto Rico"]
    to_drop = countries_to_drop + more_countries_to_drop
    df_country = df_country[~df_country["country"].isin(to_drop)]

    #convert date
    df_country["date"] = pd.to_datetime(df_country["date"])

    #map continent
    country_continent = pd.read_csv(country_continent_path, encoding="latin-1")
    country_continent["code_2"] = np.where(country_continent["country"] == "Namibia", "NA", country_continent["code_2"])

    map_continent1 = country_continent[["continent", "code_2"]]
    df_country = map_continent1.merge(df_country, left_on="code_2", right_on="country_code", how="right")
    df_country = df_country.sort_values(["country", "date"]).reset_index(drop=True)

    southeast_asia = ["Brunei", "Myanmar", "Cambodia", "Timor-Leste", "Indonesia", "Taiwan",
                      "Laos", "Malaysia", "Philippines", "Singapore", "Thailand", "Vietnam"]

    df_sea = df_country[df_country["country"].isin(southeast_asia)].drop(["country_code", "code_2"], axis=1)
    df_country = df_country.drop(["country_code", "code_2"], axis=1)

    return df_country, df_sea

global_mob, sea_mob = mobility_df()
# global_mob.to_csv("C:\programming\mobility\dfs\global_mobility_df.csv")
# sea_mob.to_csv("C:\programming\mobility\dfs\sea_mobility_df.csv")

countries = global_mob["country"].unique().tolist()
first_date = str(global_mob["date"][0].date())
last_date = str(global_mob["date"][len(global_mob)-1].date())

print(first_date, last_date)


##### ncov #####
ncov_confirmed = pd.read_csv(ncov_confirmed_path)
ncov_death = pd.read_csv(ncov_death_path)

def make_ncov_df(ncov_df): #simply get country level, drop na, unify formats
    df = ncov_df
    to_drop_cols = ["Lat", "Long"]
    df = df.drop(to_drop_cols, axis=1)

    ###GET ONLY COUNTRY LEVEL DATA###
    date_cols = range(2, len(df.columns))

    to_inspect_c = ["Australia", "Canada", "China", "Hong Kong"]
    aus_df = df[df["Country/Region"] == "Australia"]
    can_df = df[df["Country/Region"] == "Canada"]
    chi_df = df[df["Country/Region"] == "China"]
    hk_df = df[df["Province/State"] == "Hong Kong"]

    to_inspect_df = [aus_df, can_df, chi_df, hk_df]
    australia, canada, china, hongkong = [], [], [], []
    to_inspect_list = [australia, canada, china, hongkong]

    for i in range(len(to_inspect_list)):
        to_inspect_list[i].append(np.nan)
        to_inspect_list[i].append(to_inspect_c[i])

    date_cols = range(2, len(df.columns))
    for i in range(len(to_inspect_list)):
        for col in date_cols:
            mean = to_inspect_df[i].iloc[:, col].sum()
            to_inspect_list[i].append(mean)

    df_inspect = pd.DataFrame(to_inspect_list, columns=df.columns)

    df = pd.concat([df, df_inspect])
    df = df[df["Province/State"].isnull()]
    df = df.drop("Province/State", axis=1)
    df = df.set_index("Country/Region")

    return df

ncov_confirmed_df = make_ncov_df(ncov_confirmed)
ncov_death_df = make_ncov_df(ncov_death)

def chop_ncov_df(ncov_df): #sync dates, and countries with mobility dfs
    df = ncov_df
    df1 = df[df.index.isin(countries)]

    to_correct = []
    for c in countries:
        if c not in df1.index.values.tolist():
            to_correct.append(c)

    correct_dict = {}
    keys = ["Bahamas", "Korea, South", "Burma", "Taiwan*", "US"]
    val = to_correct
    for i in range(len(keys)):
        correct_dict[keys[i]] = val[i]

    to_correct_df = df[df.index.isin(keys)]
    to_correct_df.index = to_correct_df.index.map(
        correct_dict)

    df = pd.concat([df, to_correct_df])

    df1 = df[df.index.isin(countries)]

    def update_date_col(df):
        converted_d = [str(datetime.datetime.strptime(d,"%m/%d/%y").date()) for d in df1.columns]
        df.columns = converted_d
        return df

    df1 = update_date_col(df1)

    for i, v in enumerate(df1.columns):
        if v == first_date:
            low_bound=i
        if v == last_date:
            high_bound=i

    to_drop_head = df1.columns[0:low_bound]
    to_drop_tail = df1.columns[high_bound+1:]
    df1 = df1.drop(to_drop_head, axis=1)
    df1 = df1.drop(to_drop_tail, axis=1)

    df1 = df1.sort_values("Country/Region")

    return df1

ncov_c_df = chop_ncov_df(ncov_confirmed_df)
ncov_d_df = chop_ncov_df(ncov_death_df)


ncov_c_df.to_csv(r"C:\programming\mobility\dfs\ncov_c_df.csv")
ncov_d_df.to_csv(r"C:\programming\mobility\dfs\ncov_d_df.csv")

def combined_df(global_mob, ncov_c_df, ncov_d_df):
    def flatten(l):
        flat_l = []
        for sub_l in l:
            for item in sub_l:
                flat_l.append(item)
        return flat_l
    acc_cases = flatten(ncov_c_df.values.tolist())
    acc_death = flatten(ncov_d_df.values.tolist())

    global_mob["acc_case"] = acc_cases
    global_mob["acc_death"] = acc_death

    def get_new(df):
        new = []
        for c in df.index:
            l_new = df.loc[c].values.tolist()
            new.append(l_new[0])
            for i in range(1, len(l_new)):
                new.append(l_new[i]-l_new[i-1])
        return new
    new_case = get_new(ncov_c_df)
    new_death = get_new(ncov_d_df)
    global_mob["new_case"] = new_case
    global_mob["new_death"] = new_death

    for i, c in enumerate(global_mob["continent"]):
        if c == "Asia" or c == "Oceania":
            global_mob.loc[i, "continent"] = "Asia and Oceania"

    continent_marker = {
        "Asia and Oceania":1, 
        "Africa":2, 
        "Americas":3, 
        "Europe":4}
    global_mob["continent_marker"] = global_mob["continent"].map(continent_marker)

    for i, v in enumerate(global_mob["continent_marker"]):
        if v == 1:
            global_mob.loc[i, "continent_marker"] = random.uniform(0.7,1.3)
        elif v == 2:
            global_mob.loc[i, "continent_marker"] = random.uniform(1.7,2.3)
        elif v == 3:
            global_mob.loc[i, "continent_marker"] = random.uniform(2.7,3.3)
        else:
            global_mob.loc[i, "continent_marker"] = random.uniform(3.7,4.3)

    return global_mob

combined_df = combined_df(global_mob, ncov_c_df, ncov_d_df)
combined_df.to_csv(r"C:\programming\mobility\dfs\combined_df.csv")


def us_mobility_df():
    us_df = mob_df[mob_df["country"] == "United States"]
    us_rename_columns = {"sub_region_1": "state"}
    us_df = us_df.rename(columns=us_rename_columns)

    us_df = us_df[~us_df["state"].isnull()]
    us_df = us_df[us_df["sub_region_2"].isnull()]
    us_df = us_df.drop(["sub_region_2", "country_code", "country"], axis=1)
    us_df["parks"] = us_df["parks"].fillna(method="ffill")

    us_df["outdoor"] = (us_df["retail_and_recreation"] + us_df["grocery_and_pharmacy"] + us_df["parks"] + us_df["transit_stations"] + us_df["workplaces"])/5
    us_df = us_df.reset_index(drop=True)
    return us_df

us_mob = us_mobility_df()
us_mob.to_csv(r"C:\programming\mobility\dfs\us_mobility_df.csv")
# print(us_mob.head())

states = us_mob["state"].unique().tolist()

us_confirmed = pd.read_csv(us_ncov_confirmed_path)
us_death = pd.read_csv(us_ncov_death_path)

# print(us_confirmed.head())

for s in us_death["Province_State"].unique():
    if s not in us_mob["state"].unique():
        print(s)

def us_ncov_df(us_ncov_df): #drop cols, chop states and states
    df = us_ncov_df
    to_drop_cols = ["UID", "iso2", "iso3", "code3", "FIPS", "Admin2", "Country_Region", "Lat", "Long_", "Combined_Key"]
    df = df.drop(to_drop_cols, axis=1)
    if "Population" in df.columns:
        df = df.drop("Population", axis=1)

    df = df.set_index("Province_State")
    df = df[df.index.isin(states)]
    df = df.sort_values("Province_State")

    converted_d = []
    for d in df.columns:
        converted_d.append(str(datetime.datetime.strptime(d,"%m/%d/%y").date()))

    df.columns = converted_d
    for i, v in enumerate(df.columns):
        if v == first_date:
            low_bound=i
        if v == last_date:
            high_bound=i

    to_drop_head = df.columns[0:low_bound]
    to_drop_tail = df.columns[high_bound+1:]
    df = df.drop(to_drop_head, axis=1)
    df = df.drop(to_drop_tail, axis=1)

    gb = df.groupby("Province_State").sum()

    return gb

us_confirmed_df = us_ncov_df(us_confirmed)
us_confirmed_df.to_csv(r"C:\programming\mobility\dfs\us_combined.csv")
us_death_df = us_ncov_df(us_death)

def us_combined_df(us_mob, us_confirmed_df, us_death_df):
    def flatten(l):
        flat_l = []
        for sub_l in l:
            for item in sub_l:
                flat_l.append(item)
        return flat_l

    acc_cases = flatten(us_confirmed_df.values.tolist())
    acc_death = flatten(us_death_df.values.tolist())

    us_mob["acc_case"] = acc_cases
    us_mob["acc_death"] = acc_death

    def get_new(df):
        new = []
        for c in df.index:
            l_new = df.loc[c].values.tolist()
            new.append(l_new[0])
            for i in range(1, len(l_new)):
                new.append(l_new[i]-l_new[i-1])
        return new
    new_case = get_new(us_confirmed_df)
    new_death = get_new(us_death_df)
    us_mob["new_case"] = new_case
    us_mob["new_death"] = new_death

    return us_mob

us_combined = us_combined_df(us_mob, us_confirmed_df, us_death_df)
us_combined.to_csv(r"C:\programming\mobility\dfs\us_combined_df.csv")
print(us_combined.head())

