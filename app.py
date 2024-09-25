import dash
from dash import Dash, html, dcc
from dash.exceptions import PreventUpdate
from datetime import datetime as dt
from datetime import timedelta as td
from dash.dependencies import Input, Output

# local modules
from postgres_query import fig_generator
from postgres_query import first_entry


# initialize the dash app as 'app'
app = Dash(__name__)

# set datetime parameters
now=dt.today()
start_date=(now-td(days=1)).strftime('%Y-%m-%d')
end_date=now.strftime('%Y-%m-%d')

csat_table='bor__csat_m_v0'
pic_table='bor__g2311f_m_v0'

# set datetime parameters
# csat_first_date=first_entry(csat_table,'DATAHUB_BORDEN_DBNAME')
# pic_first_date=first_entry(pic_table,'DATAHUB_BORDEN_DBNAME')
# first_date=(min(csat_first_date,pic_first_date)).strftime('%Y-%m-%d')
first_date='2024-01-01'

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
                    dcc.Graph(id='plot_1',figure=fig_generator(start_date,end_date,'plot_1','DATAHUB_BORDEN_DBNAME')),
                    html.Br(),
                    html.H2(children=['Borden CSAT Temperatures Display']),
                    dcc.Graph(id='plot_2',figure=fig_generator(start_date,end_date,'plot_2','DATAHUB_BORDEN_DBNAME'))
                    ] 
                    )

@app.callback(
    Output('plot_1', 'figure'),
    Output('plot_2', 'figure'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'))

def update_output(start_date,end_date):
    if not start_date or not end_date:
        raise PreventUpdate
    else:
        print ('Updating plot')
        plot_1_fig=fig_generator(start_date,end_date,'plot_1','DATAHUB_BORDEN_DBNAME')
        plot_2_fig=fig_generator(start_date,end_date,'plot_2','DATAHUB_BORDEN_DBNAME')
    return plot_1_fig,plot_2_fig

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)