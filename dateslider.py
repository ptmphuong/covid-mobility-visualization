import dash

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.io as pio

pio.orca.config.executable = r'C:\Users\MPPC\AppData\Local\Programs\orca'
pio.orca.config.save()

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

DF_PATH = r"C:\programming\mobility\dfs\combined_df.csv"
# DF_PATH = r"C:\programming\mobility\dfs\combined_weekly.csv"
df_w = pd.read_csv(DF_PATH)
df_w["date"] = pd.to_datetime(df_w["date"])

date = df_w["date"]
numdate= [x for x in range(len(df_w['date'].unique()))]

dd = ['02/15']
for d in df_w['date'].dt.date.unique()[1:]:
    dd.append(d.strftime('%m/%d'))

mapped_marks = {numd:d for numd,d in zip(numdate, dd)}


external_stylesheets = [r'https://codepen.io/chriddyp/pen/bWLwgP.css']


a3 = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# a3 = DjangoDash("DateSlider")

a3.layout = html.Div([
    html.Div([
        html.Div(
            [
            html.P("""Hover over the bubbles for country details""",
                        style={'padding-left': '2%'})
            ],
        ),         
        dcc.Graph(id='graph-with-slider'),
    ]),
    html.Div([
        html.Div(
            [
            html.H4("""Slide to switch between weeks: """,
                        style={'padding-left': '2%'})
            ],
        ), 
        dcc.Slider(
        id='date-slider',
        min = numdate[0],
        max = numdate[-1],
        value = numdate[-4],
        marks = mapped_marks,
        updatemode="drag"
        )
    ],
    ),                                                           
],
)


@a3.callback(
    Output('graph-with-slider', 'figure'),
    [Input('date-slider', 'value')])
def update_figure(selected_date):
    filtered_df = df_w[df_w["date"] == df_w["date"].unique()[selected_date]]

    fig = make_subplots(rows=1, cols=7, shared_yaxes=True, horizontal_spacing=0.005)

    categories = ['retail_and_recreation', 'grocery_and_pharmacy', 'parks', 'transit_stations', 'workplaces', 'outdoor', 'residential']
    trace1, trace2, trace3, trace4, trace5, trace6, trace7 = ([] for _ in range(7))
    traces = [trace1, trace2, trace3, trace4, trace5, trace6, trace7]
    title_text = ['Retail', 'Grocery', 'Parks', 'Transits', 'workplaces', 'Outdoor', 'Residential']

    colors = ["#F45C51", "#FBBA18", "#02A699", "#595BD4", "#87311F"]

    for i, v in enumerate(filtered_df.continent.unique()):
            df_by_continent = filtered_df[filtered_df['continent'] == v]
            df_by_continent = df_by_continent.set_index("date")
            traces[0].append(dict(
                x=df_by_continent['continent_marker'],
                y=df_by_continent[f'{categories[0]}'],
                text=df_by_continent['country'],
                mode='markers',
                opacity=0.9,
                marker={
                    'size': 7,
                    'color': colors[i],
                    'opacity':0.65,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=v,
                showlegend=True
            ))

    for t in range(1, len(traces)):
        for i, v in enumerate(filtered_df.continent.unique()):
            df_by_continent = filtered_df[filtered_df['continent'] == v]
            traces[t].append(dict(
                x=df_by_continent['continent_marker'],
                y=df_by_continent[f'{categories[t]}'],
                text=df_by_continent['country'],
                mode='markers',
                opacity=0.9,
                marker={
                    'size': 7,
                    'color': colors[i],
                    'opacity':0.65,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=v,
                showlegend=False
            ))
    for t in range(len(traces)):
        for trace in traces[t]:
            fig.append_trace(trace, row=1, col=t+1)
            fig.update_xaxes(title_text=title_text[t], row=1, col=t+1, showticklabels=False)
            fig.update_traces(hovertemplate='<b>%{text}</b> <br>%{y}')

    fig['layout'].update(yaxis={'title': 'Percent change from Jan 2020', 'range': [-100, 100]}, 
                            legend=dict(orientation="h", xanchor="auto", x=0.5, y=1.12),
                            height=500,
                            title={'text': f'{str(date[selected_date])[:10]}','xanchor':'center', 'x':0.5})

    return fig.write_image(f"im/{str(date[selected_date])[:10]}.png")

    # return fig


if __name__ == '__main__':
    a3.run_server(debug=True, port=8050)

for i in range(len(numdate)):
    update_figure(numdate[i])

