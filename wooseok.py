import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def dataread(readdata): #데이터를 엑셀에서 가져오는 함수
    df_freom_excel = pd.read_excel(
        r'C:\Users\Seok\Desktop\개발\Stock_Analysis\data'+'\\'+readdata+'.xlsx', #엑셀 경로
    )
    return(df_freom_excel)

def dataRef(dataSet): #불러온 데이터중 필요한 데이터만 추출하는 정제과정함수
    totalData = pd.DataFrame()
    k = 0;
    for i in dataSet:
        totalData["data:"+str(k)] = i["tradePrice"] #앞""안에 들어가는 값은 우리가 지정할 컬럼명 뒤""안에 들어가는 값은 엑셀에서의 컬럼값
        k = k+1
    return(totalData)

def correlationFunc(totalData): #피어슨 상관계수를 구하는 함수
    result = totalData.corr()
    return(result)

def visualizationResult(result):
    plt.figure(figsize=(10, 8))
    sns.heatmap(data = result, annot=True, fmt = '0.2f', linewidths=1, cmap='Blues')
    plt.show()


def main():
    # 엑셀에서 데이터 추출
    dataSet = []
    KOSPI200data = dataread('코스피200')
    DJIdata = dataread('다우지수')
    dataSet.append(KOSPI200data)
    dataSet.append(DJIdata)


    # 필요데이터 정제
    totalData = dataRef(dataSet)

    # 상관계수 구하기
    result = correlationFunc(totalData)

    # 시각화
    visualizationResult(result)






main()



