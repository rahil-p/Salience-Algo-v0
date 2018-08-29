import warnings
import time
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential

#-----
def build_nn(layers):
    nn = Sequential()

    nn.add(LSTM(input_dim=layers[0],
                   output_dim=layers[1],
                   return_sequences=True))
    nn.add(Dropout(.2))

    nn.add(LSTM(layers[2],
                   return_sequences=False))
    nn.add(Dropout(.2))

    nn.add(Dense(output_dim=layers[3]))
    nn.add(Activation('linear'))

    compile_nn(nn)

    return nn

def compile_nn(nn):
    start = time.time()
    nn.compile(loss='mse', optimiser='rmsprop')
    print('Compilation time: ' + (time.time()-start))           #

    return

#model rest of day from available data

#model
