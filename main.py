import datetime
import json
import time
import pandas as pd
import arrow
from os.path import exists
import numpy as np
import math
import os
import requests
from numpy import mean, isnan

def snp(year,month,day):
    setTime1()
    setTime2()
    data = pd.read_csv('constituents.csv')
    stocks = data['Symbol']
    label = []

    for stock in stocks:
        if os.path.exists(f'{stock}.json'):
            f = open(f'{stock}.json', 'r')
            json_object = json.load(f)
            try:
                if(json_object['Note']):
                    print('need to be deleted')
                    f.close()
                    os.remove(f'{stock}.json')
            except:
                print('ok')
    # exit(0)

    for count in range(300, len(stocks)-1, 2):
        print('1', count, stocks[count])
        print('2', count+1, stocks[count+1])
        lines(year, month, day, stocks[count], stocks[count+1])

def setTime1():
    global LAST_ACCESS1
    LAST_ACCESS1 = time.time()

def getTime1():
    return LAST_ACCESS1

def setTime2():
    global LAST_ACCESS2
    LAST_ACCESS2 = time.time()

def getTime2():
    return LAST_ACCESS2


def getJson(label):
    try:
        f = open(f'{label}.json', 'r')
        json_object = json.load(f)
        return json_object
    except FileNotFoundError as e:
        key = 'ENQ25ISH0JT8OR08'
        key2 = '10FVMMC7CFRA2XIQ'
        symbol = label
        api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
        api_url2 = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key2}'
        # convert data to json
        ts1 = time.time()

        if (ts1 - getTime1() < 12):
            time.sleep(ts1 - getTime1())
            setTime1()
        data = requests.get(api_url).json()
        json_object = json.dumps(data, indent=4)
        if (json_object['Note']):
            return None
        with open(f'{symbol}.json', 'w') as outfile:
            outfile.write(json_object)
        return json_object

def getJson2(label):
    try:
        f = open(f'{label}.json', 'r')
        json_object = json.load(f)
        return json_object
    except FileNotFoundError as e:
        key = 'ENQ25ISH0JT8OR08'
        key2 = '10FVMMC7CFRA2XIQ'
        symbol = label
        api_url2 = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key2}'
        # convert data to json
        ts2 = time.time()
        if (ts2 - getTime2()) < 12:
            time.sleep(ts2 - getTime2())
            setTime2()
        data = requests.get(api_url2).json()
        json_object = json.dumps(data, indent=4)
        if (json_object['Note']):
            return None
        with open(f'{symbol}.json', 'w') as outfile:
            outfile.write(json_object)
        return json_object

def lines(year,month,day,label, label2):
    data = getJson(label)
    data = getJson(label2)
    return
    start_date = datetime.date(int(year), int(month), int(day))
    string_date = start_date.strftime("%Y-%m-%d")
    my_col = []
    my_col.append('lows')
    my_col.append('high')
    indexes = []


    for ind in data['Time Series (Daily)']:
        if(ind < string_date):
            break
        l = float(data['Time Series (Daily)'][ind]['3. low'])
        h = float(data['Time Series (Daily)'][ind]['2. high'])
        if(l < minPrice):
            minPrice = l
        if (h > maxPrice):
            maxPrice = h

    slicePercent = 0.025
    first = True
    hrange = float(round(minPrice*(1+slicePercent),2))
    lrange = str(round(minPrice * (1 - slicePercent), 2))
    temp = hrange
    while(hrange < maxPrice):
        if(first == True):
            hrange = str(hrange)
            indexes.append(f'{lrange} - {hrange}')
            first = False
        else:
            temp = str(temp)
            indexes.append(f'{temp} - {hrange}')
        temp = float(hrange)
        hrange = float(round(temp*(1+slicePercent),2))
    df = pd.DataFrame(columns = my_col,index=indexes)
    df['low_avg'] = 'N/A'
    df['high_avg'] = 'N/A'
    first = True
    for ind in indexes:
        ind = ind.strip()
        ind_s = ind.split('-')
        ind1 = float(ind_s[0])
        ind2 = float(ind_s[1])
        df.loc[f'{ind1} - {ind2}', 'lows'] = 0
        df.loc[f'{ind1} - {ind2}', 'high'] = 0
        count_low = 0
        count_high = 0
        lows_list = []
        highs_list = []
        for day in range(0, 100):
            date = (start_date + datetime.timedelta(days=day)).isoformat()
            today = arrow.now().format('YYYY-MM-DD')
            if(date == today):
                break
            try:
                lowPrice = data['Time Series (Daily)'][f'{date}']['3. low']
                highPrice = data['Time Series (Daily)'][f'{date}']['2. high']
                lowPrice = round(float(lowPrice),2)
                if (first):
                    minimumPrice = lowPrice
                    first = False
                highPrice = round(float(highPrice),2)
                if (lowPrice < minimumPrice):
                    minimumPrice = lowPrice
                if (highPrice < minimumPrice):
                    minimumPrice = highPrice
                if (lowPrice >= ind1 and lowPrice <= ind2):
                    lows_list.append(lowPrice)
                    count_low+=1
                    df.loc[f'{ind1} - {ind2}' , 'lows'] = count_low
                if (highPrice >= ind1 and highPrice <= ind2):
                    highs_list.append(highPrice)
                    count_high+=1
                    df.loc[f'{ind1} - {ind2}' , 'high'] = count_high
            except:
                continue
        if(len(lows_list)>0):
            df.loc[f'{ind1} - {ind2}','low_avg'] = round(mean(lows_list),2)
        if(len(highs_list)>0):
            df.loc[f'{ind1} - {ind2}', 'high_avg'] = round(mean(highs_list), 2)

    df['diff'] = abs(df['lows'] - df['high'])
    df['total'] = df['lows'] + df['high']
    df['Strong Line'] = None
    for ind in df.index:
        try:
            if(isnan(df.loc[ind]['low_avg']) == False and isnan(df.loc[ind]['high_avg']) == False):
                df.loc[ind]['Strong Line'] = (df.loc[ind]['low_avg'] + df.loc[ind]['high_avg']) / 2
            elif(isnan(df.loc[ind]['low_avg']) and isnan(df.loc[ind]['high_avg']) == False):
                df.loc[ind]['Strong Line'] = df.loc[ind]['high_avg']
            elif(isnan(df.loc[ind]['low_avg']) == False and isnan(df.loc[ind]['high_avg'])):
                df.loc[ind]['Strong Line'] = df.loc[ind]['low_avg']
            else:
                df.loc[ind]['Strong Line'] = None
        except:
            continue

    df = df.sort_values(by=['total','diff'], ascending= False)

    length = len(df)*0.25
    i=0
    open1 = float(data['Time Series (Daily)']['2022-07-27']['1. open'])
    open2 = float(data['Time Series (Daily)']['2022-07-28']['1. open'])
    for row in df.index:
        if(i >= length):
            break
        i = i + 1
        try:
            line = round(df.loc[row]['Strong Line'],2)
            if(open1 < line and open2 > line):
                print(label,line)
        except:
            continue

def daily_volume(year,month,day):
    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_daily = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_daily).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}_daily.json', 'w') as outfile:
        outfile.write(json_object)
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    indexes = []
    my_col = ['Daily Volume','Color']
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns=my_col, index=indexes)

    for ind in df.index:
        vol = data['Time Series (Daily)'][ind]['5. volume']
        vol = str(round((int(vol) / 1000000),2)) + 'M'
        df.loc[ind]['Daily Volume'] = vol
        if(data['Time Series (Daily)'][ind]['4. close'] > data['Time Series (Daily)'][ind]['1. open']):
            df.loc[ind]['Color'] = 'Green'
        else:
            df.loc[ind]['Color'] = 'Red'

    first = df.index[0]
    second = df.index[1]
    third = df.index[2]
    forth = df.index[3]
    if(df.loc[first]['Daily Volume'] >= df.loc[second]['Daily Volume'] and
        df.loc[second]['Daily Volume'] >= df.loc[third]['Daily Volume']):
        if(df.loc[third]['Daily Volume'] >= df.loc[forth]['Daily Volume']):
            daily_summary = '4 days of volume up'
        else:
            daily_summary = '3 days of volume up'

    elif(df.loc[first]['Daily Volume'] <= df.loc[second]['Daily Volume'] and
        df.loc[second]['Daily Volume'] >= df.loc[third]['Daily Volume']):
        if (df.loc[third]['Daily Volume'] >= df.loc[forth]['Daily Volume']):
            daily_summary = 'volume down after 3 days'
        else:
            daily_summary = 'volume start to slow'

    elif (df.loc[first]['Daily Volume'] >= df.loc[second]['Daily Volume'] and
          df.loc[second]['Daily Volume'] <= df.loc[third]['Daily Volume']):
        if (df.loc[third]['Daily Volume'] <= df.loc[forth]['Daily Volume']):
            daily_summary = 'volume up after 3 days'
        else:
            daily_summary = 'volume start to rise'
    else:
        daily_summary = 'Nan'

    print(df)
    print('\nDaily summary - ', daily_summary)
def weekly_volume(year,month,day):
    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_weekly = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={key}'
    # convert data to json
    data = requests.get(api_weekly).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}_weekly.json', 'w') as outfile:
        outfile.write(json_object)
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    indexes = []
    my_col = ['Weekly Volume', 'Color']

    for key in data['Weekly Time Series']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns=my_col, index=indexes)

    for ind in df.index:
        vol = data['Weekly Time Series'][ind]['5. volume']
        vol = str(round((int(vol) / 1000000), 2)) + 'M'
        df.loc[ind]['Weekly Volume'] = vol
        if (data['Weekly Time Series'][ind]['4. close'] > data['Weekly Time Series'][ind]['1. open']):
            df.loc[ind]['Color'] = 'Green'
        else:
            df.loc[ind]['Color'] = 'Red'

    first = df.index[0]
    second = df.index[1]
    third = df.index[2]
    forth = df.index[3]

    if (df.loc[first]['Weekly Volume'] >= df.loc[second]['Weekly Volume'] and
            df.loc[second]['Weekly Volume'] >= df.loc[third]['Weekly Volume']):
        if (df.loc[third]['Weekly Volume'] >= df.loc[forth]['Weekly Volume']):
            weekly_summary = '4 weeks of volume up'
        else:
            weekly_summary = '3 weeks of volume up'

    elif (df.loc[first]['Weekly Volume'] <= df.loc[second]['Weekly Volume'] and
          df.loc[second]['Weekly Volume'] >= df.loc[third]['Weekly Volume']):
        if (df.loc[third]['Weekly Volume'] >= df.loc[forth]['Weekly Volume']):
            weekly_summary = 'volume down after 3 weeks'
        else:
            weekly_summary = 'volume start to slow'

    elif (df.loc[first]['Weekly Volume'] >= df.loc[second]['Weekly Volume'] and
          df.loc[second]['Weekly Volume'] <= df.loc[third]['Weekly Volume']):
        if (df.loc[third]['Weekly Volume'] <= df.loc[forth]['Weekly Volume']):
            weekly_summary = 'volume up after 3 weeks'
        else:
            weekly_summary = 'volume start to rise'
    else:
        weekly_summary = 'Nan'

    print(df)
    print('\nWeekly Summary - ', weekly_summary)
def ema20(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ema = 20
    MULTIPLIER = 2 / (ema + 1)
    my_col = [f'EMA-{ema}']
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    #today = arrow.now().format('YYYY-MM-DD')
    count = 0
    indexes = []
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    indexes.reverse()
    df = pd.DataFrame(columns=my_col,index=indexes)
    for row in df.index:
        start_date = str(start_date)
        if(row == start_date):
            df.loc[str(start_date), 'EMA-20'] = 80.63
        else:
            try:
                closingPrice = float(data['Time Series (Daily)'][f'{row}']['4. close'])
                df.loc[row,'EMA-20'] = round(closingPrice * MULTIPLIER + (df.loc[temp,'EMA-20'] * (1-MULTIPLIER)),2)
            except Exception as e:
                continue
        temp = row
    print(df)
def ema50(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ema = 50
    MULTIPLIER = 2 / (ema + 1)
    my_col = [f'EMA-{ema}']
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    #today = arrow.now().format('YYYY-MM-DD')
    count = 0
    indexes = []
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    indexes.reverse()
    df = pd.DataFrame(columns=my_col,index=indexes)
    for row in df.index:
        start_date = str(start_date)
        if(row == start_date):
            df.loc[str(start_date), f'EMA-{ema}'] = 95.83
        else:
            try:
                closingPrice = float(data['Time Series (Daily)'][f'{row}']['4. close'])
                df.loc[row,f'EMA-{ema}'] = round(closingPrice * MULTIPLIER + (df.loc[temp,f'EMA-{ema}'] * (1-MULTIPLIER)),2)
            except Exception as e:
                continue
        temp = row
    print(df)
def ema100(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ema = 100
    MULTIPLIER = 2 / (ema + 1)
    my_col = [f'EMA-{ema}']
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    #today = arrow.now().format('YYYY-MM-DD')
    count = 0
    indexes = []
    i = 0
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    indexes.reverse()
    df = pd.DataFrame(columns=my_col,index=indexes)
    for row in df.index:
        start_date = str(start_date)
        if(row == start_date):
            df.loc[str(start_date), f'EMA-{ema}'] = 118.75
        else:
            try:
                closingPrice = float(data['Time Series (Daily)'][f'{row}']['4. close'])
                df.loc[row,f'EMA-{ema}'] = round(closingPrice * MULTIPLIER + (df.loc[temp,f'EMA-{ema}'] * (1-MULTIPLIER)),2)
            except Exception as e:
                continue
        temp = row
    print(df)
def ema200(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ema = 200
    MULTIPLIER = 2 / (ema + 1)
    my_col = [f'EMA-{ema}']
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    #today = arrow.now().format('YYYY-MM-DD')
    count = 0
    indexes = []
    i = 0
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    indexes.reverse()
    df = pd.DataFrame(columns=my_col,index=indexes)
    for row in df.index:
        start_date = str(start_date)
        if(row == start_date):
            df.loc[str(start_date), f'EMA-{ema}'] = 180.08
        else:
            try:
                closingPrice = float(data['Time Series (Daily)'][f'{row}']['4. close'])
                df.loc[row,f'EMA-{ema}'] = round(closingPrice * MULTIPLIER + (df.loc[temp,f'EMA-{ema}'] * (1-MULTIPLIER)),2)
            except Exception as e:
                continue
        temp = row
    print(df)
def ma20(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ma = 20
    my_col = [f'MA-{ma}']
    start_date = datetime.date(int(year), int(month), int(day))
    d = start_date - datetime.timedelta(days = ma+10)
    d = d.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")
    indexes = []
    list_of_prices = []
    for key in data['Time Series (Daily)']:
        if key < d:
            break
        list_of_prices.append(float(data['Time Series (Daily)'][key]['4. close']))

    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns = my_col,index=indexes)
    i = 0

    for ind in df.index:
        avg = mean(list_of_prices[i:i+20])
        df.loc[ind][f'MA-{ma}'] = round(avg,2)
        i = i + 1

    print(df)
def ma50(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ma = 50
    my_col = [f'MA-{ma}']
    start_date = datetime.date(int(year), int(month), int(day))
    d = start_date - datetime.timedelta(days = ma+10)
    d = d.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")
    indexes = []
    list_of_prices = []
    for key in data['Time Series (Daily)']:
        if key < d:
            break
        list_of_prices.append(float(data['Time Series (Daily)'][key]['4. close']))

    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns = my_col,index=indexes)
    i = 0

    for ind in df.index:
        avg = mean(list_of_prices[i:i+ma])
        df.loc[ind][f'MA-{ma}'] = round(avg,2)
        i = i + 1

    print(df)
def ma100(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ma = 100
    my_col = [f'MA-{ma}']
    start_date = datetime.date(int(year), int(month), int(day))
    d = start_date - datetime.timedelta(days = ma+10)
    d = d.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")
    indexes = []
    list_of_prices = []
    for key in data['Time Series (Daily)']:
        if key < d:
            break
        list_of_prices.append(float(data['Time Series (Daily)'][key]['4. close']))

    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns = my_col,index=indexes)
    i = 0

    for ind in df.index:
        avg = mean(list_of_prices[i:i+ma])
        df.loc[ind][f'MA-{ma}'] = round(avg,2)
        i = i + 1

    print(df)
def ma200(year,month,day):

    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    ma = 200
    my_col = [f'MA-{ma}']
    start_date = datetime.date(int(year), int(month), int(day))
    d = start_date - datetime.timedelta(days = ma+10)
    d = d.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")
    indexes = []
    list_of_prices = []
    for key in data['Time Series (Daily)']:
        if key < d:
            break
        list_of_prices.append(float(data['Time Series (Daily)'][key]['4. close']))

    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns = my_col,index=indexes)
    i = 0

    for ind in df.index:
        avg = mean(list_of_prices[i:i+ma])
        df.loc[ind][f'MA-{ma}'] = round(avg,2)
        i = i + 1

    print(df)
def rsi(year,month,day):
    key = 'FY4LIXP2TPH6STPO'
    symbol = 'UPST'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    start_date = datetime.date(int(year), int(month), int(day))
    d = start_date - datetime.timedelta(days=30)
    d = d.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")
    percentages = []
    dates = []
    for key in data['Time Series (Daily)']:
        if key < d:
            break
        dates.append(key)
    for i in range(0,len(dates)-1):
        todayClose = float(data['Time Series (Daily)'][dates[i]]['4. close'])
        yesterdayClose = float(data['Time Series (Daily)'][dates[i+1]]['4. close'])
        closing = todayClose - yesterdayClose
        percentages.append(closing)

    indexes = []
    my_col = ['RSI', 'Status']
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)

    df = pd.DataFrame(columns=my_col, index=indexes)
    count = 0
    for ind in df.index:
        up = 0
        down = 0
        count_up = 0
        count_down = 0
        for i in range(count,14+count):
            if(percentages[i] > 0):
                count_up = count_up+1
                up = up + percentages[i]
            elif(percentages[i] < 0):
                count_down = count_down+1
                down = down + abs(percentages[i])
        avgUp = (up/14)
        avgDown = (down/14)
        rs = avgUp / avgDown
        rsi = 100 - (100/(1+rs))
        df.loc[ind]['RSI'] = round(rsi,2)
        count = count + 1

    for ind in df.index:
        if( df.loc[ind]['RSI'] <= 40 and df.loc[ind]['RSI'] >= 20):
            df.loc[ind]['Status'] = 'OS'
        elif (df.loc[ind]['RSI'] < 20):
            df.loc[ind]['Status'] = 'Extreme Oversold'
        elif(df.loc[ind]['RSI'] >= 78):
            df.loc[ind]['Status'] = 'Extreme Overbought'
        elif(df.loc[ind]['RSI'] <78 and df.loc[ind]['RSI'] >= 73):
            df.loc[ind]['Status'] = 'OB'
        else:
            df.loc[ind]['Status'] = 'Natural'

    print(df)
def daily_candles(year,month,day):
    key = 'FY4LIXP2TPH6STPO'
    symbol = 'AAPL'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    my_col = ['Percents','Candle']
    indexes = []
    for key in data['Time Series (Daily)']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns=my_col, index=indexes)
    df['Candle'] = 'None'
    i = -1
    for ind in df.index:
        i = i +1
        c = float(data['Time Series (Daily)'][ind]['4. close'])
        o = float(data['Time Series (Daily)'][ind]['1. open'])
        h = float(data['Time Series (Daily)'][ind]['2. high'])
        l = float(data['Time Series (Daily)'][ind]['3. low'])
        if (o > c):
            redCandle = True
            greenCandle = False
        else:
            redCandle = False
            greenCandle = True

        #test hammer candle (נר פטיש)
        if(greenCandle):
            candlestick_percent = ((h - l) / l)*100
            if(((o-l)/l)*100 / round(candlestick_percent,2) > 0.3 and ((h-c)/c)*100 / round(candlestick_percent,2) < 0.10):
                if (df.loc[ind]['Candle'] == 'None'):
                    df.loc[ind]['Candle'] = 'Hammer'
                else:
                    df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Hammer'

        #test shooting star (כוכב נופל)
        if(redCandle):
            candlestick_percent = ((h-l)/l)*100
            if(((h-o)/o)*100 / round(candlestick_percent,2) > 0.7 and ((c-l)/l)*100 / round(candlestick_percent,2) < 0.08):
                if (df.loc[ind]['Candle'] == 'None'):
                    df.loc[ind]['Candle'] = 'Shooting star'
                else:
                    df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Shooting star'

        if(greenCandle):
            candlestick_percent = ((h-l)/l)*100
            if (((h-c) / c) * 100 / round(candlestick_percent, 2) > 0.7 and ((o - l) / l) * 100 / round(candlestick_percent, 2) < 0.08):
                if (df.loc[ind]['Candle'] == 'None'):
                    df.loc[ind]['Candle'] = 'Shooting star'
                else:
                    df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Shooting star'

        #test bullish engulfing (נר בולען)
        try:
            previous_opening =  float(data['Time Series (Daily)'][df.index[i+1]]['1. open'])
            previous_closing =  float(data['Time Series (Daily)'][df.index[i+1]]['4. close'])
            df.loc[ind]['Percents'] = str(round(((c - previous_closing) / previous_closing *100),2)) + '%'
            if(previous_closing > previous_opening):
                prev_candle = 'Green'
            else:
                prev_candle = 'Red'

            if(prev_candle == 'Red'):
                if(o<previous_closing and c > previous_opening):
                    if(df.loc[ind]['Candle'] == 'None'):
                        df.loc[ind]['Candle'] = 'Bullish Engulfing'
                    else:
                        df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Bullish Engulfing'

            if(prev_candle == 'Green'):
                if(o > previous_closing and c < previous_opening):
                    if (df.loc[ind]['Candle'] == 'None'):
                        df.loc[ind]['Candle'] = 'Bearish Engulfing'
                    else:
                        df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Bearish Engulfing'
        except:
            print('temporary exception', ind)

        #test Dodji candle (נר דודג'י)
        if(redCandle):
            candlePercent1 = ((o-c) / c)*100
            up_per = (((h-o) / o)*100)
            down_per = (((c-l) / l)*100)
            condition2 = abs(up_per - down_per)
            if(up_per > down_per):
                condition3 = down_per / up_per
            else:
                condition3 = up_per / down_per

        else:
            candlePercent1 = ((c-o) / o)*100
            condition2 = abs((((h-c) / c)*100) - (((o-l) / l)*100))

        condition1 = ((h - l) / l) * 100
        if(condition1 > candlePercent1 * 10 and (condition2 <= 1.2 or condition3 > 0.8)):
            if (df.loc[ind]['Candle'] == 'None'):
                df.loc[ind]['Candle'] = 'Dodji'
            else:
                df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Dodji'

        elif (condition1 > candlePercent1 * 9 and (condition2 <= 2 or condition3 > 0.6)):
            if (df.loc[ind]['Candle'] == 'None'):
                df.loc[ind]['Candle'] = 'Undecided'
            else:
                df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Undecided'

        if(df.loc[ind]['Candle'] == 'None'):
            if(greenCandle):
                df.loc[ind]['Candle'] = 'Green'
            else:
                df.loc[ind]['Candle'] = 'Red'
    print(df)
def weekly_candles(year,month,day):
    key = 'FY4LIXP2TPH6STPO'
    symbol = 'AAPL'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={key}'
    # convert data to json
    data = requests.get(api_url).json()
    json_object = json.dumps(data, indent=4)
    with open(f'{symbol}.json', 'w') as outfile:
        outfile.write(json_object)
    start_date = datetime.date(int(year), int(month), int(day))
    start_date = start_date.strftime("%Y-%m-%d")
    my_col = ['Percents','Candle']
    indexes = []
    for key in data['Weekly Time Series']:
        if key < start_date:
            break
        indexes.append(key)
    df = pd.DataFrame(columns=my_col, index=indexes)
    df['Candle'] = 'None'
    i = -1
    for ind in df.index:
        i = i +1
        c = float(data['Weekly Time Series'][ind]['4. close'])
        o = float(data['Weekly Time Series'][ind]['1. open'])
        h = float(data['Weekly Time Series'][ind]['2. high'])
        l = float(data['Weekly Time Series'][ind]['3. low'])
        if (o > c):
            redCandle = True
            greenCandle = False
        else:
            redCandle = False
            greenCandle = True

        #test hammer candle (נר פטיש)
        if(greenCandle):
            candlestick_percent = ((h - l) / l)*100
            if(((o-l)/l)*100 / round(candlestick_percent,2) > 0.3 and ((h-c)/c)*100 / round(candlestick_percent,2) < 0.10):
                if (df.loc[ind]['Candle'] == 'None'):
                    df.loc[ind]['Candle'] = 'Hammer'
                else:
                    df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Hammer'

        #test shooting star (כוכב נופל)
        if(redCandle):
            candlestick_percent = ((h-l)/l)*100
            if(((h-o)/o)*100 / round(candlestick_percent,2) > 0.7 and ((c-l)/l)*100 / round(candlestick_percent,2) < 0.08):
                if (df.loc[ind]['Candle'] == 'None'):
                    df.loc[ind]['Candle'] = 'Shooting star'
                else:
                    df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Shooting star'

        if(greenCandle):
            candlestick_percent = ((h-l)/l)*100
            if (((h-c) / c) * 100 / round(candlestick_percent, 2) > 0.7 and ((o - l) / l) * 100 / round(candlestick_percent, 2) < 0.08):
                if (df.loc[ind]['Candle'] == 'None'):
                    df.loc[ind]['Candle'] = 'Shooting star'
                else:
                    df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Shooting star'

        #test bullish engulfing (נר בולען)
        try:
            previous_opening =  float(data['Weekly Time Series'][df.index[i+1]]['1. open'])
            previous_closing =  float(data['Weekly Time Series'][df.index[i+1]]['4. close'])
            df.loc[ind]['Percents'] = str(round(((c - previous_closing) / previous_closing *100),2)) + '%'
            if(previous_closing > previous_opening):
                prev_candle = 'Green'
            else:
                prev_candle = 'Red'

            if(prev_candle == 'Red'):
                if(o<previous_closing and c > previous_opening):
                    if(df.loc[ind]['Candle'] == 'None'):
                        df.loc[ind]['Candle'] = 'Bullish Engulfing'
                    else:
                        df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Bullish Engulfing'

            if(prev_candle == 'Green'):
                if(o > previous_closing and c < previous_opening):
                    if (df.loc[ind]['Candle'] == 'None'):
                        df.loc[ind]['Candle'] = 'Bearish Engulfing'
                    else:
                        df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Bearish Engulfing'
        except:
            print('temporary exception', ind)

        #test Dodji candle (נר דודג'י)
        if(redCandle):
            candlePercent1 = ((o-c) / c)*100
            up_per = (((h-o) / o)*100)
            down_per = (((c-l) / l)*100)
            condition2 = abs(up_per - down_per)
            if(up_per > down_per):
                condition3 = down_per / up_per
            else:
                condition3 = up_per / down_per

        else:
            candlePercent1 = ((c-o) / o)*100
            condition2 = abs((((h-c) / c)*100) - (((o-l) / l)*100))

        condition1 = ((h - l) / l) * 100
        if(condition1 > candlePercent1 * 10 and (condition2 <= 1.2 or condition3 > 0.8)):
            if (df.loc[ind]['Candle'] == 'None'):
                df.loc[ind]['Candle'] = 'Dodji'
            else:
                df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Dodji'

        elif (condition1 > candlePercent1 * 9 and (condition2 <= 2 or condition3 > 0.6)):
            if (df.loc[ind]['Candle'] == 'None'):
                df.loc[ind]['Candle'] = 'Undecided'
            else:
                df.loc[ind]['Candle'] = df.loc[ind]['Candle'] + ',Undecided'

        if(df.loc[ind]['Candle'] == 'None'):
            if(greenCandle):
                df.loc[ind]['Candle'] = 'Green'
            else:
                df.loc[ind]['Candle'] = 'Red'
    print(df)
# def gaps(year,month,day):



if __name__ == '__main__':
    # year = input('year = \n')
    # month = input('month = \n')
    # day = input('day = \n')
    year = 2022
    month = 4
    day = 14
    snp(year,month,day)
    #lines(year, month, day)
    #volume(year,month,day)
    #ema20(year,month,day)
    #ema50(year,month,day)
    #ema100(year, month, day)
    #ema200(year, month, day)
    #ma20(year,month,day)
    #ma50(year,month,day)
    #ma100(year, month, day)
    #ma200(year, month, day)
    #rsi(year,month,day)
    #daily_candles(year,month,day)
    #weekly_candles(year,month,day)