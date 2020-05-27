import dash

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd

df_path = r"C:\programming\mobility\dfs\combined_df.csv"
df = pd.read_csv(df_path, index_col=0)
df["date"] = pd.to_datetime(df["date"])

date = df["date"]
numdate= [x for x in range(len(df['date'].unique()))]

dd = ['02/15']
for d in df['date'].dt.date.unique()[1:]:
    if d.strftime('%d') == '01':
        dd.append(d.strftime('%m/%d'))
    else:
        dd.append(d.strftime('%d'))

for i, d in enumerate(dd):
    if d[0]=="0":
        dd[i] = d[1:]

for i, d in enumerate(dd):
    if len(d) > 3:
        if d[2]=="0":
            dd[i] = d.replace(d[2], "")



mapped_marks = {numd:d for numd,d in zip(numdate, dd)}

for k, v in mapped_marks.items():
    if len(v) >2:
        mapped_marks[k] = {'label':f'{v}', 'style':{'color':'#24A5A9', 'font-size':11, 'font-weight': 'bolder'}}
    else:
        mapped_marks[k] = {'label':f'{v}', 'style':{'font-size':9}}


external_stylesheets = [r'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='graph-with-slider'),
    ]),
    html.Div([
            dcc.Slider(
            id='date-slider',
            min = numdate[0],
            max = numdate[-1],
            value = numdate[55],
            marks = mapped_marks,
            updatemode="drag"
        )
    ],
    style={'font-size':2}
    ),                                                           
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('date-slider', 'value')])
def update_figure(selected_date):
    filtered_df = df[df["date"] == date[selected_date]]

    fig = make_subplots(rows=1, cols=7, shared_yaxes=True, horizontal_spacing=0.005)

    categories = ['retail_and_recreation', 'grocery_and_pharmacy', 'parks', 'transit_stations', 'workplaces', 'outdoor', 'residential']
    trace1, trace2, trace3, trace4, trace5, trace6, trace7 = ([] for _ in range(7))
    traces = [trace1, trace2, trace3, trace4, trace5, trace6, trace7]

    colors = ["#F45C51", "#FBBA18", "#02A699", "#595BD4", "#87311F"]

    for i, v in enumerate(filtered_df.continent.unique()):
            df_by_continent = filtered_df[filtered_df['continent'] == v]
            traces[0].append(dict(
                x=df_by_continent['continent_marker'],
                y=df_by_continent[f'{categories[0]}'],
                text=df_by_continent['country'],
                mode='markers',
                opacity=0.9,
                marker={
                    'size': 8,
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
                    'size': 8,
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
            fig.update_xaxes(title_text=categories[t], row=1, col=t+1, showticklabels=False)
            fig.update_traces(hovertemplate='<b>%{text}</b> <br>%{y}')

    fig['layout'].update(yaxis={'title': 'Percent change', 'range': [-100, 100]}, title='my title')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

