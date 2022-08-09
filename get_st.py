# -*-coding:utf-8-*-
__author__ = 'Sunny'

import requests


def send_notice(text):
    params = {"message": "{}".format(text)}
    r = requests.post("***", headers=headers, params=params)
    print(r.status_code)  # 200


import pandas as pd

pd.set_option('display.max_rows', None)

import warnings

warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
import time

api_key = 'aarTAfshbstbs0onc8fa'
api_secret = 'ssvsbIrTaSPjgKuWsbsdZ9fYfwD9Rhv'


# print(UTC0)


def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])
    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)
    return tr


def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()
    return atr


def supertrend(df, period=34, atr_multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
    return df



# Create a function to calculate the Double Exponential Moving Average (DEMA)
def DEMA(data, time_period, column):
    # Calculate the Exponential Moving Average for some time_period (in days)
    EMA = data[column].ewm(span=time_period, adjust=False).mean()
    # Calculate the DEMA
    DEMA = 2 * EMA - EMA.ewm(span=time_period, adjust=False).mean()
    return DEMA


def main(coin):
    # coin = ['LTCUSDT']
    candlesticks = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1HOUR, UTC0[0], UTC0[1])

    for candle in candlesticks:
        del candle[-6:]  # only need the first few columns

    p = 34
    arm = 3

    df = pd.DataFrame(candlesticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = df['timestamp'].apply(lambda x: x + 28800000)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    df['ema5'] = df['close'].ewm(span=5, min_periods=0, adjust=True, ignore_na=True).mean()
    df['dema144'] = DEMA(df, 144, 'close')
    df['dema169'] = DEMA(df, 169, 'close')
    supertrend_data = supertrend(df, period=p, atr_multiplier=arm)
    # supertrend_data.to_csv("C:/Users/Sunny/PycharmProjects/autotrading/data/{}_{}.csv"
    #                        .format(coin, time_range[0].split(' ')[0]))

    PNL = []
    StopTake = []
    profit = []
    fee = 0.02  # %
    st = 0.05
    tp = 0.3

    # def send_signal(text):
    #     index = int(text.split('{}'.format(coin))[0])
    #     time_diff = [str(df['timestamp'][index + 1]).split(' '),
    #                  datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(' ')]
    #     if time_diff[0][0] == time_diff[1][0] and time_diff[0][1].split(':')[0] == time_diff[1][1].split(':')[0]:
    #         send_notice(text)
    #         print(text)

    def check_sg(t):
        now = datetime.now().strftime('%Y-%m-%d %H:00:00')
        now2 = datetime.strptime(now, "%Y-%m-%d %H:00:00") - timedelta(hours=1)

        if str(t.split('   ')[0]) == str(now):
            with open(fpath, 'r') as file:
                content = file.read()
                if t.split(': ')[0] in content:
                    file.close()
                else:
                    send_notice(t)
                    f = open(fpath, 'a')
                    f.write(t + '\n')
                    f.close()



    def check_buy_sell_signals(last_row_index):
        previous_row_index = last_row_index - 1
        # next_row_index = last_row_index + 1
        if last_row_index < 3:
            return

        lastPrice = df['close'][last_row_index]

        # with open("C:/Users/Sunny/PycharmProjects/autotrading/data/{}_{}.csv".format(coin, time_range[0].split(' ')[0]),
        #           'r') as file:
        #     data = file.readlines()
        #     trend1 = data[-1].split(',')[-1]
        #     trend2 = data[-2].split(',')[-1]
        #     file.close()

        if len(PNL) != 0:
            percent = ((lastPrice / PNL[0][1]) - 1) * 100
            if PNL[0][0] == 0:
                percent = -percent
                if lastPrice < StopTake[0][1]:
                    profit.append(round(percent - fee, 2))
                    # print(coin, df['timestamp'][last_row_index], 'Buy(+%): ', lastPrice, round(profit[-1], 2))
                    PNL.clear()
                    StopTake.clear()
                elif lastPrice > StopTake[0][0]:
                    profit.append(round(percent - fee, 2))
                    # print(coin, df['timestamp'][last_row_index], 'Buy(-%): ', lastPrice, round(profit[-1], 2))
                    PNL.clear()
                    StopTake.clear()
       
            elif PNL[0][0] == 1:
                if lastPrice > StopTake[0][1]:
                    profit.append(round(percent - fee, 2))
                    # print(coin, df['timestamp'][last_row_index], 'Sell(+%):', lastPrice, round(profit[-1], 2))
                    PNL.clear()
                    StopTake.clear()
                elif lastPrice < StopTake[0][0]:
                    profit.append(round(percent - fee, 2))
                    # print(coin, df['timestamp'][last_row_index], 'Sell(-%):', lastPrice, round(profit[-1], 2))
                    PNL.clear()
                    StopTake.clear()



        if not df['in_uptrend'][last_row_index]:

            if lastPrice < df['dema144'][last_row_index] or lastPrice < df['dema169'][last_row_index]:
                sg_txt = '{}   {} Sell(sg): {}'.format(df['timestamp'][last_row_index], coin, lastPrice)

                check_sg(sg_txt)
                send_signal(last_row_index, '{}{}{}'.format(coin, 'Sell(sg):', lastPrice))
                PNL.append([0, lastPrice])
                print(coin, df['timestamp'][last_row_index], 'Sell(sg):', lastPrice)
                StopTake.append([df['high'][previous_row_index] * 1, lastPrice * (1 - tp)])
                StopTake.append([lastPrice * (1 + st), lastPrice * (1 - tp)])
            else:
                percent = ((lastPrice / PNL[0][1]) - 1) * 100
                profit.append(round(percent - fee, 2))
                print(coin, df['timestamp'][last_row_index], 'Sell(sg):', lastPrice, round(profit[-1], 2))
                PNL.clear()
                StopTake.clear()

        elif df['in_uptrend'][last_row_index]:
            # elif trend1 is False:
            # if len(PNL) == 0:
            # if 1:
            if lastPrice > df['dema144'][last_row_index] or lastPrice > df['dema169'][last_row_index]:
                sg_txt = '{}   {} Buy(sg):  {}'.format(df['timestamp'][last_row_index], coin, lastPrice)
                check_sg(sg_txt)
                send_signal(last_row_index, '{}{}{}'.format(coin, 'Buy(sg): ', lastPrice))
                PNL.append([1, lastPrice])
                print(coin, df['timestamp'][last_row_index], 'Buy(sg): ', lastPrice)
                StopTake.append([df['low'][previous_row_index] * 1, lastPrice * (1 + tp)])
                StopTake.append([lastPrice * (1 - st), lastPrice * (1 + tp)])
            else:
                percent = -((lastPrice / PNL[0][1]) - 1) * 100
                profit.append(round(percent - fee, 2))
                print(coin, df['timestamp'][last_row_index], 'Buy(sg): ', lastPrice, round(profit[-1], 2))
                PNL.clear()
                StopTake.clear()

    if df['in_uptrend'][len(df['timestamp']) - 1] != df['in_uptrend'][len(df['timestamp']) - 2]:
        check_buy_sell_signals(len(df['timestamp']) - 1)

    
    print(coin)
    print(df['timestamp'][len(df['timestamp']) - 2], df['in_uptrend'][len(df['timestamp']) - 2])
    print(df['timestamp'][len(df['timestamp']) - 1], df['in_uptrend'][len(df['timestamp']) - 1])
    print('')
    


if __name__ == "__main__":
    coin = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'NEARUSDT', 'LUNABUSD', 'SOLUSDT', 'ICPUSDT', 'ANKRUSDT',
            'ADAUSDT', 'ATOMUSDT', 'AXSUSDT', 'BANDUSDT', 'ROSEUSDT', 'UNIUSDT', 'DOTUSDT', 'VETUSDT', 'AVAXUSDT',
            'MATICUSDT', 'SANDUSDT', 'XRPUSDT', 'GALAUSDT', 'DOGEUSDT', 'FTMUSDT', 'AUDIOUSDT', 'RUNEUSDT', 'LINKUSDT',
            'KNCUSDT', 'ENSUSDT', 'ZILUSDT', 'BNBUSDT', 'CHRUSDT', 'TLMUSDT', 'STORJUSDT', 'FTTUSDT', 'SHIBUSDT',
            'MANAUSDT', 'BCHUSDT', 'APEUSDT', 'GMTUSDT', 'DYDXUSDT', 'ALGOUSDT', 'EGLDUSDT', 'BNXUSDT']
    # coin = ['KNCUSDT']
    fpath = '***'

    from binance.client import Client

    while 1:
        current_time = datetime.now().strftime('%Y-%m-%d %H:00:00')
        cal_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") - timedelta(days=60)
        # time_range = ['2022-01-03 00:00:00', current_time]
        time_range = [cal_time.strftime('%Y-%m-%d %H:00:00'), current_time]
        print(time_range)

        UTC0 = [(datetime.strptime(str(time_range[0]), "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)).strftime(
            "%Y-%m-%d %H:%M:%S"),
            datetime.utcnow().strftime('%Y-%m-%d %H:00:00')]

        try:
            client = Client(api_key, api_secret)
            info = client.futures_exchange_info()
            # print(info['symbols'])
            positions = client.futures_position_information()
            print(len(positions))
            print(positions)

            

            client.futures_create_order(symbol='LTCUSDT',
                                        type='TAKE_PROFIT',  # TAKE_PROFIT  STOP_MARKET
                                        side='SELL',
                                        price=55,
                                        stopPrice=55,
                                        quantity=10,
                                        closePosition=False
                                        )

            
        except Exception as e:
            print(e)
            with open(fpath, 'r') as file:
                content = file.read()
                if str(e) in content:
                    file.close()
                else:
                    send_notice(str(e))
                    f = open(fpath, 'a')
                    f.write(str(e) + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
                    f.close()
        break

