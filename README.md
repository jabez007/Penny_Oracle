# Swing_Oracle
Using Python and Machine Learning to identify trends in small cap stocks
under $25 and possible [swing trades](https://www.eatsleeptrade.net/my-swing-trading-strategies)

## Resources
* [Intrinio Stock Screener API](http://docs.intrinio.com/?shell#securities-search-screener)
    for identifying stocks to train on and also make predictions on.
  * [Python source](https://github.com/intrinio/python-sdk)
* [Alpha Vantage](https://www.alphavantage.co/) for gathering data on
    identified stocks.
  * [Python source](https://github.com/RomelTorres/alpha_vantage)
* [Deep Learning with Keras](https://app.pluralsight.com/library/courses/keras-deep-learning/table-of-contents)
  * [TensorFlow: Getting Started](https://app.pluralsight.com/library/courses/tensorflow-getting-started/table-of-contents)

## Outline

### Training
We will use the screener API to search for securities that have 
a `52 Week Low` >= $1.00 and a `52 Week High` <= $25.00, 
with a `Market Capitalization` between $300,000,000 and
$2,000,000,000, and an `Average Daily Volume` over 500,000
```
https://api.intrinio.com/securities/search?conditions=52_week_low~gte~1.00,52_week_high~lte~25.00,marketcap~gte~300000000,marketcap~lte~2000000000,average_daily_volume~gte~500000
```
to get out our list of ticker symbols.
With that list of tickers, we will go through each one to pull the last
100 days worth of data from Alpha Vantage
```
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}
```
And those 100 days will then be split on a `Sequence Size` of 20 to
train our Recurrent Neural Network [LSTM](https://machinelearningmastery.com/time-series-prediction-lstm-recurrent-neural-networks-python-keras/) model

### Forecasting
Here we will again use the screener API to search for securities that 
have a `52 Week Low` >= $1.00 and a `52 Week High` <= $25.00 with
a `Market Capitalization` between $300,000,000 and $2,000,000,000, and 
an `Average Daily Volume` over 500,000
```
https://api.intrinio.com/securities/search?conditions=52_week_low~gte~1.00,52_week_high~lte~25.00,marketcap~gte~300000000,marketcap~lte~2000000000,average_daily_volume~gte~500000
```
to get out our list of ticker symbols, and with that list of tickers
pull the last 100 days worths of data from Alpha Vantage
```
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}
```
From there, we will take only the last 20 days of data from each ticker
to seed our model and run a forecast for the next 20 days. We will then
plot and analyze the forecasts looking for potential [long term swing trades](http://www.swing-trade-stocks.com/trading-strategy.html).

## Technical

### Training

#### [Number of Layers](https://www.heatonresearch.com/2017/06/01/hidden-layers.html)
* 2 -> Can represent an arbitrary decision boundary to arbitrary accuracy with rational activation functions and can approximate any smooth mapping to any accuracy.
* **>2 -> Additional layers can learn complex representations (sort of automatic feature engineering) for layer layers.**

#### [Number of Neurons](https://www.heatonresearch.com/2017/06/01/hidden-layers.html)
* The number of hidden neurons should be between the size of the input layer and the size of the output layer.
* The number of hidden neurons should be 2/3 the size of the input layer, plus the size of the output layer.
* The number of hidden neurons should be less than twice the size of the input layer.
