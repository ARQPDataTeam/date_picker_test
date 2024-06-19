from dash import Dash, html, dcc 
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime as dt
from datetime import date
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# initialize the dash app as 'app'
app = Dash(__name__)

# set the key vault path
KEY_VAULT_URL = "https://fsdh-swapit-dw1-poc-kv.vault.azure.net/"
error_occur = False

try:
    # Retrieve the secrets containing DB connection details
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

    # Retrieve the secrets containing DB connection details
    DB_HOST = secret_client.get_secret("datahub-psql-server").value
    DB_NAME = secret_client.get_secret("datahub-psql-db_name").value
    DB_USER = secret_client.get_secret("datahub-psql-user").value
    DB_PASS = secret_client.get_secret("datahub-psql-password").value
except Exception as e:
    error_occur = True
    print(f"An error occurred: {e}")

# set the sql engine string
sql_engine_string=('postgresql://{}:{}@{}/{}').format(DB_USER,DB_PASS,DB_HOST,DB_NAME)
sql_engine=create_engine(sql_engine_string)


# sql query
sql_query="""
    SET TIME ZONE 'GMT';
    select datetime, ws_u, ws_v 
    from hwy__csat_v0
    order by datetime
    limit 10000;
    """

# create the dataframe from the sql query
met_output_df=pd.read_sql_query(sql_query, con=sql_engine)

met_output_df.set_index('datetime', inplace=True)
met_output_df.index=pd.to_datetime(met_output_df.index)
beginning_date=met_output_df.index[0]
ending_date=met_output_df.index[-1]
today=dt.today().strftime('%Y-%m-%d')

# use specs parameter in make_subplots function
# to create secondary y-axis


# plot a scatter chart by specifying the x and y values
# Use add_trace function to specify secondary_y axes.
def create_figure(met_output_df):
    fig.add_trace(
        go.Scatter(x=met_output_df.index, y=met_output_df['ws_u'], name="U WInd Speed"),
        secondary_y=False)
    
    # Use add_trace function and specify secondary_y axes = True.
    fig.add_trace(
        go.Scatter(x=met_output_df.index, y=met_output_df['ws_v'], name="V Wind Speed"),
        secondary_y=True,)

    # set axis titles
    fig.update_layout(
        template='simple_white',
        title='HWY 401 CSAT Data',
        xaxis_title="Date",
        yaxis_title="WS U",
        yaxis2_title="WS V",
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )   
    )
    return create_figure

# set up the app layout
app.layout = html.Div(children=
                    [
                    html.H1(children=['SWAPIT HWY 401 Met Dashboard']),
                    html.Div(children=['Met plot display with date picker']),

                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=beginning_date,
                        max_date_allowed=ending_date
                    ),
                    dcc.Graph(id='hwy401-csat-plot',figure={}),
                    
                    ] 
                    )

# @app.callback(
#     Output('graph_2', 'figure'),
#     [Input('date-picker', 'start_date'),
#     Input('date-picker', 'end_date')],
#     [State('submit_button', 'n_clicks')])

@app.callback(
    Output('hwy401-csat-plot', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))

def update_output(start_date, end_date):
    print (start_date, end_date)
    if not start_date:
        start_date=met_output_df.index[0]
    if not end_date:
        end_date=met_output_df.index[-1]
    
    fig['layout']['xaxis']={'range':(start_date,end_date)}
    return fig

    # string_prefix = 'You have selected: '
    # if start_date is not None:
    #     start_date_object = dt.strptime(start_date, '%Y-%m-%d')
    #     start_date_string = start_date_object.strftime('%Y-%m-%d')
    #     string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    # if end_date is not None:
    #     end_date_object = dt.strptime(end_date, '%Y-%m-%d')
    #     end_date_string = end_date_object.strftime('%Y-%m-%d')
    #     string_prefix = string_prefix + 'End Date: ' + end_date_string
    # if len(string_prefix) == len('You have selected: '):
    #     return 'Select a date to see it displayed here'
    # else:
    #     return string_prefix


if __name__=='__main__':
    app.run(debug=True)
