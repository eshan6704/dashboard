# qresult.py
import yfinance as yf
import pandas as pd

def info(symbol):

        tk = yf.Ticker(symbol + ".NS")
        return tk

def qresult(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.quarterly_financials
    return df
    
def result(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.financials
    return df
    
def balance(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.balance_sheet
    return df
    
def cashflow(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.cashflow
    return df
    
def dividend(symbol):        
    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.dividends.to_frame('Dividend')
    return df
    
def split(symbol): 
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.splits.to_frame('Split')
        return df
    
def intraday(symbol): 

        df = ticker.download(symbol + ".NS",period="1d",interval="5min").round(2)
        return df
    
def daily(symbol): 

        df = ticker.download(symbol + ".NS",period="1y",interval="1d").round(2)
        return df