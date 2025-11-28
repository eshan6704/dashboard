# qresult.py
import yfinance as yf
import pandas as pd


def qresult(symbol):
    yfsymbol = symbol + ".NS"
    ticker = yf.Ticker(yfsymbol)
    df = ticker.quarterly_financials
    return df
def result(symbol):
    yfsymbol = symbol + ".NS"
    ticker = yf.Ticker(yfsymbol)
    df = ticker.quarterly_financials
    return df
    