# -*- coding: utf-8 -*-
import os
import datetime
import sys
import pandas as pd
import operator
from time import localtime, strftime
from collections import OrderedDict
from konlpy.tag import Twitter
from apyori import apriori
from sklearn.preprocessing import scale, robust_scale, minmax_scale, maxabs_scale
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt


DATADIR = 'C:/Users/planit/Desktop/bigdata/'
NEWFILE = ''


def read_newfile():
    dir = DATADIR
    files = os.listdir(dir)
    # listdir() 해당 경로의 파일을 리스트로 반환

    # 파일의 수정시간을 타임스탬프로 출력한 후 내림차순으로 정렬하였다.
    for i in range(0, len(files)):
        for j in range(0, len(files)):
            if datetime.datetime.fromtimestamp(os.path.getmtime(dir + files[i])) > \
                    datetime.datetime.fromtimestamp(os.path.getmtime(dir + files[j])):
                (files[i], files[j]) = (files[j], files[i])

    print(files[0])
    NEWFILE = 'article.xlsx'
    return NEWFILE


def pretreatment_content(filname):
    PATH = DATADIR + filname
    result = {}
    ori_data = pd.read_excel(PATH, sheet_name='Sheet1')
    temp_data = ori_data[['years', 'title', 'contents']]
    temp_data = temp_data.drop_duplicates(subset=['title', 'contents'], keep='last')
    titles_dict = temp_data.groupby('years')['title'].apply(lambda grp : list(grp.value_counts().index)).to_dict()
    contents_dict = temp_data.groupby('years')['contents'].apply(lambda grp: list(grp.value_counts().index)).to_dict()
    #contents_dict = temp_data.groupby('years')["contents"].apply(lambda x: x.tolist())
    twitter = Twitter()
    for date in titles_dict.keys():
        titles_dict[date] = twitter.nouns(str(titles_dict[date]))


    return titles_dict
    #print(titles_dict.values())

    # for date in contents_dict.keys():
    #     contents_dict[date] = twitter.nouns(str(contents_dict[date]))
    # return contents_dict
    # print(contents_dict.values())
    # for name_of_the_group, group in titles:
    #     print(name_of_the_group)
    #     print(group)



    # for index, row in temp_data.iterrows():
    #      result[ori_data['years'][index]] = twitter.nouns(ori_data['title'][index])
    #      result[ori_data['years'][index]] = twitter.nouns(ori_data['contents'][index])
    #      print(result)

def main():
    excel = read_newfile()
    stdata = pretreatment_content(excel) #단어 분석 데이터

    store_data = pd.read_csv('C:\\Users\\planit\\Desktop\\bigdata\\stock2.csv')  # 주식데이터

    stdatakey = list(stdata.keys())
    stdval = stdata.values()

    words = []
    for s in stdval: #추출된 단어의 값들
        words.extend(s)

    words = list(set(words)) #중복제거된 단어 모음

    # 단어사전 만들기
    dicword = {}
    for i in range(len(words)):  #['wordn' = 'weight']
        dicword[words[i]] = 0

    # 전처리 과정----
    temp = [] #겹치는 날짜, 가중치만 가지고 있음
    temp2 = {} #겹치는 날짜, 단어를 가지고 있음

    dicwordkey = list(dicword.keys()) #단어 키값만 가지고 있는 데이터

    for i in range(len(store_data)):  # 둘이 겹치는 데이터만 가져오기 # 주식 76
        if store_data.values[i][1] in stdata:  # 단어
            #for j in range(len(store_data.values[i])):
            temp.append([store_data.values[i][1],store_data.values[i][3]])

    for i in range(len(store_data)):  # 둘이 겹치는 데이터만 가져오기 # 주식 76
        if store_data.values[i][1] in stdata:  # 단어
            #for j in range(len(store_data.values[i])):
            temp2[store_data.values[i][1]] = stdata[store_data.values[i][1]]

    #temp: [['2019-02-12-', 300], ['2019-02-21-', 550], ['2019-02-22-', 400], ['2019-02-25-', 500], ['2019-02-26-', 1250], ['2019-03-04-', 1850], ['2019-03-05-', 100], ['2019-03-06-', 1000],
    #temp2: {'2019-02-12-': ['절반', '이상', '북한', '협력', '대상', '명', '비교'], '2019-02-21-': ['트럼프', '대북', '제재', '풀', '북한', '뭔가'], '2019-02-22-': ['폼페이', '오', '북한', '개방', '베를린', '장벽', '붕괴'],
    temp2val = list(temp2.values())
    #---

    for i in range(len(temp2)):  #등장하는 단어 가중치(주식의 가격) 더해주기
        for j in range(len(temp2val[i])):
            dicword[temp2val[i][j]] =  dicword[temp2val[i][j]] + temp[i][1]

    sortedDicword = sorted(dicword.items(), key = operator.itemgetter(1), reverse=True) #정렬 [밸류값별 오름차순]
    print(sortedDicword)

    temp3 = {} #각 날짜별 주식 가중치 총합
    for i in range(len(temp)):
        temp3[temp[i][0]] = 0

    for i in range(len(temp2)):
        for j in range(len(temp2val[i])):
           temp3[temp[i][0]] =  temp3[temp[i][0]] + dicword[temp2val[i][j]]

    print(temp3)

    #regression을 위한 전처리
    temp3val = list(temp3.values())
    temp3key = list(temp3.keys())
    scaletemp3 = scale(temp3val)

    temp4 = {} #날짜별 주가 종가를 가지고 있음

    for i in range(len(temp)): #76번 반복 원소개수(날짜수)
        if temp[i][0] in stdata: #97개 데이터 중에 날짜가 존재하면
            temp4[temp[i][0]] = store_data.values[i][2]

    temp4val = list(temp4.values())
    temp4key = list(temp4.keys())
    scaletemp4 = scale(temp4val)

    x = np.array(temp3val).reshape((-1,1))   #temp3 : {'2019-02-12-': -129150, '2019-02-21-': -134250, '2019-02-22-': -124900, '2019-02-25-': -281050, '2019-02-26-': -138950, '2019-03-04-': -274100, '2019-03-05-': -270900, '2019-03-06-': -651350, '2019-03-07-': -862050, '2019-03-08-': -848450, '2019-03-11-': -401350, '2019-03-12-': -693600,
    y = np.array(temp4val).reshape((-1,1))   #temp4 :{'2019-02-12-': 28500, '2019-02-21-': 28200, '2019-02-22-': 27850, '2019-02-25-': 28100, '2019-02-26-': 28300, '2019-03-04-': 28850, '2019-03-05-': 28600, '2019-03-06-': 28050, '2019-03-07-': 28450, '2019-03-08-': 27950, '2019-03-11-': 29200, '2019-03-12-': 29500, '2019-03-13-': 25900, '2019-03-14-'

    model = LinearRegression()
    model.fit(x,y)
    r_sq = model.score(x, y)
    print('coefficient of determination:', r_sq)

    print('intercept:', model.intercept_)
    print('slope:', model.coef_)
    y_pred = model.predict(x)
    print('predicted response:', y_pred, sep='\n')

    #그레프 표현
    title = "stock price"
    xlab = "x axis"
    ylab = "y axis"

    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)

    plt.plot(temp4key,y_pred)
    plt.show()

    print(y)





main()