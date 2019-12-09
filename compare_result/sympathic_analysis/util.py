import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def stock_file_pretreatment():
  stock_df     = pd.read_excel('/Users/dailyworker/workspace/python/Stock_Analysis/stockcrawling_result/2019-12-9 2시 23분 36초 result(KOSPI).xlsx')
  stock_df['datetime'] = stock_df['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
  stock_df.set_index(stock_df['datetime'], inplace=True)

  stock_df.to_csv('/Users/dailyworker/workspace/python/Stock_Analysis/sympathic_data/KOSPI200.csv',
                   sep=',',
                   na_rep='NaN',
                   float_format='%.2f',
                   columns=['tradePrice','change', 'changePrice'],
                   index=True,
                   encoding='utf-8')

def merge_file():
    stock_df = pd.read_csv('/Users/dailyworker/workspace/python/Stock_Analysis/sympathic_data/KOSPI200.csv')
    sympathic_df = pd.read_csv('/Users/dailyworker/workspace/python/Stock_Analysis/sympathic_data/일본뉴스 말뭉치.csv')
    merge_df = pd.merge(stock_df, sympathic_df)
    print(merge_df)
    return merge_df

def show_line_graph_negative(df):

    df['datetime'] = pd.to_datetime(df['datetime'])
    df['day'] = df['datetime'].dt.day

    x = df['day']
    y = df['tradePrice']
    y2 = df['good']
    y3 = df['bad']

    plt.plot(x,y,'b', label='KOSPI200')
    plt.plot(x,y2, 'r', label='NEGATIVE GRADE')
    plt.xlabel('Day')
    plt.ylabel('Index')
    plt.legend(loc='center right')
    plt.savefig('KOSPI200과 부정점수 비교 라인그래프 (러시아뉴스).png')
    plt.show()

def show_line_graph_positive(df):

    df['datetime'] = pd.to_datetime(df['datetime'])
    df['day'] = df['datetime'].dt.day

    x = df['day']
    y = df['tradePrice']
    y2 = df['good']
    y3 = df['bad']

    plt.plot(x,y,'b', label='KOSPI200')
    plt.plot(x,y2, 'r', label='NEGATIVE GRADE')
    plt.xlabel('Day')
    plt.ylabel('Index')
    plt.legend(loc='center right')
    plt.savefig('KOSPI200과 긍정점수 비교 라인그래프 (러시아뉴스).png')
    plt.show()


def show_relpolt_graph(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['day'] = df['datetime'].dt.day

    sns.relplot(x='day', y='bad', hue=df['change'], data=df)
    plt.savefig('KOSPI200 등락과 부정점수 비교 산점도 그래프(일본뉴스).png')
    plt.show()


if __name__ == "__main__":
    stock_file_pretreatment()
    data = merge_file()
    #show_line_graph_positive(data)
    #show_line_graph_negative(data)
    show_relpolt_graph(data)