import config

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators                 #
from alpha_vantage.cryptocurrencies import CryptoCurrencies             #

import pandas as pd
import numpy as np

from datetime import datetime

ts = TimeSeries(key=config.av_api_key, output_format='pandas')

#-----
def get_stock_intraday(symbol):
    data, meta_data = ts.get_intraday(symbol, interval='1min', outputsize='full')
    data = wrangle(data)
    return data, meta_data

#-----
def wrangle(data):
    data['date'] = pd.to_datetime(data.index)
    data.index = range(data.shape[0])

    #create separate time indices
    data['day_index'] = np.busday_count(pd.Series(np.repeat(data['date'].min(),
                                                            len(data))).values.astype('datetime64[D]'),
                                        data['date'].values.astype('datetime64[D]'))
    data['session_time_index'] = data['date'].apply(lambda a: ((a.hour*60) + a.minute) - 570)
    data['full_time_index'] = (data['day_index']*390) + data['session_time_index']

    #create NaN rows for missing time series values
    data = data.set_index('full_time_index').reindex(pd.Index(np.arange(data['full_time_index'].min(),
                                                                        data['full_time_index'].max() + 1),
                                                              name='full_time_index')).reset_index()
    data = data.drop(columns=['full_time_index'])

    #interpolate NaN values for all columns
    for column in data.columns:
        if column != 'date':
            data[column].interpolate(method='values', inplace=True)                         #interpolate float columns
        else:
            tmp = data['date'].apply(lambda t: (t-datetime(1970,1,1)).total_seconds())      #turn date into seconds
            tmp.interpolate(method='values', inplace=True)                                  #interpolate (now float)
            data[column] = pd.to_datetime(tmp, unit='s')                                    #replace

    return data
