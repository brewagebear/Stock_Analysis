import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib

def dataread(readdata): #데이터를 엑셀에서 가져오는 함수
    df_freom_excel = pd.read_excel(
        'C:/Users/Seok/Desktop/개발/Stock_Analysis/stockcrawling_result/new' + '/' + readdata  + '.xlsx', #엑셀 경로
    )
    return(df_freom_excel)

def dataRef(dataSet): #불러온 데이터중 필요한 데이터만 추출하는 정제과정함수
    totalData = pd.DataFrame()
    k = 0;
    for i in dataSet:
        if(k==0): #첫데이터 추가(무조건 코스피200)
            # totalData["KOSPI200_tradePrice"] = i["tradePrice"][7:30] #앞""안에 들어가는 값은 우리가 지정할 컬럼명 뒤""안에 들어가는 값은 엑셀에서의 컬럼값 (엑셀 9행부터 32행까지 추출)
            totalData["KOSPI200_tradePrice"] = i["tradePrice"]
            k = k+1
            print(totalData)
        elif (i.shape[1]==10): #국내 지수(컬럼수가 10개)
            totalData["tradePrice"] = i["tradePrice"]
            totalData["changePrice"] = i["changePrice"]
            totalData["accTradeVolume"] = i["accTradeVolume"]
            totalData["accTradePrice"] = i["accTradePrice"]
            totalData["individualStraightPurchasePrice"] = i["individualStraightPurchasePrice"]
            totalData["foreignStraightPurchasePrice"] = i["foreignStraightPurchasePrice"]
            totalData["institutionStraightPurchasePrice"] = i["institutionStraightPurchasePrice"]
        else: #해외시장지수
            totalData["tradePrice"] = i["tradePrice"]
            totalData["changePrice"] = i["changePrice"]
            totalData["changeRate"] = i["changeRate"]
            totalData["prevClosingPrice"] = i["prevClosingPrice"]
            totalData["openingPrice"] = i["openingPrice"]
            totalData["highPrice"] = i["highPrice"]
            totalData["lowPrice"] = i["lowPrice"]
            # totalData["accTradeVolume"] = i["accTradeVolume"]
            # totalData["periodTradeVolume"] = i["periodTradeVolume"]
            k = k+1
    return(totalData)

def correlationFunc(totalData): #피어슨 상관계수를 구하는 함수
    result = totalData.corr()
    return(result)

def visualizationResult(result,a):

    plt.figure(figsize=(12, 15))
    sns.heatmap(data = result, annot=True, fmt = '0.2f', linewidths=1, cmap='Blues')
    plt.title('KOSPI200 & ' + a , fontsize=20)
    plt.show()
    plt.figure(figsize=(12, 15))
    sns.heatmap(data=result, annot=True, fmt='0.2f', linewidths=1, cmap='Blues')
    plt.title('KOSPI200 & ' + a, fontsize=20)
    plt.savefig('C:/Users/Seok/Desktop/개발/Stock_Analysis/stockcrawling_result/new/분석이미지/'+ a + '.png')


def main():

    print("비교할 데이터 입력 : ")
    a = input()
    # 엑셀에서 데이터 추출 [코스피200과 원하는 데이터 하나빼고 모두 주석처리]
    dataSet = []
    dataSet.append(dataread('한국-KOSPI200'))
    dataSet.append(dataread(a))
    # dataSet.append(dataread('코스닥'))
    # dataSet.append(dataread('다우지수'))
    # dataSet.append(dataread('나스닥'))
    # dataSet.append(dataread('상해종합'))
    # dataSet.append(dataread('니케이225'))
    # dataSet.append(dataread('러시아RTS'))

    # 필요데이터 정제
    totalData = dataRef(dataSet)

    # 상관계수 구하기
    result = correlationFunc(totalData)

    # 시각화
    visualizationResult(result,a)




while(1):
    main()



