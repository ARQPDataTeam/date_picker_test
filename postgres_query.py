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


def fig_generator(start_date,end_date,sql_query, database_name):
    print ('Querying ',sql_query)
    # set the sql engine string
    sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER',database_name,'DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
    sql_engine=create_engine(sql_engine_string)
    conn = sql_engine.connect()

    # set the path to the sql folder
    sql_path='assets/sql_queries/'

    # load the plotting properties
    plotting_properties_df=pd.read_csv(sql_path+'plotting_inputs.txt', index_col=0, sep=';')
    plot_title=plotting_properties_df.loc[sql_query,'plot_title']
    y_title_1=plotting_properties_df.loc[sql_query,'y_title_1']
    y_title_2=plotting_properties_df.loc[sql_query,'y_title_2']
    axis_list=plotting_properties_df.loc[sql_query,'axis_list']
    secondary_y_flag=plotting_properties_df.loc[sql_query,'secondary_y_flag']
    print ('secondary_y_flag',secondary_y_flag)

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
        print ('secondary y',secondary_y_flag)
        plot_color_list=['black','blue','red','green','orange','yellow','brown','violet','turquoise','pink','olive','magenta','lightblue','purple']
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        # fig = make_subplots()
        for i,column in enumerate(df_columns):
            fig.add_trace(
                go.Scatter(x=df_index, y=df[column], name=column, line_color=plot_color_list[i]))
        # # print (df_index, df.loc[:,column])
        # if secondary_y_flag:
        #     fig.add_trace(
        #         go.Scatter(x=df_index, y=df[column], name=column, line_color=plot_color_list[i]),
        #         secondary_y=axis_list[i])
        # else:
        #     fig.add_trace(
        #         go.Scatter(x=df_index, y=df[column], name=column, line_color=plot_color_list[i]))

        fig.update_layout(
            template='simple_white',
            title=plot_title,
            xaxis_title="Date",
            yaxis_title=y_title_1,
            legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )   
        )
 
         # if secondary_y_flag: 
        #     print ('second y')   
        #     # set axis titles
        #     fig.update_layout(
        #         template='simple_white',
        #         title=plot_title,
        #         xaxis_title="Date",
        #         yaxis_title=y_title_1,
        #         yaxis2_title=y_title_2,
        #         legend=dict(
        #         yanchor="top",
        #         y=0.99,
        #         xanchor="left",
        #         x=0.01
        #     )   
        #     )
        # else:
        #     print ('no second y')
        #     fig.update_layout(
        #         template='simple_white',
        #         title=plot_title,
        #         xaxis_title="Date",
        #         yaxis_title=y_title_1,
        #         legend=dict(
        #         yanchor="top",
        #         y=0.99,
        #         xanchor="left",
        #         x=0.01
        #     )   
        #     )
        print ('returning fig')      
        return fig

    fig=create_figure(output_df.index,output_df,plot_title,y_title_1,y_title_2,output_df.columns,axis_list,secondary_y_flag)
    conn.close()
    return fig

def first_entry(table,database_name):
    # set the sql engine string
    sql_engine_string=sql_engine_string_generator('DATAHUB_PSQL_SERVER',database_name,'DATAHUB_PSQL_USER','DATAHUB_PSQL_PASSWORD')
    sql_engine=create_engine(sql_engine_string)
    conn = sql_engine.connect()

    first_entry_query=('SELECT datetime from {};').format(table)
    output = conn.execute(text(first_entry_query))
    conn.close()
    return output.fetchone()[0]
