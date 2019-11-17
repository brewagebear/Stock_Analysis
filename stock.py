import pandas as pd
import plotly.offline as offline
import plotly.graph_objs as go
import urllib
from requests import get
from datetime import datetime

RESULT_PATH = 'D:/Workspace/Python/Crawling/data/'
now = datetime.now()  # 파일이름 현 시간으로 저장하기


def download_stockList(url, file_name = None):
    if not file_name:
        file_name = url.split('/')[1]

    with open(file_name, "wb") as file:
        res = get(url)
        file.write(res.content)

def excel_to_pandas():
    # https://stackoverflow.com/a/24725123/7250379 로 해결 본래는 pd.read_excel 사용
    stockinfo_df = pd.read_html("상장법인목록.xls", header=0)[0]
    stockinfo_df.종목코드 = stockinfo_df.종목코드.map('{:06d}'.format)
    stockinfo_df = stockinfo_df[['회사명', '종목코드']]
    stockinfo_df = stockinfo_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    return stockinfo_df

def get_stockInfo(item_name, stockinfo_df):
    code = stockinfo_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = "http://finance.naver.com/item/sise_day.nhn?code={code}".format(code=code)

    print("요청 URL = {}".format(url))
    return url

def get_stockpriceInfo(item_list, url):
    df = pd.DataFrame()
    try:
        for page in range(1, 21):
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            res = get(pg_url)
            res.encoding = 'utf-8'
            df = df.append(pd.read_html(res.content, header=0)[0], ignore_index=True)
    except Exception as e:
        print(e)

    df = df.dropna()
    df = df.rename(columns= {'날짜' : 'date', '종가' : 'close', '전일비' : 'diff', '시가' : 'open', '고가' : 'high', '저가' : 'low', '거래량' : 'volume'})
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] \
        = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date'], ascending= True)
    print(df)
    return df

def make_excel(df):
    xlsx_outputFileName = '%s-%s-%s  %s시 %s분 %s초 result(stock).xlsx' % (
        now.year, now.month, now.day, now.hour, now.minute, now.second)

    df.to_excel(RESULT_PATH + xlsx_outputFileName, encoding='utf-8')

def draw_graph(df, item_name):
    # 그래프를 생성. x축에는 날짜, y축에는 종가, 그래프 이름은 item_name에서 가져온다.
    trace = go.Scatter(x=df.date, y=df.close, name=item_name)
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
    url = "http://kind.krx.co.kr/corpgeneral/corpList.do?method=download"
    file_name = "상장법인목록.xls"

    stockinfo_df = excel_to_pandas()
    print("수집할 종목명을 입력해주세요 : ")
    stock_name = input()

    url = get_stockInfo(stock_name, stockinfo_df)
    result = get_stockpriceInfo(stock_name,url)
    make_excel(result)
    draw_graph(result, stock_name)
















