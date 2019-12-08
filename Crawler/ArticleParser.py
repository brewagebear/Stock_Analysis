from bs4 import BeautifulSoup
from sklearn.preprocessing import RobustScaler
import os.path
import requests
import re
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

class ArticleParser(object):
    special_symbol = re.compile('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$&▲▶◆◀■【】\\\=\(\'\"]')
    content_pattern = re.compile('본문 내용|TV플레이어| 동영상 뉴스|flash 오류를 우회하기 위한 함수 추가function  flash removeCallback|tt|앵커 멘트|xa0')

    @classmethod
    def clear_content(cls, text):
        # 기사 본문에서 필요없는 특수문자 및 본문 양식 등을 다 지움
        newline_symbol_removed_text = text.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        special_symbol_removed_content = re.sub(cls.special_symbol, ' ', newline_symbol_removed_text)
        end_phrase_removed_content = re.sub(cls.content_pattern, '', special_symbol_removed_content)
        blank_removed_content = re.sub(' +', ' ', end_phrase_removed_content).lstrip()  # 공백 에러 삭제
        reversed_content = ''.join(reversed(blank_removed_content))  # 기사 내용을 reverse 한다.
        content = ''
        for i in range(0, len(blank_removed_content)):
            # reverse 된 기사 내용중, ".다"로 끝나는 경우 기사 내용이 끝난 것이기 때문에 기사 내용이 끝난 후의 광고, 기자 등의 정보는 다 지움
            if reversed_content[i:i + 2] == '.다':
                content = ''.join(reversed(reversed_content[i:]))
                break
        return content

    @classmethod
    def clear_headline(cls, text):
        # 기사 제목에서 필요없는 특수문자들을 지움
        newline_symbol_removed_text = text.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        special_symbol_removed_headline = re.sub(cls.special_symbol, '', newline_symbol_removed_text)
        return special_symbol_removed_headline

    @classmethod
    def find_news_totalpage(cls, url):
        # 당일 기사 목록 전체를 알아냄
        try:
            totlapage_url = url
            request_content = requests.get(totlapage_url)
            document_content = BeautifulSoup(request_content.content, 'html.parser')
            headline_tag = document_content.find('div', {'class': 'paging'}).find('strong')
            regex = re.compile(r'<strong>(?P<num>\d+)')
            match = regex.findall(str(headline_tag))
            return int(match[0])
        except Exception:
            return 0

    @classmethod
    def clear_like_count(cls, g):
        g = g.replace(',', '')
        return g

    @classmethod
    def get_latest_file(cls, path):
        files_Path = path
        file_name_and_time_lst = []
        # 해당 경로에 있는 파일들의 생성시간을 함께 리스트로 넣어줌.
        for f_name in os.listdir(f"{files_Path}"):
            written_time = os.path.getctime(f"{files_Path}{f_name}")
            file_name_and_time_lst.append((f_name, written_time))
        # 생성시간 역순으로 정렬하고,
        sorted_file_lst = sorted(file_name_and_time_lst, key=lambda x: x[1], reverse=True)
        # 가장 앞에 있는 놈을 넣어준다.
        recent_file = sorted_file_lst[0]
        recent_file_name = recent_file[0]
        return recent_file_name

    @classmethod
    def create_corpus_latest_file_by_sympathic(cls, path):
        df = pd.read_excel(path, sheet_name='Sheet1')
        df.drop_duplicates(['title'], keep='first', inplace=True)
        df.drop_duplicates(['desc'], keep='first', inplace=True)
        robustScaler = RobustScaler()

        df['datetime'] = df['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y.%m.%d.'))

        df.set_index(df['datetime'], inplace=True)
        df[['good']] = robustScaler.fit_transform(df[['good']])
        df[['bad']] = robustScaler.fit_transform(df[['bad']])
        df[['neutral']] = robustScaler.fit_transform(df[['neutral']])
        df.drop('datetime', 1)
        print(df)

        weekly_df = df.resample('D', how={'good':np.sum,
                                              'bad':np.sum,
                                              'neutral':np.sum}).fillna(0)

        weekly_df.to_csv('/Users/dailyworker/workspace/python/Stock_Analysis/corpus/공감순_말뭉치(북한).csv',
                  sep=',',
                  na_rep='NaN',
                  float_format='%.2f',
                  columns=['good', 'bad', 'neutral'],
                  index = True,
                  encoding='utf-8')