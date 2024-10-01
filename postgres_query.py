import pandas as pd
from ast import literal_eval
from sqlalchemy import create_engine
from sqlalchemy import text
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def sql_engine_string_generator(datahub_host, datahub_db, datahub_user, datahub_pwd): 

    # set a try except clause to grab the online credentials keys and if not, grab them locally as environment variables
    try:
        # set the key vault path
        KEY_VAULT_URL = "https://fsdh-proj-swapit-poc-kv.vault.azure.net/"
        error_occur = False

        # Retrieve the secrets containing DB connection details
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

        # Retrieve the secrets containing DB connection details
        DB_HOST = secret_client.get_secret(datahub_host).value
        DB_NAME = secret_client.get_secret(datahub_db).value
        DB_USER = secret_client.get_secret(datahub_user).value
        DB_PASS = secret_client.get_secret(datahub_pwd).value
        print ('Credentials loaded from FSDH')

    except Exception as e:
        # declare FSDH keys exception
        error_occur = True
        # print(f"An error occurred: {e}")

        # load the .env file using the dotenv module remove this when running a powershell script to confirue system environment vars
        parent_dir=os.path.dirname(os.getcwd())
        load_dotenv(os.path.join(parent_dir, '.env')) # default is relative local directory 
        DB_HOST = os.getenv(datahub_host)
        DB_NAME = os.getenv(datahub_db)
        DB_USER = os.getenv(datahub_user)
        DB_PASS = os.getenv(datahub_pwd)
        # print ('Credentials loaded locally')

    # set the sql engine string
    sql_engine_string=('postgresql://{}:{}@{}/{}?sslmode=require').format(DB_USER,DB_PASS,DB_HOST,DB_NAME)
    # print ('sql engine string: ',sql_engine_string)
    return sql_engine_string


def fig_generator(start_date,end_date,sql_query, database_name):

    # set the sql engine string
    sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER',database_name,'DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
    sql_engine=create_engine(sql_engine_string)
    conn = sql_engine.connect()

    # set the path to the sql folder
    sql_path='assets/sql_queries/'

    # load the plotting properties
    plotting_properties_df=pd.read_csv(sql_path+'plotting_inputs.txt', index_col=0, sep=';', converters={"axis_list": literal_eval})
    plot_title=plotting_properties_df.loc[sql_query,'plot_title']
    y_title_1=plotting_properties_df.loc[sql_query,'y_title_1']
    y_title_2=plotting_properties_df.loc[sql_query,'y_title_2']
    axis_list=list(plotting_properties_df.loc[sql_query,'axis_list'])
    secondary_y_flag=plotting_properties_df.loc[sql_query,'secondary_y_flag']
    
    # load the sql query
    filename=sql_query+'.sql'
    filepath=sql_path+filename
    with open(filepath,'r') as f:
        sql_query=f.read()

    # sql query
    sql_query=(sql_query).format(start_date,end_date)

    # create the dataframes from the sql query
    output_df=pd.read_sql_query(sql_query, con=sql_engine)
    # set a datetime index
    output_df.set_index('datetime', inplace=True)
    output_df.index=pd.to_datetime(output_df.index)

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    def create_figure (df_index, df,plot_title,y_title_1,y_title_2,df_columns,axis_list,secondary_y_flag):
        plot_color_list=['black','blue','red','green','orange','yellow','brown','violet','turquoise','pink','olive','magenta','lightblue','purple']
        fig = make_subplots(specs=[[{"secondary_y": secondary_y_flag}]])
        # fig = make_subplots()
        for i,column in enumerate(df_columns):
            if secondary_y_flag:
                fig.add_trace(
                    go.Scatter(x=df_index, y=df[column], name=column, line_color=plot_color_list[i]),
                    secondary_y=axis_list[i])
            else:
                fig.add_trace(
                    go.Scatter(x=df_index, y=df[column], name=column, line_color=plot_color_list[i]))

 
        if secondary_y_flag: 
            # set axis titles
            fig.update_layout(
                template='seaborn',
                title=plot_title,
                xaxis_title="Date",
                yaxis_title=y_title_1,
                yaxis2_title=y_title_2,
                legend=dict(
                y=0.99
                )   
            )
        else:
            fig.update_layout(
                template='seaborn',
                title=plot_title,
                xaxis_title="Date",
                yaxis_title=y_title_1,
                legend=dict(
                y=0.99
                )   
            )
        return fig

    fig=create_figure(output_df.index,output_df,plot_title,y_title_1,y_title_2,output_df.columns,axis_list,secondary_y_flag)
    conn.close()
    return fig

def first_entry(table,database_name):
    # set the sql engine string
    sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER',database_name,'DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
    print ('sql credentials', sql_engine_string)
    sql_engine=create_engine(sql_engine_string)
    conn = sql_engine.connect()

    first_entry_query=('SELECT datetime from {};').format(table)
    output = conn.execute(text(first_entry_query))
    conn.close()
    return output.fetchone()[0]
