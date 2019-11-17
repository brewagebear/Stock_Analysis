# -*- coding: utf-8 -*-
import os
import datetime
import sys
import csv
import stock
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets, linear_model
import tkinter as tk
import statsmodels.api as sm
from konlpy.tag import Twitter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DATADIR = 'D:/Workspace/Python/Crawling/newscrawling_result/'
DATADIR2 = 'D:/Workspace/Python/Crawling/data/'
NEWFILE = ''

def read_newfile(dir):
    files = os.listdir(dir)
    # listdir() 해당 경로의 파일을 리스트로 반환


    # 파일의 수정시간을 타임스탬프로 출력한 후 내림차순으로 정렬하였다.
    for i in range(0, len(files)):
        for j in range(0, len(files)):
            if datetime.datetime.fromtimestamp(os.path.getmtime(dir + files[i])) > \
                    datetime.datetime.fromtimestamp(os.path.getmtime(dir + files[j])):
                (files[i], files[j]) = (files[j], files[i])

    print(files[0])
    NEWFILE = files[0]
    return NEWFILE

def get_sentimentWeight(word_list):
    table = dict()
    negative = 0.0
    neutral = 0.0
    positive = 0.0
    with open('KOSAC.csv', 'r', encoding='UTF8') as polarity:
        next(polarity)
        for line in csv.reader(polarity):
            key = str()
            for word in line[0].split(';'):
                key += word.split('/')[0]
                table[key] = {'Neg': line[3], 'Neut': line[4], 'Pos': line[6]}
    for word in word_list:
        try:
            if table[word]:
                negative += float(table[word]['Neg'])
                neutral += float(table[word]['Neut'])

                positive += float(table[word]['Pos'])
        except KeyError:
            pass
    #print( '긍정 : %s, 중립 : %s, 부정 : %s' % (positive, neutral, negative))
    result = [positive, neutral, negative]
    print(result)
    return result

def sentiment_analysis(db):
    PATH = DATADIR + db
    data = []
    print(PATH)
    ori_data = pd.read_excel(PATH, sheet_name='Sheet1')
    #ori_data = pd.read_table(db)
    print(ori_data)
    ori_data['years'] = ori_data['years'].astype(str)
    ori_data['date'] = ori_data['years'].str[0:4] + "-" + ori_data['years'].str[5:7] + "-" + ori_data['years'].str[8:10]
    ori_data['date'] = pd.to_datetime(ori_data['date'])
    temp_data = ori_data[['date', 'title', 'contents']]
    temp_data = temp_data.drop_duplicates(subset=['title', 'contents'], keep='last')
    titles_dict = temp_data.groupby('date')['title'].apply(lambda grp : list(grp.value_counts().index)).to_dict()
    contents_dict = temp_data.groupby('date')['contents'].apply(lambda grp: list(grp.value_counts().index)).to_dict()
    #contents_dict = temp_data.groupby('years')["contents"].apply(lambda x: x.tolist())

    twitter = Twitter()
    for date in titles_dict.keys():
        titles_dict[date] = twitter.nouns(str(titles_dict[date]))
        print(titles_dict[date])
        sentiment_val = get_sentimentWeight(titles_dict[date])
        dict = {'date' : date, 'keyword' : titles_dict[date], 'pos' : sentiment_val[0], 'neut' : sentiment_val[1], 'neg' : sentiment_val[2]}
        data.append(dict)
    sentiment_result = pd.DataFrame(data)
    return sentiment_result

    # for date in contents_dict.keys():
    #     contents_dict[date] = twitter.nouns(str(contents_dict[date]))
    #     sentiment_val = get_sentimentWeight(contents_dict[date])
    #     dict = {'date': date, 'keyword': titles_dict[date], 'pos': sentiment_val[0], 'neut': sentiment_val[1],
    #             'neg': sentiment_val[2]}
    #     data.append(dict)
    # sentiment_result = pd.DataFrame(data)
    # return sentiment_result

def pretreatment_df(sentiment_df, stock_df):
    mapping_df = pd.DataFrame()
    # 겹치지 않는 날짜 제거용
    print(sentiment_df['date'])
    print(stock_df['date'])
    s = set(sentiment_df['date'])
    temp = [x for x in stock_df['date'] if x not in s]
    for date in temp:
        date = date.strftime('%Y-%m-%d')
        stock_df = stock_df[stock_df['date'] != date]

    s = set(stock_df['date'])
    temp = [x for x in sentiment_df['date'] if x not in s]
    for date in temp:
        print(date)
        date = date.strftime('%Y-%m-%d')
        sentiment_df = sentiment_df[sentiment_df['date'] != date]

    # 감성 분석 결과 및 주가 데이터 바인딩하여, 새로운 DataFrame 생성
    mapping_df = pd.merge(sentiment_df, stock_df, on='date', how="right")
    return mapping_df

def linear_regression(mapping_df):
    X = mapping_df[['pos', 'neg']]
    Y = mapping_df['close']

    regr = linear_model.LinearRegression()
    regr.fit(X, Y)

    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)

    # with statsmodels
    X = sm.add_constant(X)  # adding a constant

    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X)

    # tkinter GUI
    root = tk.Tk()
    root.title("뉴스 감성분석을 통한 주가예측 시스템")
    canvas1 = tk.Canvas(root, width=1200, height=450)
    canvas1.pack()

    # with sklearn
    Intercept_result = ('Intercept: ', regr.intercept_)
    label_Intercept = tk.Label(root, text=Intercept_result, justify='center')
    canvas1.create_window(260, 220, window=label_Intercept)

    # with sklearn
    Coefficients_result = ('Coefficients: ', regr.coef_)
    label_Coefficients = tk.Label(root, text=Coefficients_result, justify='center')
    canvas1.create_window(260, 240, window=label_Coefficients)

    # with statsmodels
    print_model = model.summary()
    label_model = tk.Label(root, text=print_model, justify='center', relief='solid', bg='LightSkyBlue1')
    canvas1.create_window(800, 220, window=label_model)

    # New_Interest_Rate label and input box
    label1 = tk.Label(root, text='긍정 점수를 입력해주세요: ')
    canvas1.create_window(120, 100, window=label1)

    entry1 = tk.Entry(root)  # create 1st entry box
    canvas1.create_window(270, 100, window=entry1)

    # New_Unemployment_Rate label and input box
    label2 = tk.Label(root, text='부정 점수를 입력해주세요: ')
    canvas1.create_window(120, 120, window=label2)

    entry2 = tk.Entry(root)  # create 2nd entry box
    canvas1.create_window(270, 120, window=entry2)

    label2 = tk.Label(root, text='주식 종목명을 입력해주세요: ')
    canvas1.create_window(120, 140, window=label2)

    entry3 = tk.Entry(root)  # create 2nd entry box
    canvas1.create_window(270, 140, window=entry3)

    def values():
        global New_Positive_Rate  # our 1st input variable
        New_Positive_Rate = float(entry1.get())

        global New_Negative_Rate  # our 2nd input variable
        New_Negative_Rate = float(entry2.get())

        global New_Stock_name
        New_Stock_name = str(entry3.get())

        Prediction_result = (
        '예상되는 주가 가격 : ', regr.predict([[New_Positive_Rate, New_Negative_Rate]]))
        label_Prediction = tk.Label(root, text=Prediction_result, bg='orange')
        canvas1.create_window(260, 280, window=label_Prediction)

    button1 = tk.Button(root, text='예상 주가 확인하기', command=values,
                        bg='orange')  # button to call the 'values' command above
    canvas1.create_window(270, 180, window=button1)
    # plot 1st scatter
    figure3 = plt.Figure(figsize=(5, 4), dpi=100)
    ax3 = figure3.add_subplot(111)
    ax3.scatter(mapping_df['pos'].astype(float), mapping_df['close'].astype(float), color='r')
    scatter3 = FigureCanvasTkAgg(figure3, root)
    scatter3.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH)
    ax3.legend()
    ax3.set_xlabel('Positive Nouns')
    ax3.set_title('Positive Nonus Vs. Stock Index Price')

    # plot 2nd scatter
    figure4 = plt.Figure(figsize=(5, 4), dpi=100)
    ax4 = figure4.add_subplot(111)
    ax4.scatter(mapping_df['neg'].astype(float), mapping_df['close'].astype(float), color='g')
    scatter4 = FigureCanvasTkAgg(figure4, root)
    scatter4.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH)
    ax4.legend()
    ax4.set_xlabel('Negative Nouns')
    ax4.set_title('Negative Nouns Vs. Stock Index Price')
    root.mainloop()

if __name__ == '__main__':
    excel = read_newfile(DATADIR)
    article_df = sentiment_analysis(excel)
    print(excel)

    stock_df   = pd.DataFrame()
    excel = DATADIR2 + read_newfile(DATADIR2)
    stock_df = pd.read_excel(excel, sheet_name='Sheet1')

    mapping_df = pretreatment_df(article_df, stock_df)

    print(mapping_df['diff'])
    # 상관분석 결과
    #corr = mapping_df.corr(method='pearson')
    cols = ['pos', 'neut', 'neg', 'diff', 'close']
    cm = np.corrcoef(mapping_df[cols].values.T)
    sns.set(font_scale=1.5)
    gm = sns.heatmap(cm, cbar=True, square=True, fmt='.2f', annot_kws={'size':15}, yticklabels=cols, xticklabels=cols)
    plt.show()

    linear_regression(mapping_df)
