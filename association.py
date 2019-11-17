# -*- coding: utf-8 -*-
import os
import datetime
import sys
import pandas as pd
from time import localtime, strftime
from collections import OrderedDict
from konlpy.tag import Twitter
from apyori import apriori

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
    stdata = pretreatment_content(excel) #단어 분석 데이터 가져오기

    stdataval = list(stdata.values())
    store_data = pd.read_csv('C:\\Users\\planit\\Desktop\\bigdata\\stock2.csv') #주식데이터
    temp = [] #날짜, 가중치만 가지고 있음

    for i in range(76):
        if store_data.values[i][3] > 0 :
            temp.append([store_data.values[i][1],'1'])
        elif int(store_data.values[i][3]) == 0 :
            temp.append([store_data.values[i][1],'0'])
        elif int(store_data.values[i][3]) < 0 :
            temp.append([store_data.values[i][1],'-1'])  #[['2019-02-12-', '1'], ['2019-02-13-', '-1'], ['2019-02-14-', '-1'], ['2019-02-15-', '1'], ['2019-02-18-', '1'], ['2019-02-19-', '1'], ['2019-02-20-', '-1']

    temp2  = {} #날짜별 단어 가중치값 가지 데이터(차후 apriori 적용해볼 데이터 셋)

    for i in range(len(temp)): #전처리 과정 #둘이 겹치는 데이터만 가져오기 # 주식
        if temp[i][0] in stdata:  #단어
            stdataval[i].append(temp[i][1])
            temp2[temp[i][0]] = stdataval[i]  #{날짜 : 단어, 가중치}

    print(temp2) # {'2019-02-12-': ['절반', '이상', '북한', '협력', '대상', '명', '비교', '1'], '2019-02-21-': ['당국자', '북한', '주장', '말장난', '사흘', '장외', '공방전', '트럼프', '북한', '요구', '과장', '이번', '북한', '말', '-1'],
    apriorival = list(temp2.values())

    association_rules = apriori(apriorival, min_support=0.1, min_confidence=0.4) #10시 32분
    association_results = list(association_rules)

    print(len(association_results))
    for ar in association_results:
        print(ar)




main()