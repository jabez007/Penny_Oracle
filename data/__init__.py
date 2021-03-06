from .TimeSeries import TimeSeries
from collections import OrderedDict
import configuration_manager
from datetime import datetime, timedelta
import json
import os
import requests
from screener import TICKERS
from time import sleep

_api_key_ = configuration_manager.AppSettings["alpha vantage"]
_data_path_ = os.path.dirname(os.path.realpath(__file__))
_daily_json_ = os.path.join(_data_path_, 'daily.json')
_year_old_ = datetime.now().date() - timedelta(weeks=52)


def _load_daily_(tickers):
    """
    loads the cached time series data for all the ticker symbols
    :return: {
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
    """
    print("-- Loading time series data for each of our ticker symbols")
    with open(_daily_json_) as daily_json:
        daily_data = json.load(daily_json)

    for ticker, dates in list(daily_data.items()):
        if len(dates) == 0:  # if we've eventually cleared all the data from this ticker symbol
            del daily_data[ticker]
        else:
            # clean out any data that is older than one year
            for date in list(dates.keys()):
                if datetime.strptime(date, "%Y-%m-%d").date() < _year_old_:
                    del dates[date]

    for t in tickers:
        if t["ticker"] in daily_data:  # some of the tickers in the screener might not have data available
            '''
            _daily_data = _download_daily_100_(t["ticker"])
            sleep(2)  # slow it down so we don't hit a rate limit
            if len(_daily_data["Daily"]) <= 0:
                continue
            if t["ticker"] not in daily_data:
                daily_data[t["ticker"]] = _daily_data["Daily"]
            else:
                for date in _daily_data["Daily"]:
                    if datetime.strptime(date, "%Y-%m-%d").date() == datetime.now().date():
                        continue  # skip today's date so we don't pull in-progress data
                    if date not in daily_data[t["ticker"]]:
                        daily_data[t["ticker"]][date] = _daily_data["Daily"][date]
            
            _rsi_data = _download_rsi_(t["ticker"])
            sleep(2)
            for date, data in daily_data[t["ticker"]].items():
                if date in _rsi_data["RSI"]:
                    daily_data[t["ticker"]][date]["RSI"] = _rsi_data["RSI"][date]
                else:
                    daily_data[t["ticker"]][date]["RSI"] = "0.00"

            # '''
    _save_daily_(daily_data)

    return dict([(ticker, TimeSeries.from_json(ticker, dates)) for ticker, dates in daily_data.items()
                 if len(dates) > 0])


def _download_daily_100_(symbol):
    """
    downloads the daily time series of the last 100 days for the given ticker symbol
    :param symbol:
    :return: {
                "Symbol": "ABC",
                "Daily": {
                    "2018-06-17": {
                    },
                    "2018-06-18": {
                    }
                }
             }
    """
    data = {"Symbol": "",
            "Daily": OrderedDict()}

    r = requests.get(
        "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol + "&apikey=" + _api_key_)
    if r.status_code < 400:
        _data = r.json()
        if "Meta Data" in _data:
            data["Symbol"] = _data["Meta Data"]["2. Symbol"]
            data["Daily"] = OrderedDict(sorted(_data["Time Series (Daily)"].items()))

    return data


def _download_rsi_(symbol):
    """
    downloads the Relative Strength Index (RSI) time series of the given ticker symbol
    The default time frame for comparing up periods to down periods is 14, as in 14 trading days
    :param symbol:
    :return: {
                "Symbol": "ABC",
                "RSI": {
                    "2018-07-02": "",
                    "2018-06-29": ""
                }
             }
    """
    data = {"Symbol": "",
            "RSI": OrderedDict()}

    r = requests.get(
        "https://www.alphavantage.co/query?function=RSI&symbol=" + symbol + 
        "&interval=daily&time_period=14&series_type=close" +
        "&apikey=" + _api_key_)
    if r.status_code < 400:
        _data = r.json()
        if "Meta Data" in _data:
            data["Symbol"] = _data["Meta Data"]["1: Symbol"]
            for date, rsi in _data["Technical Analysis: RSI"].items():
                if len(date.split(" ")) == 1:  # the RSI for the current date will have a date and time
                    data["RSI"][date] = rsi["RSI"]

    return data


def _download_minus_di_(symbol):
    pass


def _download_plus_di_(symbol):
    pass


def _save_daily_(daily_data):
    """

    :param daily_data:
    :return:
    """
    with open(_daily_json_, 'w') as daily_json:
        json.dump(daily_data, daily_json, 
                  indent=4, sort_keys=True)


DAILY = _load_daily_(TICKERS)
