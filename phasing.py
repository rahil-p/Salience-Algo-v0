import config

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.cryptocurrencies import CryptoCurrencies

import warnings
from datetime import datetime
import time

#import keras
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential

import pandas as pd
import numpy as np
from numpy import newaxis
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error, confusion_matrix

import plotly
import plotly.plotly as py
import plotly.graph_objs as go



ts = TimeSeries(key=config.av_api_key, output_format='pandas')

warnings.filterwarnings('ignore')

#-----
def get_stock_intraday(symbol, starting_date='initial'):
    data, meta_data = ts.get_intraday(symbol, interval='1min', outputsize='full')
    data = wrangle(data, starting_date)
    return data, meta_data

#-----
def wrangle(data, starting_date):
    #USE pandas.DataFrame.assign with **kwargs if possible

    data['date'] = pd.to_datetime(data.index)
    data.index = range(data.shape[0])

    data.loc[data['5. volume'] == 0, '5. volume'] = 1               #ad hoc solution for avoiding nans when normalizing

    #create separate time indices
    if starting_date == 'initial':
        starting_date = data['date'].min()

    data['day_index'] = np.busday_count(pd.Series(np.repeat(starting_date,
                                                            len(data))).values.astype('datetime64[D]'),
                                        data['date'].values.astype('datetime64[D]'))

    #remove day indices which are not populated with stock data
    day_map = dict(zip(data['day_index'].unique(), range(len(data['day_index'].unique()))))
    data['day_index'].replace(day_map, inplace=True)

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

    data['value_delta'] = (data['4. close'] - data['1. open']) / data['1. open']
    data['close_off_high'] = (data['2. high'] - data['4. close']) / data['2. high']
    data['volatility'] = (data['2. high'] - data['3. low']) / data['1. open']

    # moving_avgs  = [3, 5, 10, 20, 30, 60, 120, 240, 360]
    # for ma in moving_avgs:
    #     data[str(ma) + 'MA'] =

    return data

def split_tt(data, train_size=.8):
    return data[:int(train_size * len(data))], data[int(train_size * len(data)):]

def generate_io(data, window_len,
                normalization_columns=['1. open', '2. high', '3. low', '4. close', '5. volume'],
                output_column='1. open'):
    #generates an array of sliding subsets of the input data, each with the # of rows as window_len
    inputs = []
    outputs = []
    output_price_scalers = []
    for i in range(len(data) - window_len - 1):
        tmp_window = data[i:(i + window_len)].copy()

        output = data[output_column].iloc[i + window_len] / tmp_window[output_column].iloc[0] - 1
        output_price_scaler = tmp_window[output_column].iloc[0]

        tmp_window = tmp_window.drop(columns=['date', 'day_index', 'session_time_index'])
        for column in normalization_columns:
            tmp_window[column] = tmp_window[column] / tmp_window[column].iloc[0] - 1

        #ad hoc '5. volume' standardization
        tmp_window['5. volume'] = tmp_window['5. volume'] / 100

        inputs.append(np.array(tmp_window))
        outputs.append(output)
        output_price_scalers.append(output_price_scaler)

    return np.array(inputs), np.array(outputs), np.array(output_price_scalers)

#-----
def build_nn(inputs, layer_neurons, output_size=1, dropout=.2, activation_f1x='tanh', activation_f2x='linear',
             loss='mse', optimizer='adam', metrics=['mse']):
    nn = Sequential()

    nn.add(LSTM(layer_neurons[0],
                input_shape=(inputs.shape[1], inputs.shape[2]),
                activation=activation_f1x,
                return_sequences=True))
    nn.add(Dropout(dropout))

    nn.add(LSTM(layer_neurons[1],
                activation=activation_f1x,
                return_sequences=True))
    nn.add(Dropout(dropout))

    nn.add(LSTM(layer_neurons[2],
                activation=activation_f1x,
                return_sequences=False))
    nn.add(Dropout(dropout))

    nn.add(Dense(units=output_size))
    nn.add(Activation(activation_f2x))

    compile_nn(nn, optimizer, metrics)

    return nn

def compile_nn(nn, optimizer, metrics):
    nn.compile(loss='mse', optimizer=optimizer, metrics=metrics)

    return nn

#model rest of day from available data

#model


#-----
def plotly_set_credentials():
    plotly.tools.set_credentials_file(username='sentience', api_key=config.plotly_api_key)

def make_plot(data, symbol, results='none'):
    open_data = go.Scatter(x=data.index,
                           y=data['1. open'],
                           name='open',
                           hoverinfo='y',
                           line=dict(color='#074584'),
                           opacity=.8)
    high_data = go.Scatter(x=data.index,
                           y=data['2. high'],
                           name='high',
                           hoverinfo='y',
                           line=dict(color='#183D34'),
                           opacity=.8,
                           visible='legendonly')
    low_data = go.Scatter(x=data.index,
                          y=data['3. low'],
                          name='low',
                          hoverinfo='y',
                          line=dict(color='#E04514'),
                          opacity=.8,
                          visible='legendonly')
    close_data = go.Scatter(x=data.index,
                            y=data['4. close'],
                            name='close',
                            hoverinfo='y',
                            line=dict(color='#F4E262'),
                            opacity=.8,
                            visible='legendonly')
    time_trace = go.Scatter(x=data.index,
                            y=np.repeat(data['1. open'].max() + .05, len(data['1. open'])),
                            name='time',
                            hoverinfo='text',
                            text=data['date'].dt.time,
                            line=dict(color='#E8E8E8'),
                            opacity=.5)


    layout = go.Layout(title=symbol,
                       xaxis=dict(title='time',
                                  ticktext=np.unique([a.date() for a in data['date']]),
                                  tickvals=list(range(0, data.index.max(), 390)),
                                  hoverformat='-----',
                                  showspikes=True),
                       yaxis=dict(title='USD ($)'))

    if results == 'none':
        fig = go.Figure([open_data,
                         high_data,
                         low_data,
                         close_data,
                         time_trace], layout=layout)
    elif results.ndim == 1:
        predict_data = go.Scatter(x=data.index[-len(results):],
                                  y=results,
                                  name='open (predicted)',
                                  hoverinfo='y',
                                  line=dict(color='#B6D9FB'),
                                  opacity=.8)
        fig = go.Figure([open_data,
                         predict_data,
                         high_data,
                         low_data,
                         close_data,
                         time_trace], layout=layout)
    elif results.ndim == 2:
        trace_array = [open_data,
                       high_data,
                       low_data,
                       close_data,
                       time_trace]
        for i, sublist in enumerate(results):
            trace_array.insert(i+1, go.Scatter(x=data.index[-len(results.flatten())+(i*results.shape[1]): \
                                                            -len(results.flatten())+((i+1)*results.shape[1])],
                                               y=sublist,
                                               name='open (predicted ' + str(i) + ')',
                                               hoverinfo='y',
                                               line=dict(color='#B6D9FB'),
                                               opacity=.8,
                                               showlegend=False))
        fig = go.Figure(trace_array, layout=layout)
    else:
        return

    link = py.plot(fig, filename=symbol, auto_open=True)

#-----
def main():
    symbol = 'F'
    data, _ = get_stock_intraday(symbol)

    inputs, outputs, output_price_scalers = generate_io(data, window_len=10)
    train_inputs, test_inputs = split_tt(inputs)
    train_outputs, test_outputs = split_tt(outputs)
    train_scalers, test_scalers = split_tt(output_price_scalers)

    # SINGLE-POINT REGRESSOR
    lstm_rnn = build_nn(train_inputs, layer_neurons=[482, 482, 482])
    lstm_rnn.fit(train_inputs, train_outputs,
                 epochs=25, batch_size=10, verbose=1,                           #turn off verbose
                 validation_data=(test_inputs, test_outputs), shuffle=False)



    test_predicts = lstm_rnn.predict(test_inputs).flatten()
    test_direction_predicts = [1  if x > 0 else 0 for x in test_predicts]
    test_direction_actuals = [1  if x > 0 else 0 for x in test_outputs]
    print(test_direction_predicts)
    print(test_direction_actuals)

    print(confusion_matrix(test_direction_actuals, test_direction_predicts))



    test_predicts_prices = (test_predicts + 1) * test_scalers
    test_actuals_prices = (test_outputs + 1) * test_scalers

    mse = mean_squared_error(test_actuals_prices, test_predicts_prices)
    print(mse)
    make_plot(data, symbol, results=test_predicts_prices)



    # SINGLE-POINT CLASSIFIER (+/-) - WIP
    # lstm_classifier = build_nn(train_inputs, layer_neurons=[20, 20, 20],
    #                            activation_f1x='relu', activation_f2x='sigmoid',
    #                            loss='binary_crossentropy', metrics=['accuracy'])
    # lstm_classifier.fit(train_inputs, [1 if x > 0 else 0 for x in train_outputs],
    #                     epochs=10, batch_size=10, verbose=1,
    #                     validation_data=(test_inputs, [1 if x > 0 else 0 for x in test_outputs]), shuffle=False)
    #
    # test_class_predicts = lstm_classifier.predict(test_inputs).flatten()
    # print(test_class_predicts)
    # print([1 if x >= .5 else 0 for x in test_class_predicts])
    # print([1 if x > 0 else 0 for x in test_outputs])
    # print(confusion_matrix([1  if x > 0 else 0 for x in test_outputs],
    #                        [1 if x >= .5 else 0 for x in test_class_predicts]))






    # MULTI-POINT REGRESSOR
    # sequence_len = 10
    # sequence_predicts = []
    # for i in range(len(test_inputs) // sequence_len):
    #     tmp_frame = test_inputs[(i * sequence_len) +
    #                             (len(test_inputs) % sequence_len)]              #selects data every sequence_len points
    #     predicted = []
    #     for j in range(sequence_len):
    #         tmp_p = lstm_rnn.predict(np.array(tmp_frame[newaxis,:,:]))[0][0]    #append prediction
    #         # print(np.append(np.repeat(tmp_p, 4), [0, 0, 0, 0]))
    #         predicted.append(tmp_p)
    #         tmp_frame = tmp_frame[1:]                                           #remove first row of window
    #         tmp_frame = np.insert(tmp_frame, [sequence_len-2],
    #                               predicted[-1], axis=0)                        #insert last prediction to tmp_frame
    #     sequence_predicts.append(predicted)
    # sequence_predicts_flat = np.array(sequence_predicts).flatten()
    # ms_test_predicts_prices = (sequence_predicts_flat + 1) * test_scalers[-len(sequence_predicts_flat):]
    # ms_test_actuals_prices = test_actuals_prices[-len(ms_test_predicts_prices):]
    #
    # ms_mse = mean_squared_error(ms_test_actuals_prices, ms_test_predicts_prices)
    # ms_sl_mse = mean_squared_error(ms_test_actuals_prices[sequence_len-1::sequence_len],
    #                                ms_test_predicts_prices[sequence_len-1::sequence_len])
    # make_plot(data, symbol, results=ms_test_predicts_prices.reshape(np.array(sequence_predicts).shape))
    #
    # ms_sl_mse0 = mean_squared_error(ms_test_actuals_prices[sequence_len::sequence_len],
    #                                 ms_test_predicts_prices[sequence_len::sequence_len])
    # print(ms_sl_mse0)
    # print(ms_mse)
    # print(ms_sl_mse)


    # print(data)
    # print(test_inputs[0])
    # print(mse)

if __name__ == '__main__':
    main()
