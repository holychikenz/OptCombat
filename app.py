import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from optcombat import *

external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

maxhit   = lambda stat, bonus: np.floor(1.3 + stat/10 + bonus/80 + stat*bonus/640)
accuracy = lambda stat, bonus: stat*(bonus+64)

x = np.linspace(1, 99, 99)
y = np.linspace(1, 99, 99)
X, Y = np.meshgrid(x, y)
Z = maxhit(X, Y)
c = np.linspace(0, 50, 51)
bigx = np.linspace(1, 300, 300)

fig = go.Figure( data=
        go.Contour(
            z=Z,
            x=x,
            y=y,
            contours_coloring='lines',
            contours=dict(
                start=1,
                end=30,
                showlabels=True,
                labelfont = dict( size=12, color='black' ),
                size=1
                )
        ),
        layout=go.Layout(
            autosize = False,
            width = 600,
            height = 600
            )
      )

fig.update_layout( xaxis_title="Strength Level", yaxis_title="Strength Bonus" )

descipt = \
'''
The first plot is the 2 dimensional contour showing the max hit
breakpoints as a function of strength level and strength bonus.
Below are the one-dimensional slices of this plot, with the first
blotting the max hit for a target strength level with a fixed
strength bonus, and the second plot orthogonal to that.
'''

app.layout = html.Div(children=[
    html.H1(children='Max Hit Calculator'),
    html.P(children=descipt),
    html.Div(children=[
        dcc.Graph(
            id='MaxHitContour',
            figure = fig,
        )
    ],
    style={}
    ),
    html.Div(children=[
        html.H3(children='Strength Bonus'),
        dcc.Input(
            id='StrengthBonus',
            type="number",
            min=0,
            value=1,
        ),
        dcc.Graph(
            id='GivenBonus',
            ),
        ],
        style={}
        ),
    html.Div(children=[
        html.H3(children='Strength Level'),
        dcc.Input(
            id='StrengthLevel',
            type="number",
            min=1,
            value=1,
        ),
        dcc.Graph(
            id='GivenLevel',
            ),
        ],
        style={}
        )
])
@app.callback(
        Output('GivenBonus', 'figure'),
        Input('StrengthBonus', 'value')
)
def update_plot_one(input_value):
    x = np.linspace(1, 99, 99)
    try:
        str_bonus = int(input_value)
    except:
        str_bonus = 1
    func = maxhit(x, str_bonus)
    fign = go.Figure( data=
            px.scatter(x=x, y=func),
            layout=go.Layout(
                autosize = False,
                width = 600,
                height = 600
                )
            )
    fign.update_layout( xaxis_title="Strength Level", yaxis_title="Max Hit" )
    return fign

@app.callback(
        Output('GivenLevel', 'figure'),
        Input('StrengthLevel', 'value')
)
def update_plot_two(input_value):
    x = np.linspace(1, 99, 99)
    try:
        str_bonus = int(input_value)
    except:
        str_bonus = 1
    figz = go.Figure( data=
            px.scatter(x=bigx, y=maxhit(str_bonus, bigx)),
            layout=go.Layout(
                autosize = False,
                width = 600,
                height = 600
                )
        )
    figz.update_layout( xaxis_title="Strength Bonus", yaxis_title="Max Hit" )
    return figz


if __name__ == "__main__":
    app.run_server(debug=True)
