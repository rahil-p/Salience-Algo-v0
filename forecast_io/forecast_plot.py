import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np
from datetime import datetime

#-----
def plotly_set_credentials():
    plotly.tools.set_credentials_file(username='sentience', api_key=config.plotly_api_key)

def make_plot(data, symbol):
    open_data = go.Scatter(x=data['full_time_index'],
                           y=data['1. open'],
                           name='open',
                           hoverinfo='y',
                           line=dict(color='#074584'),
                           opacity=.8)
    high_data = go.Scatter(x=data['full_time_index'],
                           y=data['2. high'],
                           name='high',
                           hoverinfo='y',
                           line=dict(color='#183D34'),
                           opacity=.8,
                           visible='legendonly')
    low_data = go.Scatter(x=data['full_time_index'],
                          y=data['3. low'],
                          name='low',
                          hoverinfo='y',
                          line=dict(color='#E04514'),
                          opacity=.8,
                          visible='legendonly')
    close_data = go.Scatter(x=data['full_time_index'],
                            y=data['4. close'],
                            name='close',
                            hoverinfo='y',
                            line=dict(color='#F4E262'),
                            opacity=.8,
                            visible='legendonly')
    time_trace = go.Scatter(x=data['full_time_index'],
                            y=np.repeat(data['1. open'].max() + .05, len(data['1. open'])),
                            name='time',
                            hoverinfo='text',
                            text=data['date'].dt.time,
                            line=dict(color='#E8E8E8'),
                            opacity=.5)
    layout = go.Layout(title=symbol,
                       xaxis=dict(title='time',
                                  ticktext=np.unique([a.date() for a in data['date']]),
                                  tickvals=list(range(0, data['full_time_index'].max(), 390)),
                                  hoverformat='-----'),
                       yaxis=dict(title='USD ($)'))
    fig = go.Figure([open_data,
                     high_data,
                     low_data,
                     close_data,
                     time_trace], layout=layout)
    link = py.plot(fig, filename=symbol, auto_open=False)
    return link
