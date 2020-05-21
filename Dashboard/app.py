import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from utils.prepare_data import most_common_columns, most_common_data, desc_stat_columns, desc_stat_data

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Newspaper'),

    html.Div(children='''
        Newspaper.
    '''),

    html.Div(children='''
        Descriptive Statistics.
    '''),

    dash_table.DataTable(
        id='desc-stats',
        columns=desc_stat_columns,
        data=desc_stat_data,
    ),

    html.Div(children='''
    Most Common Words.
    '''),

    dash_table.DataTable(
        id='most-common',
        columns=most_common_columns,
        data=most_common_data,
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
