import config

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import pandas as pd

ts = TimeSeries(key=config.av_api_key, output_format='pandas')

#-----
def get_stock_intraday(symbol):
    data, meta_data = ts.get_intraday(symbol, interval='1min', outputsize='full')
    data = wrangle(data)
    return data, meta_data

def wrangle(data):
    data['date'] = pd.to_datetime(data.index)
    data.index = range(data.shape[0])

    data['day_index'] = [a.days for a in (data['date'] - data.date.min())]
    data['session_time_index'] = data['date'].apply(lambda a: ((a.hour*60) + a.minute) - 570)
    data['full_time_index'] = (data['day_index']*390) + data['session_time_index']

    return data