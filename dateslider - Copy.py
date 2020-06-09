import dash

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

DF_PATH = r"C:\programming\mobility\dfs\combined_weekly.csv"
df= pd.read_csv(DF_PATH, index_col=0)
df["date"] = pd.to_datetime(df["date"])

print(df.head())

date = df["date"]
numdate= [x for x in range(len(df['date'].unique()))]

dd = []
for d in df['date'].dt.date.unique():
    dd.append(d.strftime('%m/%d'))

mapped_marks = {numd:d for numd,d in zip(numdate, dd)}
print(mapped_marks)

for d in df["date"].unique():
	print(d)
	print(type(d))
	break

print(df["date"].unique()[0])
dc = df[df["date"] == df["date"].unique()[0]]