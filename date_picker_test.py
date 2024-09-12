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

from credentials import sql_engine_string_generator


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

# set the sql engine string
sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER','DATAHUB_BORDEN_DBNAME','DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
sql_engine=create_engine(sql_engine_string)

# set datetime parameters
now=dt.today()
start_date=(now-td(days=7)).strftime('%Y-%m-%d')
end_date=now.strftime('%Y-%m-%d')

def app_sql_setup(start_date, end_date):
    # csat sql query
    csat_sql_query=("""
    SET TIME ZONE 'GMT';
    SELECT DISTINCT ON (datetime) * FROM (
        SELECT datetime, ws_u AS u, ws_v AS v, vtempa AS temp
        FROM bor__csat_m_v0         
        WHERE ws_u IS NOT NULL
        AND datetime >= '{}' and datetime <='{}'
    ) AS csat
    ORDER BY datetime;
    """).format(start_date,end_date)

    # create the dataframes from the sql query
    csat_output_df=pd.read_sql_query(csat_sql_query, con=sql_engine)
    # set a datetime index
    csat_output_df.set_index('datetime', inplace=True)
    csat_output_df.index=pd.to_datetime(csat_output_df.index)

    # set plotting parameters
    csat_output_df.loc['axis',:]=[False, False, True]

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    def create_figure (df_index, df, plot_title, y_title_1, y_title_2, df_columns):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for column in df_columns:
            print (df_index, df.loc[:,column])
            fig.add_trace(
                go.Scatter(x=df_index, y=df[column], name=column),
                secondary_y=df.loc['axis',column])
        
        # set axis titles
        fig.update_layout(
            template='simple_white',
            title=plot_title,
            xaxis_title="Date",
            yaxis_title=y_title_1,
            yaxis2_title=y_title_2,
            legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )   
        )
        return fig

    fig=create_figure(csat_output_df.index,csat_output_df,'Borden CSAT','Winds (m/s)','Virt Temp (C)',csat_output_df.columns)
    return fig


# run the sql function based on the start and end times
csat_output_df=app_sql_setup(start_date, end_date)

# set up the app layout
app.layout = html.Div(children=
                    [
                    html.H1(children=['Borden Dashboard']),
                    html.Div(children=['Borden CSAT Display']),

                    dcc.DatePickerRange(
                        id='csat-date-picker',
                        min_date_allowed='2024-01-01',
                        max_date_allowed=end_date
                    ),
                    dcc.Graph(id='csat_plot',figure=app_sql_setup(start_date, end_date))
                    ] 
                    )

@app.callback(
    Output('csat_plot', 'figure'),
    Input('csat-date-picker', 'start_date'),
    Input('csat-date-picker', 'end_date'))

def update_output(start_date, end_date):
    print (start_date, end_date)
    if not start_date or not end_date:
        raise PreventUpdate
    else:
        csat_output_df=app_sql_setup(start_date, end_date)
        return csat_output_df


if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)