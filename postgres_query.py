import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date
from dotenv import load_dotenv
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from credentials import sql_engine_string_generator

# set the sql engine string
sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER','DATAHUB_BORDEN_DBNAME','DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
sql_engine=create_engine(sql_engine_string)
conn = sql_engine.connect()

def fig_generator(start_date,end_date,table,species_list,axis_list,plot_title,y_title_1,secondary_y_flag,y_title_2=None):
    print ('Plotting data')
    not_null_select=species_list.split(',')[0]
    # csat sql query
    csat_sql_query=("""
    SET TIME ZONE 'GMT';
    SELECT DISTINCT ON (datetime) * FROM (
        SELECT datetime, {}
        FROM {}         
        WHERE {} IS NOT NULL
        AND datetime >= '{}' and datetime <='{}'
    ) AS csat
    ORDER BY datetime;
    """).format(species_list,table,not_null_select,start_date,end_date)

    # create the dataframes from the sql query
    output_df=pd.read_sql_query(csat_sql_query, con=sql_engine)
    # set a datetime index
    output_df.set_index('datetime', inplace=True)
    output_df.index=pd.to_datetime(output_df.index)

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    def create_figure (df_index, df,plot_title,y_title_1,y_title_2,df_columns,axis_list):
        plot_color_list=['blue','red','green','orange']
        fig = make_subplots(specs=[[{"secondary_y": secondary_y_flag}]])
        for i,column in enumerate(df_columns):
            # print (df_index, df.loc[:,column])
            fig.add_trace(
                go.Scatter(x=df_index, y=df[column], name=column, line_color=plot_color_list[i]),
                secondary_y=axis_list[i])
        
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

    fig=create_figure(output_df.index,output_df,plot_title,y_title_1,y_title_2,output_df.columns,axis_list)
    return fig

def first_entry(table):
    first_entry_query=('SELECT datetime from {};').format(table)
    output = conn.execute(text(first_entry_query))
    return output.fetchone()[0].strftime('%Y-%m-%d')
