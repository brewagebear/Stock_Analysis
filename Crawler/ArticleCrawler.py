# -*- coding: utf-8 -*-
import time
import math
import pandas as pd
import os.path
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from Crawler.Exceptions import *
from Crawler.ArticleParser import ArticleParser

class ArticleCrawler(object):

    def __init__(self):
        self.sort_method = {"관련도순":0, "최신순":1, "오래된순":2}
        self.query = ''
        self.maxpage = 0
        self.selected_sort_method = 0
        self.date = {'s_date': '', 'e_date' : '', 's_from': '', 'e_to' : ''}
        self.result_path ='C:/Users/Seok/Desktop/개발/Stock_Analysis/newscrawling_result/'
        driver = webdriver.Chrome(executable_path='C:/Users/Seok/Desktop/개발/Stock_Analysis/chromedriver.exe')
        self.now = datetime.now()

    def set_sort_method(self, *args):
        for key in args:
            if self.categories.get(key) is None:
                raise InvalidCategory(key)
        self.selected_sort_method = args

    def set_date(self, s_date, e_date):
        args = [s_date, e_date, s_date.replace(".", ""), e_date.replace(".", "")]
        for key, date in zip(self.date, args):
            self.date[key] = date
        print(self.date)

    def set_query(self, query_string):
        if query_string and not query_string.isspace():
            self.query = query_string
        else:
            raise Exception('검색어를 제대로 입력해주세요.')

    def set_result_path(self, custom_path):
        if os.path.exists(custom_path):
            self.result_path = custom_path
        else:
            raise InvaildFilePath(custom_path)

    def set_maxpage(self, page_num):
        if page_num.isdecimal():
            self.maxpage = page_num
        else:
            raise Exception('숫자만 입력 가능합니다.')

    def get_news(self, n_url):
        news_detail = []

        dreq = self.driver.get(n_url)
        time.sleep(0.6)
        html = self.driver.execute_script('return document.body.innerHTML')
        bsoup = BeautifulSoup(html, 'html.parser')

        '''
         [0] => pdate
         [1] => title
         [2] => btext
         [3] => company
         [4] => url
         [5] => pgood
         [6] => pbad
         [7] => pneut
        '''

        pdate = bsoup.select('.t11')[0].get_text()[:11]
        news_detail.append(pdate)

        title = bsoup.select('h3#articleTitle')[0].text  # 대괄호는  h3#articleTitle 인 것중 첫번째 그룹만 가져오겠다.
        news_detail.append(ArticleParser.clear_headline(title))

        _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
        btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
        news_detail.append(ArticleParser.clear_content(btext).strip())

        pcompany = bsoup.select('#footer address')[0].a.get_text()
        news_detail.append(pcompany)
        news_detail.append(n_url)

        plike = ArticleParser.clear_like_count(bsoup.select('#spiLayer > div.u_likeit li.good span._count')[0].get_text())
        pwarm = ArticleParser.clear_like_count(bsoup.select('#spiLayer > div.u_likeit li.warm span._count')[0].get_text())
        psad = ArticleParser.clear_like_count(bsoup.select('#spiLayer > div.u_likeit li.sad span._count')[0].get_text())
        pangry = ArticleParser.clear_like_count(bsoup.select('#spiLayer > div.u_likeit li.angry span._count')[0].get_text())
        pneut = ArticleParser.clear_like_count(bsoup.select('#spiLayer > div.u_likeit li.want span._count')[0].get_text())

        # Log Scale 적용
        pgood =round(float(plike) + float(pwarm), 2)
        pbad  =round(float(psad) + float(pangry), 2)
        pneut =round(float(pneut), 2)

        news_detail.append(pgood)
        news_detail.append(pbad)
        news_detail.append(pneut)
        return news_detail

    def crawler(self):
        page = 1
        maxpage_t = (int(self.maxpage) - 1) * 10 + 1  # 11= 2페이지 21=3페이지 31=4페이지  ...81=9페이지 , 91=10페이지, 101=11페이지
        f = open(self.result_path + "contents_text(" + self.query + ").txt", 'w', encoding='utf-8')

        while page < maxpage_t:
            print(page)
            url = "https://search.naver.com/search.naver?where=news&query=" + self.query + "&sort=0&ds=" \
                                                                            + self.date['s_date'] + "&de=" \
                                                                            + self.date['e_date'] + "&nso=so%3Ar%2Cp%3Afrom" \
                                                                            + self.date['s_from'] + "to" \
                                                                            + self.date['e_to'] + "%2Ca%3A&start=" + str(page)
            req = requests.get(url)
            cont = req.content
            soup = BeautifulSoup(cont, 'html.parser')

            for urls in soup.select("._sp_each_url"):
                try:
                    if urls["href"].startswith("https://news.naver.com"):
                        news_detail = self.get_news(urls["href"])
                        f.write(
                            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(news_detail[0], news_detail[1], news_detail[2],
                                                                      news_detail[3],
                                                                      news_detail[4],
                                                                      news_detail[5],
                                                                      news_detail[6],
                                                                      news_detail[7]))  # new style
                except Exception as e:
                    print(e)
                    continue
            page += 10
        f.close()

    def excel_make(self):
        now = self.now
        s = now.strftime('%Y-%m-%d %H:%M:%S')
        data = pd.read_csv(self.result_path + 'contents_text(' + self.query + ').txt',
                           sep='\t',
                           header=None,
                           error_bad_lines=False,
                           lineterminator='\n')
        print(data)
        data.columns = ['date', 'title', 'desc', 'company', 'url', 'good', 'bad', 'neutral']
        xlsx_output = s + ' - result(' + self.query + ').xlsx'
        data.to_excel(self.result_path + xlsx_output, encoding='utf-8')

if __name__ == "__main__":
    Crawler = ArticleCrawler()
    maxpage = input("최대 출력할 페이지수 입력하시오: ")
    Crawler.set_maxpage(maxpage)
    query = input("검색어 입력: ")
    Crawler.set_query(query)
    s_date = input("시작날짜 입력(2019.01.01):")
    e_date = input("끝날짜 입력(2019.12.31):")
    Crawler.set_date(s_date, e_date)
    Crawler.crawler()
    Crawler.excel_make()
    path = Crawler.result_path
    lastfile = ArticleParser.get_latest_file(path)
    ArticleParser.create_corpus_latest_file_by_sympathic(path+lastfile)