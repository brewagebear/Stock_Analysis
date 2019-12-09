# -*- coding: utf-8 -*-
import os
import datetime
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.preprocessing import RobustScaler
from konlpy.tag import Twitter


DATADIR  = '/Users/dailyworker/workspace/python/Stock_Analysis/newscrawling_result/'
DATADIR2 = '/Users/dailyworker/workspace/python/Stock_Analysis/sympathic_data/KOSPI200.csv'
DATADIR3 = '/Users/dailyworker/workspace/python/Stock_Analysis/compare_result/morphology_analysis/형태소분석_뉴스제목(일본) 일자별 점수.csv'
OUTDIR = '/Users/dailyworker/workspace/python/Stock_Analysis/compare_result/morphology_analysis/'
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

def sentiment_analysis_title(db):
    filename = '2019-12-09 01:44:31 - compare_result(일본).xlsx'
    PATH = os.path.join(DATADIR , filename)
    data = []
    ori_data = pd.read_excel(PATH, sheet_name='Sheet1')
    ori_data['datetime'] = ori_data['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y.%m.%d.'))
    temp_data = ori_data[['datetime', 'title', 'desc']]
    temp_data = temp_data.drop_duplicates(subset=['title', 'desc'], keep='last')
    titles_dict = temp_data.groupby('datetime')['title'].apply(lambda grp: list(grp.value_counts().index)).to_dict()
    contents_dict = temp_data.groupby('datetime')['desc'].apply(lambda grp: list(grp.value_counts().index)).to_dict()
    # contents_dict = temp_data.groupby('years')["contents"].apply(lambda x: x.tolist())

    twitter = Twitter()
    for date in titles_dict.keys():
        titles_dict[date] = twitter.nouns(str(titles_dict[date]))
        print(titles_dict[date])
        sentiment_val = get_sentimentWeight(titles_dict[date])
        dict = {'datetime' : date, 'keyword' : titles_dict[date], 'pos' : sentiment_val[0], 'neut' : sentiment_val[1], 'neg' : sentiment_val[2]}
        data.append(dict)
    sentiment_result = pd.DataFrame(data)

    sentiment_result.set_index(sentiment_result['datetime'], inplace=True)
    sentiment_result.drop('datetime', 1)
    robustScaler = RobustScaler()

    sentiment_result[['pos']] = robustScaler.fit_transform(sentiment_result[['pos']])
    sentiment_result[['neg']] = robustScaler.fit_transform(sentiment_result[['neg']])
    sentiment_result[['neut']] = robustScaler.fit_transform(sentiment_result[['neut']])

    day_df = sentiment_result.resample('D', how=
    {'pos': np.sum,
     'neg': np.sum,
     'neut': np.sum}).fillna(0)
    file_name = os.path.basename(filename)
    p = re.compile(r'[가-힣]+').findall(file_name)

    day_df.to_csv(os.path.join(OUTDIR, '형태소분석_뉴스제목(' + p[0] + ') 일자별 점수.csv'),
                  sep=',',
                  na_rep='NaN',
                  float_format='%.2f',
                  columns=['pos', 'neg', 'neut'],
                  index=True,
                  encoding='utf-8')

    return day_df

def sentiment_analysis_content(db):
    filename = '2019-12-09 02:11:21 - compare_result(중국).xlsx'
    PATH = os.path.join(DATADIR, filename)
    data = []
    ori_data = pd.read_excel(PATH, sheet_name='Sheet1')
    ori_data['datetime'] = ori_data['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y.%m.%d.'))
    temp_data = ori_data[['datetime', 'title', 'desc']]
    temp_data = temp_data.drop_duplicates(subset=['title', 'desc'], keep='last')
    titles_dict = temp_data.groupby('datetime')['title'].apply(lambda grp : list(grp.value_counts().index)).to_dict()
    contents_dict = temp_data.groupby('datetime')['desc'].apply(lambda grp: list(grp.value_counts().index)).to_dict()
    #contents_dict = temp_data.groupby('years')["contents"].apply(lambda x: x.tolist())

    twitter = Twitter()

    for date in contents_dict.keys():
        contents_dict[date] = twitter.nouns(str(contents_dict[date]))
        sentiment_val = get_sentimentWeight(contents_dict[date])
        dict = {'datetime': date, 'keyword': titles_dict[date], 'pos': sentiment_val[0], 'neut': sentiment_val[1],
                'neg': sentiment_val[2]}
        data.append(dict)
    sentiment_result = pd.DataFrame(data)

    print(sentiment_result)

    sentiment_result.set_index(sentiment_result['datetime'], inplace=True)
    sentiment_result.drop('datetime', 1)
    robustScaler = RobustScaler()

    sentiment_result[['pos']] = robustScaler.fit_transform(sentiment_result[['pos']])
    sentiment_result[['neg']] = robustScaler.fit_transform(sentiment_result[['neg']])
    sentiment_result[['neut']] = robustScaler.fit_transform(sentiment_result[['neut']])

    day_df = sentiment_result.resample('D', how=
                                       {'pos': np.sum,
                                        'neg': np.sum,
                                        'neut': np.sum}).fillna(0)

    file_name = os.path.basename(filename)
    p = re.compile(r'[가-힣]+').findall(file_name)

    day_df.to_csv(os.path.join(OUTDIR, '형태소분석_뉴스본문('+p[0]+') 일자별 점수.csv'),
                  sep=',',
                  na_rep='NaN',
                  float_format='%.2f',
                  columns=['pos', 'neg', 'neut'],
                  index=True,
                  encoding='utf-8')

    return day_df

def pretreatment_df(sentiment_df, stock_df):
    # 감성 분석 결과 및 주가 데이터 바인딩하여, 새로운 DataFrame 생성
    mapping_df = pd.merge(stock_df, sentiment_df)
    print(mapping_df)
    return mapping_df

if __name__ == '__main__':
    excel = read_newfile(DATADIR)
    article_df = sentiment_analysis_title(excel)

    morphology_df = pd.read_csv(DATADIR3)
    stock_df = pd.read_csv(DATADIR2)


    mapping_df = pretreatment_df(morphology_df, stock_df)
    # 상관분석 결과
    #corr = mapping_df.corr(method='pearson')
    cols = ['pos', 'neut', 'neg', 'tradePrice', 'changePrice']
    cm = np.corrcoef(mapping_df[cols].values.T)
    sns.set(font_scale=1.5)
    gm = sns.heatmap(cm, cbar=True, square=True, fmt='.2f', annot_kws={'size':15}, yticklabels=cols, xticklabels=cols)
    plt.show()
    #plt.savefig('뉴스본문형태소_상관분석결과(중국).png')
    plt.savefig('뉴스제목형태소_상관분석결과(일본).png')
