# -*- coding: utf-8 -*-
import requests
import time
import re
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime


#RESULT_PATH = os.path.abspath("./newscrawling_result/")
RESULT_PATH = 'C:/Users/Seok/Desktop/개발/Stock_Analysis/newscrawling_result/'
print(r'C:/Users/Seok/Desktop/개발/Stock_Analysis/newscrawling_result/')
now = datetime.now()  # 파일이름 현 시간으로 저장하기

driver = webdriver.Chrome(executable_path='C:/Users/Seok/Desktop/개발/Stock_Analysis/chromedriver.exe')

class Stack(list):
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        if self.is_empty():
            return -1
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def is_empty(self):
        if len(self.stack) == 0:
            return True
        return False


def get_news(n_url):
    news_detail = []
    stack = Stack()

    dreq = driver.get(n_url)
    time.sleep(0.6)
    html = driver.execute_script('return document.body.innerHTML')
    bsoup = BeautifulSoup(html, 'html.parser')

    '''
     [0] => pdate
     [1] => title
     [2] => btext
     [3] => company
     [4] => url
     [5] => good
     [6] => bad
     [7] => neut
    '''

    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
    btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
    news_detail.append(btext.strip())

    if stack.is_empty():
        stack.append(btext)
        news_detail = news_regularization(bsoup, btext, n_url)
    else:
        if stack[0] == btext:
            stack.pop()
            return
        else:
            stack.append(btext)
            news_detail = news_regularization(bsoup, btext, n_url)
    return news_detail

def clean_text(dirty_str_list):
    for idx, value in enumerate(dirty_str_list):
        text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', dirty_str_list[idx])
        dirty_str_list[idx] = text
    return dirty_str_list

def news_regularization(bsoup, btext, n_url):
    news_detail = []
    dirty_text  = []

    pdate = bsoup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    title = bsoup.select('h3#articleTitle')[0].text  # 대괄호는  h3#articleTitle 인 것중 첫번째 그룹만 가져오겠다.
    pcompany = bsoup.select('#footer address')[0].a.get_text()
    plike = bsoup.select('#spiLayer > div.u_likeit li.good span._count')[0].get_text()
    pwarm = bsoup.select('#spiLayer > div.u_likeit li.warm span._count')[0].get_text()

    psad = bsoup.select('#spiLayer > div.u_likeit li.sad span._count')[0].get_text()
    pangry = bsoup.select('#spiLayer > div.u_likeit li.angry span._count')[0].get_text()
    pneut = bsoup.select('#spiLayer > div.u_likeit li.want span._count')[0].get_text()

    dirty_text.append(title)
    dirty_text.append(btext.strip())
    dirty_text.append(pcompany)
    dirty_text.append(plike)
    dirty_text.append(pwarm)
    dirty_text.append(psad)
    dirty_text.append(pangry)
    dirty_text.append(pneut)

    clean_text_list = clean_text(dirty_text)
    pgood = int(clean_text_list[3]) + int(clean_text_list[4])
    pbad = int(clean_text_list[5]) + int(clean_text_list[6])
    pneut = int(clean_text_list[7])

    news_detail.append(clean_text_list[0])
    news_detail.append(clean_text_list[1])
    news_detail.append(clean_text_list[2])
    news_detail.append(n_url)
    news_detail.append(pgood)
    news_detail.append(pbad)
    news_detail.append(pneut)
    print(news_detail)
    return news_detail

def crawler(maxpage, query, s_date, e_date):
    s_from = s_date.replace(".", "")
    e_to = e_date.replace(".", "")
    page = 1
    maxpage_t = (int(maxpage) - 1) * 10 + 1  # 11= 2페이지 21=3페이지 31=4페이지  ...81=9페이지 , 91=10페이지, 101=11페이지
    f = open(RESULT_PATH + "contents_text(중국).txt", 'w', encoding='utf-8')

    while page < maxpage_t:

        print(page)

        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort=0&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
            page)

        req = requests.get(url)
        print(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        # print(soup)

        for urls in soup.select("._sp_each_url"):
            try:
                # print(urls["href"])
                if urls["href"].startswith("https://news.naver.com"):
                    # print(urls["href"])
                    news_detail = get_news(urls["href"])
                    # pdate, pcompany, title, btext
                    f.write(
                        "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(news_detail[0], news_detail[1], news_detail[2], news_detail[3],
                                                      news_detail[4], news_detail[5], news_detail[6], news_detail[7]))  # new style
            except Exception as e:
                print(e)
                continue
        page += 10

    f.close()


def excel_make():
    data = pd.read_csv(RESULT_PATH + 'contents_text(러시아).txt', sep='\t', header=None, error_bad_lines=False, lineterminator='\n')
    data.columns = ['date', 'title', 'desc', 'company', 'url', 'good', 'bad', 'neut']

    xlsx_outputFileName = '%s-%s-%s  %s시 %s분 %s초 result.xlsx' % (
    now.year, now.month, now.day, now.hour, now.minute, now.second)
    # xlsx_name = 'result' + '.xlsx'


    data.to_excel(RESULT_PATH + xlsx_outputFileName, encoding='utf-8')


def main():
    maxpage = input("최대 출력할 페이지수 입력하시오: ")
    query = input("검색어 입력: ")
    s_date = input("시작날짜 입력(2019.01.01):")  # 2019.01.01
    e_date = input("끝날짜 입력(2019.04.28):")  # 2019.04.28
    crawler(maxpage, query, s_date, e_date)  # 검색된 네이버뉴스의 기사내용을 크롤링합니다.
    excel_make()

main()