import os
import pandas as pd
import plotly.offline as offline
import plotly.graph_objs as go
import urllib
import json
from requests import get
from datetime import datetime

RESULT_PATH = '/Users/dailyworker/workspace/python/Stock_Analysis/stockcrawling_result/'
now = datetime.now()  # 파일이름 현 시간으로 저장하기

headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cache-Control':'no-cache',
            'Cookie': 'KAKAO_STOCK_CHART_ENABLED_INDICATORS=[%22sma%22%2C%22column%22]; KAKAO_STOCK_RECENT=[%22A028300%22]; recentMenus=[{%22destination%22:%22current%22%2C%22title%22:%22%ED%98%84%EC%9E%AC%EA%B0%80%22}]; _dfs=czlWa0lKU3ZML1pwSzNjdkhCUzlhaExHSytXYUNJRGNVc3I0b3Q0b1YyWk41MnNFdlExaVlmSDhQd3BtVkFtUG1HczlnV3o4c29QRXBmdVh0dE1pZFE9PS0tVi9ocVRaeTlzbWFxZURvcGNHVnpQUT09--b9742b28597832efd3d55fd3bf2194d0d704345a',
            'Host': 'finance.daum.net',
            'DNT' : '1',
            'TE'  : 'Trailers',
            'X-Requested-With' : 'XMLHttpRequest',
            'If-None-Match': 'W/"9231d119fd6cb8154e2036913d1b181f"',
            'Referer': 'https://finance.daum.net/global/quotes/US.DJI',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
            }

def download_stockList(url, file_name = None):
    if not file_name:
        file_name = url.split('/')[1]

    with open(file_name, "wb") as file:
        res = get(url)
        file.write(res.content)


def get_stockInfo(item_name):
    if isinstance(item_name, int) == True:
        if item_name == 1:
            url = "https://finance.daum.net/api/market_index/days?market=KOSPI"
        elif item_name == 2:
            url = "https://finance.daum.net/api/market_index/days?market=KOSPI_200"
        else :
            url = "https://finance.daum.net/api/market_index/days?market=KOSDAQ"
    else:
        if item_name == 'WR.RUI@RTSI':
            url = "http://finance.daum.net/api/quote/{code}/days?symbolCode=WR.RUI%40RTSI".format(code=item_name)
        else:
            url = "http://finance.daum.net/api/quote/{code}/days?symbolCode={code}".format(code=item_name)
        print("요청 URL = {}".format(url))
    return url

def get_stockpriceInfo(url):
    df = pd.DataFrame()
    try:
        for page in range(1, 172):
            pg_url = '{url}&page={page}&perPage=10&pagination=true'.format(url=url, page=page)
            print(pg_url)
            res = get(pg_url, headers=headers)
            res.encoding = 'utf-8'
            res = json.loads(res.text)
            print(res)
            df = df.append(pd.DataFrame(res['data']), ignore_index=True)
            #df = df.append(pd.read_html(res.content, header=0)[0], ignore_index=True)
    except Exception as e:
        print(e)

    df = df.dropna()
    df = df.rename(columns= {'날짜' : 'date', '종가' : 'tradePrice', '전일비' : 'changePrice', '시가' : 'openingPrice', '고가' : 'highPrice', '저가' : 'lowPrice'})
    #df[['close', 'diff', 'open', 'high', 'low', 'volume']] \
    #    = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date'], ascending= True)
    print(df)
    return df

def make_excel(df, stock_name, index_flag):
    if index_flag == 2:
        stock_name = change_global_indexName(stock_name)
    xlsx_outputFileName = '%s-%s-%s %s시 %s분 %s초 result(%s).xlsx' % (
        now.year, now.month, now.day, now.hour, now.minute, now.second, stock_name)

    df.to_excel(os.path.join(RESULT_PATH, xlsx_outputFileName), encoding='utf-8')

def change_global_indexName(item_name):
    if item_name == 'CN000001':
        item_name = '중국 - 상해종합'
    elif item_name == 'JP.NI225':
        item_name = '일본 - 니케이225'
    elif item_name == 'US.DJI':
        item_name = '미국 - 다우 산업'
    elif item_name == 'US.COMP':
        item_name = '미국 - 나스닥 종합'
    else:
        item_name = '러시아 - RTS'
    return item_name

def draw_graph(df, item_name, index_flag):
    if index_flag == 2:
        item_name = change_global_indexName(item_name)
    # 그래프를 생성. x축에는 날짜, y축에는 종가, 그래프 이름은 item_name에서 가져온다.
    trace = go.Scatter(x=df.date, y=df.tradePrice, name=item_name)
    # 위에 데이터 정보를 data라는 객체의 리스트로 담아준다.
    data = [trace]
    # 레이아웃 잡기
    layout = dict(title='{}의 종가(close) Time Series'.format(item_name),  # 타이틀 생성.
                      xaxis=dict(
                          rangeselector=dict(
                              buttons=list([  # 한 달, 세 달, 6달, 전체 종가를 보여주는 버튼을 만든다.
                                  dict(
                                      count=1,  # 1개씩 센다. 여기서는 step='month'이기 때문에 1달이 된다.
                                      label='1m',  # 라벨 이름. 그래프에 1m이라는 버튼을 만든다.
                                      step='month',  # 한 달을 기준으로 잡아서 count를 센다.
                                      stepmode='backward'),  # 가장 최근 데이터부터 센다. forward는 가장 오래된 데이터부터 센다.
                                  dict(
                                      count=3,
                                      label='3m',
                                      step='month',
                                      stepmode='backward'),
                                  dict(
                                      count=6,
                                      label='6m',
                                      step='month',
                                      stepmode='backward'),
                                  dict(step='all')])
                          ),  # 전체 데이터를 출력한다. step='all'은 label을 설정할 수 없다.
                          rangeslider=dict(),
                          type='date'
                      )
                  )

    # graph object에 data, layout을 저장한다.
    fig = go.Figure(data=data, layout=layout)
    # 플롯을 출력한다.
    offline.plot(fig)


if __name__ == '__main__':

    print("수집할 국가를 선택해주세요 (다음 증권 기준) 1. 국내 / 2. 국외 : ")
    index_flag = input()
    index_flag = int(index_flag)

    if int(index_flag) == 1 :
        print("수집할 증시를 선택해주세요 (다음 증권 기준) 1. 코스피 / 2. 코스피200 / 3. 코스닥 : ")
        korea_index_flag = input()
        korea_index_flag = int(korea_index_flag)
        url = get_stockInfo(korea_index_flag)
        result = get_stockpriceInfo(url)

        if korea_index_flag == 1:
            stock_name = 'KOSPI'
        elif korea_index_flag == 2:
            stock_name = 'KOSPI_200'
        else:
            stock_name = 'KOSDAQ'
    else:
        print("수집할 국제 증시명을 (다음 증권 기준) 입력해주세요 : ")
        stock_name = input()
        url = get_stockInfo(stock_name)
        result = get_stockpriceInfo(url)

    make_excel(result, stock_name, index_flag)
    draw_graph(result, stock_name, index_flag)
















