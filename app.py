import dash
from dash import Dash, html, dcc, callback 
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
import numpy as np

# local modules
from credentials import sql_engine_string_generator
from postgres_query import fig_generator
from postgres_query import first_entry


# initialize the dash app as 'app'
app = Dash(__name__)

# set a try except clause to grab the online credentials keys and if not, grab them locally as environment variables
try:
    # set the key vault path
    KEY_VAULT_URL = "https://fsdh-swapit-dw1-poc-kv.vault.azure.net/"
    error_occur = False

    # Retrieve the secrets containing DB connection details
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

    # Retrieve the secrets containing DB connection details
    DB_HOST = secret_client.get_secret("datahub-psql-server").value
    DB_NAME = secret_client.get_secret("datahub-psql-dbname").value
    DB_USER = secret_client.get_secret("datahub-psql-user").value
    DB_PASS = secret_client.get_secret("datahub-psql-password").value
    print ('Credentials loaded from FSDH')

except Exception as e:
    # declare FSDH keys exception
    error_occur = True
    print(f"An error occurred: {e}")

    # load the .env file using the dotenv module remove this when running a powershell script to confirue system environment vars
    load_dotenv() # default is relative local directory 
    env_path='.env'
    DB_HOST = os.getenv('DATAHUB_PSQL_SERVER')
    DB_NAME = os.getenv('DATAHUB_PSQL_DBNAME')
    DB_USER = os.getenv('DATAHUB_PSQL_USER')
    DB_PASS = os.getenv('DATAHUB_PSQL_PASSWORD')
    print ('Credentials loaded locally')


# set datetime parameters
now=dt.today()
start_date=(now-td(days=1)).strftime('%Y-%m-%d')
end_date=now.strftime('%Y-%m-%d')


csat_table='bor__csat_m_v0'
pic_table='bor__g2311f_m_v0'

# set datetime parameters
csat_first_date=first_entry(csat_table,'DATAHUB_BORDEN_DBNAME')
pic_first_date=first_entry(pic_table,'DATAHUB_BORDEN_DBNAME')
first_date=(min(csat_first_date,pic_first_date)).strftime('%Y-%m-%d')

now=dt.today()
start_date=(now-td(days=7)).strftime('%Y-%m-%d')
end_date=now.strftime('%Y-%m-%d')

# set up the app layout
app.layout = html.Div(children=
                    [
                    html.H1('BORDEN DASHBOARD', style={'textAlign': 'center'}),
                    html.H3('Pick the desired date range.  This will apply to all plots on the page.'),
                    dcc.DatePickerRange(
                        id='date-picker',
                        min_date_allowed=first_date,
                        max_date_allowed=end_date,
                        display_format='YYYY-MM-DD'
                    ),
                    html.H2('Borden CR3000 Temperatures Display'),
                    dcc.Graph(id='cr3000_plot',figure=fig_generator(start_date,end_date,'cr3000_temps','DATAHUB_BORDEN_DBNAME')),
                    html.Br(),
                    html.H2(children=['Borden CSAT Temperatures Display']),
                    dcc.Graph(id='csat_plot',figure=fig_generator(start_date,end_date,'csat_temps','DATAHUB_BORDEN_DBNAME'))
                    ] 
                    )

@app.callback(
    Output('cr3000_plot', 'figure'),
    Output('csat_plot', 'figure'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'))

def update_output(start_date,end_date):
    if not start_date or not end_date:
        raise PreventUpdate
    else:
        print ('Updating plot')
        cr3000_fig=fig_generator(start_date,end_date,'cr3000_temps','DATAHUB_BORDEN_DBNAME')
        csat_fig=fig_generator(start_date,end_date,'csat_temps','DATAHUB_BORDEN_DBNAME')
    return cr3000_fig,csat_fig

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)