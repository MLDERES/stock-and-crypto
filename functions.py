from alpha_vantage.cryptocurrencies import CryptoCurrencies
from IPython.core.debugger import set_trace
import pandas as pd
TODAY = pd.datetime.today()

def GetHistoricalTicker(ticker, full=False, save_data=False):
    '''
    This will gather the standard data for a stock from AlphaVantage, including
    open, close, adjusted close, volume, dividend data, and split coefficient.  Other information is available
    using other API endpoints.
    :param ticker: Ticker symbol for the security required
    :param full: If True, then get up to 20 years worth of data and will store the data to a .csv file so that we can avoid having
    to go back to the API again.  If False, it will only gather the last 100 days and data will not be saved.
    :param save_data: This value is only relevant if full=False.  If True, we'll write the results to a file using the current date
    :return: A pandas dataframe of the information from AlphaVantage
    '''

    # Using AlphaVantage https://alpha-vantage.readthedocs.io/en/latest/
    # As of now, this just gets the last 100 days if I need more I'll have to do specify
    #  outputsize = 'full' which would bring back everything.  In that case, I'd likely try to load it from
    #  the CSV file instead and then merge together
    ts = TimeSeries(ALPHA_API, output_format='pandas')
    meta = None
    if full:
        historical = read_latest(ticker, errors='ignore')
        if historical is None:
            historical, meta = ts.get_daily_adjusted(symbol=ticker,outputsize='full')
            historical.rename(columns={'1. open':OPEN_PRICE, '2. high':DAY_HIGH,
                                       '3. low':DAY_LOW, '4. close':DAY_CLOSE,
                                       '5. adjusted close':ADJ_CLOSE, '6. volume':DAY_VOLUME,
                                       '7. dividend amount':DIVIDEND_AMT, '8. split coefficient':SPLIT_COEFFICIENT}
                              ,inplace=True)
            write_data(historical,ticker)
            ticker_data=historical
        else:
            # If we have old data, then we'll go back to the source and get new data
            if relativedelta(pd.to_datetime(historical.index[-1]), TODAY).days > 0:
                last_100, meta = ts.get_daily_adjusted(symbol=ticker,outputsize='compact')
                last_100.rename(columns={'1. open': OPEN_PRICE, '2. high': DAY_HIGH,
                                           '3. low': DAY_LOW, '4. close': DAY_CLOSE,
                                           '5. adjusted close': ADJ_CLOSE, '6. volume': DAY_VOLUME,
                                           '7. dividend amount': DIVIDEND_AMT, '8. split coefficient': SPLIT_COEFFICIENT}
                                  , inplace=True)
                ticker_data = historical.append(last_100)
                ticker_data.drop_duplicates(inplace=True)
                write_data(ticker_data,ticker)
            else:
                ticker_data = historical
    else:
        last_100, meta = ts.get_daily_adjusted(symbol=ticker,outputsize='compact')
        last_100.rename(columns={'1. open': OPEN_PRICE, '2. high': DAY_HIGH,
                                           '3. low': DAY_LOW, '4. close': DAY_CLOSE,
                                           '5. adjusted close': ADJ_CLOSE, '6. volume': DAY_VOLUME,
                                           '7. dividend amount': DIVIDEND_AMT, '8. split coefficient': SPLIT_COEFFICIENT},
                        inplace=True)
        if save_data:
            write_data(last_100,ticker)
        ticker_data = last_100
    return ticker_data
  

def GetCrypto(coin):
    '''
    :return: A pandas dataframe of the information from AlphaVantage
    '''

    # Using AlphaVantage https://alpha-vantage.readthedocs.io/en/latest/
    cc = CryptoCurrencies(key=ALPHA_API, output_format='pandas')
    data, meta_data = cc.get_digital_currency_daily(symbol=coin, market='USD')

    meta = None
    historical = read_latest(coin, parse_dates=True, errors='ignore')
    #set_trace()
    if historical is None:
        data, meta_data = cc.get_digital_currency_daily(symbol=coin, market='USD')
        data.rename(columns={'1a. open (USD)':OPEN_PRICE, '2a. high (USD)':DAY_HIGH,
                             '3a. low (USD)':DAY_LOW, '4a. close (USD)':DAY_CLOSE,
                             '5. volume':DAY_VOLUME,
                             '6. market cap (USD)':MARKET_CAP}
                    ,inplace=True)
        data = data[[OPEN_PRICE, DAY_HIGH, DAY_LOW, DAY_CLOSE, DAY_VOLUME, MARKET_CAP]]
        write_data(data, coin)
        ticker_data=data
    else:
        #set_trace()
        # If we have old data, then we'll go back to the source and get new data
        print(relativedelta(pd.to_datetime(historical.index[-1]), TODAY).days)
        if relativedelta(pd.to_datetime(historical.index[-1]), TODAY).days != 0:
            last_100, meta = cc.get_digital_currency_daily(symbol=coin, market='USD')
            last_100.rename(columns={'1a. open (USD)':OPEN_PRICE, '2a. high (USD)':DAY_HIGH,
                                     '3a. low (USD)':DAY_LOW, '4a. close (USD)':DAY_CLOSE,
                                     '5. volume':DAY_VOLUME,
                                     '6. market cap (USD)':MARKET_CAP}
                            ,inplace=True)
            last_100 = last_100[[OPEN_PRICE, DAY_HIGH, DAY_LOW, DAY_CLOSE, DAY_VOLUME, MARKET_CAP]]
            ticker_data = historical.append(last_100)
            ticker_data.drop_duplicates(inplace=True)
            write_data(ticker_data, coin)
        else:
            ticker_data = historical
    return ticker_data