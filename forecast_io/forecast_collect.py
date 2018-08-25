import config
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.cryptocurrencies import CryptoCurrencies

ts = TimeSeries(key=config.api_key)

def get_stock_intraday(symbol):
    data, meta_data = ts.get_intraday(stock)
