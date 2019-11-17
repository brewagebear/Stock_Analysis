import os
import datetime
import json
import pandas as pd
import stock
import pretreatment
import urllib.parse
from pymongo import MongoClient

STOCKDATADIR = 'D:/Workspace/Python/Crawling/data/'
ARTICLEDATADIR = 'D:/Workspace/Python/Crawling/newscrawling_result/'

def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)


    return conn[db]


def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df

def read_dir(flag):
    if flag == 0:
        path = STOCKDATADIR
    else:
        path = ARTICLEDATADIR

    files = os.listdir(path)

    # 파일의 수정시간을 타임스탬프로 출력한 후 내림차순으로 정렬하였다.
    for i in range(0, len(files)):
        for j in range(0, len(files)):
            if datetime.datetime.fromtimestamp(os.path.getmtime(path + files[i])) > \
                    datetime.datetime.fromtimestamp(os.path.getmtime(path + files[j])):
                (files[i], files[j]) = (files[j], files[i])

    return files[0]

def insert_stock_data(filename, stockname):
    stockinfo_df = stock.excel_to_pandas()
    url = stock.get_stockInfo(stock_name, stockinfo_df)
    result = stock.get_stockpriceInfo(stock_name, url)
    stock_json = json.loads(result.to_json(orient='records'))
    print("======== STOCK JSON ========\n")
    print(stock_json)
    db_client = _connect_mongo('localhost', 27017, '', '', 'stock_info')
    collection = 'Stocks'
    db = db_client[collection]
    db.remove()
    db.insert_many(stock_json)

def insert_article_data(filename):
    df = pd.read_excel(ARTICLEDATADIR + filename, sheet_name='Sheet1')
    stock_json = json.loads(df.to_json(orient='records'))
    db_client = _connect_mongo('localhost', 27017, '', '', 'article_info')
    collection = 'Articles'
    db = db_client[collection]
    db.remove()
    db.insert_many(stock_json)

def insert_pretreatment_dataset():
    #기사 감성분석
    sentiment_df = pretreatment.sentiment_analysis(pretreatment.read_newfile(ARTICLEDATADIR))
    #감성분석된 기사 정보와 주식정보를 결합
    print("========== DB Sentiment_df ==========\n")
    print(sentiment_df)
    print("========== DB Stock_df ==========\n")
    print(read_mongo('stock_info', 'Stocks'))
    stock.get_stockpriceInfo()
    df = pretreatment.pretreatment_df()
    #JSON으로 생성
    result_json = json.loads(df.to_json(orient='records'))
    db_client = _connect_mongo('localhost', 27017, '', '', 'resultSet')
    collection = 'Results'
    db = db_client[collection]
    db.remove()
    db.insert_many(result_json)

if __name__ == '__main__':
    stock_file = read_dir(0)
    article_file = read_dir(1)
    print("수집할 종목명을 입력해주세요 : ")
    stock_name = input()
    encoded_stock_name = urllib.parse.quote(stock_name)

    insert_stock_data(stock_file, encoded_stock_name)
    print(read_mongo('stock_info', 'Stocks'))
    insert_article_data(article_file)
    print(read_mongo('article_info', 'Articles'))
    insert_pretreatment_dataset()
    print(read_mongo('resultSet', 'Results'))