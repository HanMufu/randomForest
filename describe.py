import datetime
import time
import pandas as pd
from numpy import linalg as la
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
import numpy as np
import random
import matplotlib.pyplot as plt


def dealdata(data):
    '''
    :param data: 未经处理的初始数据集
    :return: 处理好的数据集
    '''
    global col
    #     data = data.drop(['capital_reserve_fund','operating_revenue','gross_profit_margin','inc_total_revenue_year_on_year'],axis=1)
    col = [c for c in data.columns if c not in ['total_assets', 'total_liability', 'Return', 'Unnamed: 0', 'Y_bin']]

    for i in col:
        data[i].fillna(data[i].mean(), inplace=True)
    data['Y_bin'].fillna(0, inplace=True)
    data['Return'].fillna(0, inplace=True)
    #     amin, amax = data.min(), data.max()  # 求最大最小值
    #     data = (data - amin) / (amax - amin)  # (矩阵元素-最小值)/(最大值-最小值)
    return data


def dataset(startdate, enddate, window, label_type, stockindex, stockpool_type):
    '''
    用来获取数据

    :param startdate:需要获取的数据开始日期
    :param enddate:需要获取的数据结束日期
    :param window:涨幅分类的阈值百分比，大于window的为正类，小于为负类
    :param label_type:使用哪种分类算法。1为按涨幅比例分，0为按涨跌与否分
    :param stockindex:哪个股票池的数据
    :param stockpool_type:使用哪种股票池。1为上证指数等大股票池，0为行业股票池
    :return: 列为各因子的值，行为startdate当天的所有股票代码
    '''
    fdate = startdate
    if stockpool_type == 1:
        stock_set = get_index_stocks(stockindex, fdate)  # 综合指数
    else:
        stock_set = get_industry_stocks(stockindex, fdate)  # 行业指数
    q = query(
        valuation.code,
        indicator.roa,
        valuation.ps_ratio,
        valuation.pcf_ratio,
        valuation.pe_ratio_lyr,
        balance.total_liability,
        balance.total_assets,
        indicator.roe,
        indicator.gross_profit_margin,

        valuation.circulating_market_cap,
        #         valuation.pb_ratio,
        valuation.pcf_ratio,
        balance.capital_reserve_fund,
        income.operating_revenue,
        indicator.inc_total_revenue_year_on_year,
        indicator.roe,
        indicator.gross_profit_margin,
        indicator.operation_profit_to_total_revenue,
        indicator.inc_revenue_year_on_year,
        indicator.inc_revenue_annual
    ).filter(
        valuation.code.in_(stock_set)
    )
    fdf = get_fundamentals(q, date=fdate)
    # 获取股票代码中的各个指标
    fdf.index = fdf['code']
    fdf.pop('code');

    current_date = startdate
    forcast_date = enddate

    current_close = get_price(stock_set, fields=['close'], end_date=current_date, count=1)[
        'close'].T  # 获取股票列表中的股票在所设置时间区间的收盘价
    forcast_close = get_price(stock_set, fields=['close'], end_date=forcast_date, count=1)['close'].T

    current_date_1 = datetime.datetime.strptime(current_date, "%Y-%m-%d")
    # 动量翻转因子：一个月
    last_month_close = \
    get_price(stock_set, fields=['close'], end_date=str(current_date_1 - datetime.timedelta(days=30)), count=1)[
        'close'].T
    last_month_close_2 = \
    get_price(stock_set, fields=['close'], end_date=str(current_date_1 - datetime.timedelta(days=60)), count=1)[
        'close'].T
    # DTA:资产负债率
    dta = fdf['total_assets'] / fdf['total_liability']
    fdf['DTA'] = dta

    grow = (forcast_close.iloc[:, 0] - current_close.iloc[:, 0]) / current_close.iloc[:, 0]  # 求涨幅
    grow1 = (current_close.iloc[:, 0] - last_month_close.iloc[:, 0]) / last_month_close.iloc[:, 0]  # 求涨幅
    grow2 = (current_close.iloc[:, 0] - last_month_close_2.iloc[:, 0]) / last_month_close_2.iloc[:, 0]  # 求涨幅
    grow = pd.DataFrame(grow, columns=['Return'])
    grow1 = pd.DataFrame(grow1, columns=['last_month'])
    grow2 = pd.DataFrame(grow2, columns=['two_last_month'])
    fdf = pd.merge(fdf, grow2, left_index=True, right_index=True)
    fdf = pd.merge(fdf, grow1, left_index=True, right_index=True)
    df = pd.merge(fdf, grow, left_index=True, right_index=True)  # 拼接
    if label_type == 1:  # 选择第一种阈值计算类型（前百分之window的涨幅为1类，之后的为0类）
        bound = np.nanpercentile(df['Return'], window)
        df.loc[(df['Return'] >= bound), 'Y_bin'] = 1
        df.loc[(df['Return'] < bound), 'Y_bin'] = 0
    else:  # 涨的为1类，跌的为0类（用于短期阈值比较好）
        bound = 0
        df.loc[(df['Return'] >= bound), 'Y_bin'] = 1
        df.loc[(df['Return'] < bound), 'Y_bin'] = 0
    return df


def print_(random_seed, s, train_data):
    '''

    :param random_seed: 最优的模型的随机种子编号
    :param s: 图的位置
    :param train_data: 训练数据集

    '''

    # 十颗树  太少
    rfc = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=random_seed)
    rfc.fit(train_data[col], train_data['Y_bin'])
    importances_result_dict = {}
    importance = rfc.feature_importances_
    for i in range(len(col)):
        importances_result_dict[col[i]] = importance[i]
    result = sorted(importances_result_dict.items(), key=lambda item: item[1], reverse=True)
    im = []
    score = []
    for i in range(len(col)):
        im.append(result[i][0])
        score.append(result[i][1])
    plt.subplot(s)
    plt.xticks(list(map(lambda x, y: x + y, list(range(len(col))), [0.5] * len(col))), im, rotation=90)
    plt.bar(range(len(col)), score)


def train_max_index(train_data, test_data):
    '''

    :param train_data: 训练数据集
    :param test_data: 测试数据集
    :return: 最优模型的随机种子编号
    '''
    x = []
    y = []

    max_index = 0  # 存储最大真阳率的random_state值
    max_zhenyang = 0
    for i in range(100):

        rfc = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=i)
        rfc.fit(train_data[col], train_data['Y_bin'])
        t1 = rfc.predict(test_data[col])

        zhenyang = ROC(t1, np.array(test_data['Y_bin']))
        if max_zhenyang < zhenyang:
            max_index = i
            max_zhenyang = zhenyang
    return max_index


def ROC(prediction, test, trueclass=1, flaseclass=0):
    '''
    :param prediction: 预测标志
    :param test: 真实标志
    :param trueclass: 视为真的类别值
    :param flaseclass: 视为假的类别值
    :return: 真阳率，假阳率
    '''
    # 这里写的字母表示意义与教材的不一致，因此后面计算真阳率时不能用书上的公式
    TP = 0  # 预测真为真
    FN = 0  # 预测真为假
    FP = 0  # 预测假为真
    TN = 0  # 预测假为假

    for i in range(np.shape(test)[0]):

        if prediction[i] == trueclass and test[i] == trueclass:
            TP = TP + 1
        elif prediction[i] == flaseclass and test[i] == flaseclass:
            TN = TN + 1
        elif prediction[i] == trueclass and test[i] == flaseclass:
            FP = FP + 1
        elif prediction[i] == flaseclass and test[i] == trueclass:
            FN = FN + 1
    #     print(TP,FN,FP,TN)
    #     if (FP + TN) == 0:  # 因为样本选取可能没有假例，此时预测假为假的TN值永远为零，当FP也为零时，分母为零，报错，这样做为了防止报错，因此最好不要用只有一类的样本集
    #         return TP / (TP + FN), 0
    #     return TP / (TP + FN), FP / (FP + TN)
    return TP / (TP + FN)


def main_(stockindex, train_startday, train_endday, test_endday, label_type, stockpool_type):
    test_startday = train_endday # 赋值测试开始时间为训练结束时间

    train_data = dealdata(dataset(train_startday, train_endday, 70, label_type, stockindex, stockpool_type))
    test_data = dealdata(dataset(test_startday, test_endday, 70, label_type, stockindex, stockpool_type))

    # 这里的col处理好之后没有用？
    col = [c for c in train_data.columns if c not in ['Return', 'Unnamed: 0', 'Y_bin']]
    max_index = train_max_index(train_data, test_data)

    plt.title(train_startday + ' ' + test_endday + ' ' + stockindex)
    print_(max_index, 111, train_data)
#     plt.show()


#时间不同
main_(stockindex='000001.XSHG',train_startday='2017-07-02',train_endday='2017-08-02',test_endday='2017-09-02',label_type=1,stockpool_type=1)
plt.show()
main_(stockindex='000001.XSHG',train_startday='2015-08-02',train_endday='2016-08-02',test_endday='2017-08-02',label_type=1,stockpool_type=1)
plt.show()
