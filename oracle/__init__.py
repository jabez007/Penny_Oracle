from . import Plot
from data import DAILY, TimeSeries
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.layers import Dense, Dropout, LeakyReLU, LSTM
from keras.models import Sequential, load_model
import numpy
import os
import random


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # disable the verbose output from TensorFlow starting up

_oracle_path_ = os.path.dirname(os.path.realpath(__file__))
_oracle_checkpoint_format_ = "model-epoch{epoch:02d}-{val_acc:.4f}.hdf5"

SEQUENCE_LEN = 20
EPOCHS = 50
BATCH_SIZE = 64


def _format_input_output_(data, input_size=20):
    """
    formats the time series data for a ticker symbol into the X and Y for a LSTM model
    input.shape = (number_inputs, input_size, 5)
    output.shape = (number_inputs, 5)
    :param data: {
                        "ABC": {
                            "2018-06-17": {
                            },
                            "2018-06-18": {
                            }
                        },
                        "DEF": {
                            "2018-06-17": {
                            },
                            "2018-06-18": {
                            }
                        }
                     }
    :param input_size: the number of timestamps that make up the input
    :return: x and y for the input and output of a LSTM model
    """
    print("-- Formatting time series data for LSTM model")
    x, y = list(), list()
    for symbol, _data in random.shuffle(data.items()):
        _x, _y = _data.get_input_output(input_size, input_size)
        x += _x
        y += _y
    return numpy.array(x), numpy.array(y)


def _build_model_(inputs, neurons=1024, activation_function="tanh", dropout=0.3, loss="mse", optimizer="adam"):
    """
    define the LSTM model. Load the network weights from a previous run if available.
    https://www.kaggle.com/pablocastilla/predict-stock-prices-with-lstm
    https://dashee87.github.io/deep%20learning/python/predicting-cryptocurrency-prices-with-deep-learning/
    https://medium.com/@siavash_37715/how-to-predict-bitcoin-and-ethereum-price-with-rnn-lstm-in-keras-a6d8ee8a5109
    :param inputs:
    :param neurons:
    :param activation_function:
    :param dropout:
    :param loss:
    :param optimizer:
    :return:
    """
    print("-- Building LSTM model")
    # load previous model if it exists
    accuracy = 0
    filename = ""
    for f in os.listdir(_oracle_path_):
        if f.endswith('.hdf5'):
            if float(os.path.splitext(f)[0].split('-')[2]) > accuracy:
                filename = f
    if filename != "":
        print("checkpoint file: " + filename)
        model = load_model(os.path.join(_oracle_path_, filename))
    else:
        model = Sequential()
        model.add(LSTM(neurons, 
                       input_shape=(inputs.shape[1], inputs.shape[2]), 
                       return_sequences=True,
                       activation=activation_function))
        model.add(Dropout(dropout))
        model.add(LSTM(neurons, 
                       return_sequences=True,
                       activation=activation_function))
        model.add(Dropout(dropout))
        model.add(LSTM(neurons,
                       return_sequences=True,
                       activation=activation_function))
        model.add(Dropout(dropout))
        model.add(Dense(units=inputs.shape[2]))
        # https://medium.com/@huangkh19951228/predicting-cryptocurrency-price-with-tensorflow-and-keras-e1674b0dc58a
        # https://cdn-images-1.medium.com/max/800/1*I4OU7P938Otu95YAR6yMIw.png
        model.add(LeakyReLU())
    
    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
    model.summary()
    return model


_x_, _y_ = _format_input_output_(DAILY, SEQUENCE_LEN)
_model_ = _build_model_(_x_)


def train():
    """

    :return:
    """
    # define the checkpoint
    checkpoint = ModelCheckpoint(os.path.join(_oracle_path_, _oracle_checkpoint_format_),
                                 monitor='val_acc',
                                 save_best_only=True,
                                 mode='max')
    early_stop = EarlyStopping(monitor='val_acc',
                               min_delta=0.01,
                               patience=5,
                               mode='max')
    
    callbacks_list = [checkpoint, early_stop]

    # fit the model
    _model_.fit(_x_, _y_,
                validation_split=0.3,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                callbacks=callbacks_list)

    
def get_forecast(symbol, outlook_len=20):
    """

    :param symbol:
    :param outlook_len:
    :return:
    """
    outlook = list()
    
    if symbol in DAILY.keys():
        _seed = DAILY[symbol].get_seed(SEQUENCE_LEN)
        seed = numpy.array([_seed])
        if len(seed.shape) == 3 and seed.shape[1] == SEQUENCE_LEN:
            while len(outlook) < outlook_len:
                _forecast = _model_.predict(seed, verbose=0)
                outlook += [_forecast[0][0].tolist()]
                seed = numpy.array([(_seed + outlook)[-SEQUENCE_LEN:]])
            return TimeSeries.from_forecast(symbol, outlook)
