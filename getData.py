# 导入函数库
import jqdata
import json
import pandas as pd
from six import StringIO
# import tushare as ts
from jqlib.technical_analysis import *
# import numpy as np

def initialize(context):
    tagIndustry()
    
    
    
# 按季度获取因子表数据
# 输入：无
# 输出：输出到文件，文件形如‘2015q1’，表示2015年第一季度沪深300股票因子表
# 注意：如果数据格式改了，则涉及到因子表的函数中使用iloc处都可能要更改
# 打标签函数中 gain_ratio和label的列数一定要更改
def getData():
    for year in range(2006, 2016):
        for quarter in range(1, 5):
            '''获取当季度的沪深300成份股'''
            month = quarter*3-2
            if month < 10:
                HS300 = get_index_stocks('000300.XSHG', '%d-%s-10' % (year, '0{}'.format(month)))
            else:
                HS300 = get_index_stocks('000300.XSHG', '%d-%d-10' % (year, month))
            '''获取财务数据'''
            df = get_fundamentals(query(
                valuation, income, indicator, cash_flow
            ).filter(
                # 这里不能使用 in 操作, 要使用in_()函数
                valuation.code.in_(HS300)
            ), statDate = '%dq%d' % (year, quarter))
            df = df.loc[:, ['code', 'statDate', 'pe_ratio', 'pb_ratio', 'ps_ratio', 'operating_profit', 'total_profit', \
            'roe', 'roa', 'gross_profit_margin', 'total_operating_revenue', 'operation_profit_to_total_revenue', 'administration_expense', \
            'inc_net_profit_year_on_year', 'turnover_ratio', 'net_profit', 'inc_net_profit_annual', 'total_operating_revenue']]
            '''获取MACD, dif, dea技术指标'''
            if month < 10:
                macd_dif, macd_dea, macd_macd = MACD(HS300,check_date='%d-%s-10' % (year, '0{}'.format(month)), SHORT = 10, LONG = 30, MID = 15)
            else:
                macd_dif, macd_dea, macd_macd = MACD(HS300,check_date='%d-%d-10' % (year, month), SHORT = 10, LONG = 30, MID = 15)
            df['macd_dif'] = 0.0
            df['macd_dea'] = 0.0
            df['macd_macd'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'macd_dif'] = macd_dif[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'macd_dea'] = macd_dea[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'macd_macd'] = macd_macd[(df.loc[i, ['code']]).iloc[0]]
            '''获取RSI技术指标，并加入df'''
            if month < 10:
                RSI1 = RSI(HS300, check_date='%d-%s-10' % (year, '0{}'.format(month)), N1=20)
            else:
                RSI1 = RSI(HS300, check_date='%d-%d-10' % (year, month), N1=20)
            df['RSI'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'RSI'] = RSI1[(df.loc[i, ['code']]).iloc[0]]
            '''获取PSY技术指标'''
            if month < 10:
                PSY1 = PSY(HS300,check_date='%d-%s-10' % (year, '0{}'.format(month)), timeperiod=20)
            else:
                PSY1 = PSY(HS300,check_date='%d-%d-10' % (year, month), timeperiod=20)
            df['PSY'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'PSY'] = PSY1[(df.loc[i, ['code']]).iloc[0]]
            '''获取扣除非经营性损益PE指标'''
            #获取参数1
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    indicator # 在这里改表名
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-10' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    indicator # 在这里改表名
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-10' % (year, month))
            adjusted_profit = fundamental1.loc[:, ['code', 'adjusted_profit']]
            #获取参数2
            if month < 10:
                fundamental2 = get_fundamentals(query(
                    valuation # 在这里改表名
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-10' % (year, '0{}'.format(month)))
            else:
                fundamental2 = get_fundamentals(query(
                    valuation # 在这里改表名
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-10' % (year, month))
            market_cap = fundamental2.loc[:, ['code', 'market_cap']]
            #计算扣除非经营性损益PE
            for i in range(0, len(adjusted_profit)):
                adjusted_profit.iloc[i, 1] = adjusted_profit.iloc[i, 1] / market_cap.iloc[i, 1]
            adjusted_profit.columns = ['code', 'PE1']
            # 和df合并
            df = pd.merge(df, adjusted_profit, how='left', on='code')
            '''获取 净利润增长率/PE'''
            #获取参数1
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    indicator
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    indicator
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            inc_net_profit_year_on_year = fundamental1.loc[:, ['code', 'inc_net_profit_year_on_year']]
            
            #获取参数2
            if month < 10:
                fundamental2 = get_fundamentals(query(
                    valuation
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental2 = get_fundamentals(query(
                    valuation
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            pe_ratio = fundamental2.loc[:, ['code', 'pe_ratio']]
            # 计算净利润增长率/pe
            for i in range(0, len(inc_net_profit_year_on_year)):
                inc_net_profit_year_on_year.iloc[i, 1] = inc_net_profit_year_on_year.iloc[i, 1] / pe_ratio.iloc[i, 1]
            inc_net_profit_year_on_year.columns = ['code', 'jinglirunzengzhanglv/PE']
            df = pd.merge(df, inc_net_profit_year_on_year, how='left', on='code')
            '''获取营业收入同比增长率'''
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    indicator
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    indicator
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            inc_revenue_year_on_year = fundamental1.loc[:, ['code', 'inc_revenue_year_on_year']]
            df = pd.merge(df, inc_revenue_year_on_year, how='left', on='code')
            '''获取净利润同比增长率'''
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    indicator
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    indicator
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            inc_net_profit_year_on_year = fundamental1.loc[:, ['code', 'inc_net_profit_year_on_year']]
            df = pd.merge(df, inc_net_profit_year_on_year, how='left', on='code')
            '''获取扣除非经常性损益后净利润率TTM'''
            # if month < 10:
            #     fundamental1 = get_fundamentals(query(
            #         indicator
            #     ).filter(
            #         valuation.code.in_(HS300)
            #     ), date='%d-%s-15' % (year, '0{}'.format(month)))
            # else:
            #     fundamental1 = get_fundamentals(query(
            #         indicator
            #     ).filter(
            #         valuation.code.in_(HS300)
            #     ), date='%d-%d-15' % (year, month))
            # adjusted_profit_to_profit = fundamental1.loc[:, ['code', 'adjusted_profit_to_profit']]
            # df = pd.merge(df, adjusted_profit_to_profit, how='left', on='code')
            '''获取总资产/净资产'''
            # #获取参数1
            # if month < 10:
            #     fundamental1 = get_fundamentals(query(
            #         balance
            #     ).filter(
            #         valuation.code.in_(HS300)
            #     ), date='%d-%s-15' % (year, '0{}'.format(month)))
            # else:
            #     fundamental1 = get_fundamentals(query(
            #         balance
            #     ).filter(
            #         valuation.code.in_(HS300)
            #     ), date='%d-%d-15' % (year, month))
            # total_assets = fundamental1.loc[:, ['code', 'total_assets']]
            # #获取参数2
            # fundamental2 = get_fundamentals(query(
            #     security_indicator
            # ).filter(
            #     valuation.code.in_(HS300)
            # ), statDate='%d' % (year))
            # net_assets = fundamental2.loc[:, ['code', 'net_assets']]
            # #计算所需参数
            # for i in range(0, 10):
            #     total_assets.iloc[i, 1] = total_assets.iloc[i, 1] / net_assets.iloc[i, 1]
            # total_assets.columns = ['code', 'zongzichan/jingzichan']
            # df = pd.merge(df, total_assets, how='left', on='code')
            '''获取现金比率'''
            #获取参数1
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            cash_equivalents = fundamental1.loc[:, ['code', 'cash_equivalents']]
            #获取参数2
            if month < 10:
                fundamental2 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental2 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            total_current_liability = fundamental2.loc[:, ['code', 'total_current_liability']]
            #计算所需参数
            for i in range(0, len(cash_equivalents)):
                cash_equivalents.iloc[i, 1] = cash_equivalents.iloc[i, 1] + total_current_liability.iloc[i, 1]
            cash_equivalents.columns = ['code', 'xianjinbilv']
            df = pd.merge(df, cash_equivalents, how='left', on='code')
            '''获取流动比率'''
            #获取参数1
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            total_current_assets = fundamental1.loc[:, ['code', 'total_current_assets']]
            
            #获取参数2
            if month < 10:
                fundamental2 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental2 = get_fundamentals(query(
                    balance
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            total_current_liability = fundamental2.loc[:, ['code', 'total_current_liability']]
            # #计算所需参数
            for i in range(0, len(total_current_assets)):
                total_current_assets.iloc[i, 1] = total_current_assets.iloc[i, 1] / total_current_liability.iloc[i, 1]
            total_current_assets.columns = ['code', 'liudongbilv']
            df = pd.merge(df, total_current_assets, how='left', on='code')
            '''获取总市值取对数'''
            if month < 10:
                fundamental1 = get_fundamentals(query(
                    valuation
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                fundamental1 = get_fundamentals(query(
                    valuation
                ).filter(
                    valuation.code.in_(HS300)
                ), date='%d-%d-15' % (year, month))
            market_cap = fundamental1.loc[:, ['code', 'market_cap']]
            for i in range(0, len(market_cap)):
                market_cap.iloc[i, 1] = math.log(market_cap.iloc[i, 1])
            df = pd.merge(df, market_cap, how='left', on='code')
            '''获取技术指标BARA'''
            if month < 10:
                BR, AR = BRAR(HS300, '%d-%s-10' % (year, '0{}'.format(month)), N=26)
            else:
                BR, AR = BRAR(HS300, '%d-%d-10' % (year, month), N=26)
            df['BR'] = 0.0
            df['AR'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'BR'] = BR[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'AR'] = AR[(df.loc[i, ['code']]).iloc[0]]
            '''获取CYR和MACYR技术指标'''
            if month < 10:
                CYR1,MACYR1 = CYR(HS300, check_date='%d-%s-15' % (year, '0{}'.format(month)), N = 13, M = 5)
            else:
                CYR1,MACYR1 = CYR(HS300, check_date='%d-%d-15' % (year, month), N = 13, M = 5)
            df['CYR'] = 0.0
            df['MACYR'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'CYR'] = CYR1[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'MACYR'] = MACYR1[(df.loc[i, ['code']]).iloc[0]]
            '''获取AMO技术指标'''
            if month < 10:
                AMOW,AMO1,AMO2 = AMO(HS300, check_date='%d-%s-15' % (year, '0{}'.format(month)), M1 = 5, M2 = 10)
            else:
                AMOW,AMO1,AMO2 = AMO(HS300, check_date='%d-%d-15' % (year, month), M1 = 5, M2 = 10)
            df['AMOW'] = 0.0
            df['AMO1'] = 0.0
            df['AMO2'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'AMOW'] = AMOW[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'AMO1'] = AMO1[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'AMO2'] = AMO2[(df.loc[i, ['code']]).iloc[0]]
            '''获取VOL技术指标'''
            if month < 10:
                VOL1,MAVOL11,MAVOL12 = VOL(HS300, check_date='%d-%s-15' % (year, '0{}'.format(month)), M1=5, M2=10)
            else:
                VOL1,MAVOL11,MAVOL12 = VOL(HS300, check_date='%d-%d-15' % (year, month), M1=5, M2=10)
            df['VOL'] = 0.0
            df['MAVOL11'] = 0.0
            df['MAVOL12'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'VOL'] = VOL1[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'MAVOL11'] = MAVOL11[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'MAVOL12'] = MAVOL12[(df.loc[i, ['code']]).iloc[0]]
            '''获取AMV技术指标'''
            if month < 10:
                AMV1 = AMV(HS300,check_date='%d-%s-15' % (year, '0{}'.format(month)), timeperiod=13)
            else:
                AMV1 = AMV(HS300,check_date='%d-%d-15' % (year, month), timeperiod=13)
            df['AMV'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'AMV'] = AMV1[(df.loc[i, ['code']]).iloc[0]]
            '''获取MA技术指标'''
            if month < 10:
                MA1 = MA(HS300, check_date='%d-%s-15' % (year, '0{}'.format(month)), timeperiod=5)
            else:
                MA1 = MA(HS300, check_date='%d-%d-15' % (year, month), timeperiod=5)
            df['MA'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'MA'] = MA1[(df.loc[i, ['code']]).iloc[0]]
            '''获取BOLL布林线 技术指标'''
            if month < 10:
                upperband, middleband, lowerband = Bollinger_Bands(HS300, check_date='%d-%s-15' % (year, '0{}'.format(month)), timeperiod=20, nbdevup=2, nbdevdn=2)
            else:
                upperband, middleband, lowerband = Bollinger_Bands(HS300, check_date='%d-%d-15' % (year, month), timeperiod=20, nbdevup=2, nbdevdn=2)
            df['upperband'] = 0.0
            df['middleband'] = 0.0
            df['lowerband'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'upperband'] = upperband[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'middleband'] = middleband[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'lowerband'] = lowerband[(df.loc[i, ['code']]).iloc[0]]
            '''获取ENE 技术指标'''
            if month < 10:
                up1, low1, ENE1 = ENE(HS300,check_date='%d-%s-15' % (year, '0{}'.format(month)),N=25,M1=6,M2=6)
            else:
                up1, low1, ENE1 = ENE(HS300,check_date='%d-%d-15' % (year, month),N=25,M1=6,M2=6)
            df['up1'] = 0.0
            df['low1'] = 0.0
            df['ENE'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'up1'] = up1[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'low1'] = low1[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'ENE'] = ENE1[(df.loc[i, ['code']]).iloc[0]]
            '''获取CYE 技术指标'''
            if month < 10:
                CYEL,CYES = CYE(HS300,check_date='%d-%s-15' % (year, '0{}'.format(month)))
            else:
                CYEL,CYES = CYE(HS300,check_date='%d-%d-15' % (year, month))
            df['CYEL'] = 0.0
            df['CYES'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'CYEL'] = CYEL[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'CYES'] = CYES[(df.loc[i, ['code']]).iloc[0]]
            '''获取QR强弱指标 技术指标'''
            if month < 10:
                qr_gg, qr_dp, qr_qrz = QR('000300.XSHG',HS300,check_date='%d-%s-15' % (year, '0{}'.format(month)), N = 21)
            else:
                qr_gg, qr_dp, qr_qrz = QR('000300.XSHG',HS300,check_date='%d-%d-15' % (year, month), N = 21)
            df['qr_gg'] = 0.0
            df['qr_qrz'] = 0.0
            for i in range(0, len(df)):
                df.loc[i, 'qr_gg'] = qr_gg[(df.loc[i, ['code']]).iloc[0]]
                df.loc[i, 'qr_qrz'] = qr_qrz[(df.loc[i, ['code']]).iloc[0]]
            # 获取其他特征...
            
            # 按季度写入到文件
            write_file('%dq%d.csv'% (year, quarter), df.to_csv(), append=False)
    
# 下载沪深300历史数据，并计算每季度盈利率，用于打标签
def getHS300hist():
    df = attribute_history('000300.XSHG', 48, '60d')
    df['gain_ratio'] = 0.0
    for i in range(0, len(df)-1):
        df.iloc[i+1, 6] = df.iloc[i+1, 1] / df.iloc[i, 1] - 1
    write_file('沪深300历史指数.csv', df.to_csv(), append=False)

# 根据当季度首日开盘价格与最后一天收盘价格计算收益率
def calculate_gainRatio():
    body = read_file("沪深300历史指数.csv")
    HSindex = pd.read_csv(StringIO(body))
    HSindex.drop('Unnamed: 0',axis=1, inplace=True)
    temp = 0
    for year in range(2006, 2016):
        for quarter in range(1, 5):
            # 读出当前季度因子表
            body = read_file("%dq%d.csv" % (year, quarter))
            df = pd.read_csv(StringIO(body))
            df.drop('Unnamed: 0',axis=1, inplace=True)
            df['gain_ratio'] = 0.0
            df['label'] = -1
            # 把季度化为月份
            month = quarter*3-2
            nextMonth = month + 2
            temp = temp + 1
            for i in range(0, len(df)):
                # 从20xxqx的csv文件中提取出每行的股票代码myCode
                myCode = (df.loc[[i], 'code']).iloc[0]
                # 根据每行的股票代码查询当季度初开盘价
                try:
                    # 月份不满两位数要补零（API要求）
                    if month <= 9:
                        tempDF1 = get_price(myCode, start_date='%d-%s-10' % (year, '0{}'.format(month)), end_date='%d-%s-17' % (year, '0{}'.format(month)))
                    else:
                        tempDF1 = get_price(myCode, start_date='%d-%s-10' % (year, month), end_date='%d-%s-17' % (year, month))
                except:
                    log.info('not ok %s' % (myCode))
                else:
                    log.info('ok %s' % (myCode))
                try:
                    openPrice = (tempDF1.loc[:, 'open']).mean()
                except:
                    log.info('not ok %s' % (myCode))
                else:
                    log.info('ok %s' % (myCode))
                # 查询季度末收盘价
                try:
                    # 月份不满两位数要补零（tushare API要求）
                    if nextMonth <= 9:
                        tempDF2 = get_price(myCode, start_date='%d-%s-10' % (year, '0{}'.format(nextMonth)), end_date='%d-%s-17' % (year, '0{}'.format(nextMonth)))
                    else:
                        tempDF2 = get_price(myCode, start_date='%d-%s-10' % (year, nextMonth), end_date='%d-%s-17' % (year, nextMonth))
                except:
                    log.info('not ok %s' % (myCode))
                else:
                    log.info('ok %s' % (myCode))
                try:
                    closePrice = (tempDF2.loc[:, 'close']).mean()
                except:
                    log.info('not ok %s' % (myCode))
                else:
                    log.info('ok %s' % (myCode))
                # 计算收益率
                gain_ratio = closePrice / openPrice - 1 - HSindex.iloc[temp, 6]
                df.iloc[i, 52] = gain_ratio
                # if gain_ratio >= 0:
                #     df.iloc[i, 9] = 1
                # else:
                #     df.iloc[i, 9] = 0
            write_file('%dq%d.csv' % (year, quarter), df.to_csv(), append=False)
    
    
def mergeAllTable():
    year = 2006
    quarter = 1
    body = read_file("%dq%d.csv" % (year, quarter))
    df = pd.read_csv(StringIO(body))
    df.drop('Unnamed: 0',axis=1, inplace=True)
    ALLDATA = df
    quarter = 2
    body = read_file("%dq%d.csv" % (year, quarter))
    df = pd.read_csv(StringIO(body))
    df.drop('Unnamed: 0',axis=1, inplace=True)
    ALLDATA = ALLDATA.append(df, ignore_index=True)
    quarter = 3
    body = read_file("%dq%d.csv" % (year, quarter))
    df = pd.read_csv(StringIO(body))
    df.drop('Unnamed: 0',axis=1, inplace=True)
    ALLDATA = ALLDATA.append(df, ignore_index=True)
    quarter = 4
    body = read_file("%dq%d.csv" % (year, quarter))
    df = pd.read_csv(StringIO(body))
    df.drop('Unnamed: 0',axis=1, inplace=True)
    ALLDATA = ALLDATA.append(df, ignore_index=True)
    for year in range(2007, 2016):
        for quarter in range(1, 5):
            # 读出当前季度因子表
            body = read_file("%dq%d.csv" % (year, quarter))
            df = pd.read_csv(StringIO(body))
            df.drop('Unnamed: 0',axis=1, inplace=True)
            ALLDATA = ALLDATA.append(df, ignore_index=True)
    write_file('ALLDATA.csv', ALLDATA.to_csv(), append=False)



def tagLabel():
    body = read_file("ALLDATA.csv")
    df = pd.read_csv(StringIO(body))
    df.drop('Unnamed: 0',axis=1, inplace=True)
    # 根据盈利率对所有股票排序
    df = df.sort(['gain_ratio'], ascending=False)
    # # 删除未能正确计算盈利率的行
    # for i in range(len(df)-1, -1, -1):
    #     if math.isnan(df.iloc[i, 8]) == True:
    #         log.info('%d %f' % (i, df.iloc[i, 8]))
    #         df = df.drop([i])
    #     else:
    #         break
    # 盈利率前30%标记正类，后30%标记负类
    n = 0.3
    number = len(df.index) * n
    number = int(number)
    count = 0 #计数器
    # 标记正类
    for i in range(0, len(df)):
        df.iloc[i, 53] = 1
        count = count + 1
        if count == number:
            break
    # 标记负类
    count = 0
    for i in range(0, len(df)):
        if count < len(df) - number:
            count = count + 1
            continue
        else:
            df.iloc[i, 53] = 0
            count = count + 1
    write_file('tagedALLDATA.csv', df.to_csv(), append=False)
    
    
def tagIndustry():
    HY001 = get_industry_stocks('HY001')
    HY002 = get_industry_stocks('HY002')
    HY003 = get_industry_stocks('HY003')
    HY004 = get_industry_stocks('HY004')
    HY005 = get_industry_stocks('HY005')
    HY006 = get_industry_stocks('HY006')
    HY007 = get_industry_stocks('HY007')
    HY008 = get_industry_stocks('HY008')
    HY009 = get_industry_stocks('HY009')
    HY010 = get_industry_stocks('HY010')
    HY011 = get_industry_stocks('HY011')
    # 读取ALLDATA表
    body = read_file("tagedALLDATA.csv")
    df = pd.read_csv(StringIO(body))
    df.drop('Unnamed: 0',axis=1, inplace=True)
    # 在ALLDATA大表中增加一列存储行业信息
    df['HY'] = '00000'
    # 遍历每个股票代码，添加行业属性
    for i in range(0, len(df)):
        myCode = (df.loc[[i], 'code']).iloc[0]
        if myCode in HY001:
            df.iloc[i, 54] = 'HY001'
        elif myCode in HY002:
            df.iloc[i, 54] = 'HY002'
        elif myCode in HY003:
            df.iloc[i, 54] = 'HY003'
        elif myCode in HY004:
            df.iloc[i, 54] = 'HY004'
        elif myCode in HY005:
            df.iloc[i, 54] = 'HY005'
        elif myCode in HY006:
            df.iloc[i, 54] = 'HY006'
        elif myCode in HY007:
            df.iloc[i, 54] = 'HY007'
        elif myCode in HY008:
            df.iloc[i, 54] = 'HY008'
        elif myCode in HY009:
            df.iloc[i, 54] = 'HY009'
        elif myCode in HY010:
            df.iloc[i, 54] = 'HY010'
        elif myCode in HY011:
            df.iloc[i, 54] = 'HY011'
    write_file('tagedALLDATA.csv', df.to_csv(), append=False)

def test11():
    HS300 = get_index_stocks('000300.XSHG', '2006-01-10')
    year = 2006
    month = 10
    RSI1 = RSI(HS300, check_date='%d-%d-10' % (year, month), N1=20)
    

# # 根据当季度首日开盘价格与最后一天收盘价格计算收益率
# def calculate_gainRatio():
#     for year in range(2005, 2012):
#         for quarter in range(1, 5):
#             # 读出当前季度因子表
#             body = read_file("%dq%d.csv" % (year, quarter))
#             df = pd.read_csv(StringIO(body))
#             df.drop('Unnamed: 0',axis=1, inplace=True)
#             df['gain_ratio'] = 0.0
#             df['label'] = -1
#             # 把季度化为月份
#             month = quarter*3-2
#             nextMonth = month + 2
            
#             for i in range(0, len(df)):
#                 # 从20xxqx的csv文件中提取出每行的股票代码myCode
#                 myCode = (df.loc[[i], 'code']).iloc[0]
#                 myCode = myCode[0:6]
#                 # 根据每行的股票代码查询当季度初开盘价
#                 try:
#                     # 月份不满两位数要补零（tushare API要求）
#                     if month <= 9:
#                         tempDF1 = ts.get_k_data(myCode, start='%d-%s-10' % (year, '0{}'.format(month)), end='%d-%s-17' % (year, '0{}'.format(month)))
#                     else:
#                         tempDF1 = ts.get_k_data(myCode, start='%d-%s-10' % (year, month), end='%d-%s-17' % (year, month))
#                 except:
#                     log.info('not ok %s' % (myCode))
#                 else:
#                     log.info('ok %s' % (myCode))
#                 try:
#                     openPrice = (tempDF1.loc[:, 'open']).mean()
#                 except:
#                     log.info('not ok %s' % (myCode))
#                 else:
#                     log.info('ok %s' % (myCode))
#                 # 查询季度末收盘价
#                 try:
#                     # 月份不满两位数要补零（tushare API要求）
#                     if nextMonth <= 9:
#                         tempDF2 = ts.get_k_data(myCode, start='%d-%s-10' % (year, '0{}'.format(nextMonth)), end='%d-%s-17' % (year, '0{}'.format(nextMonth)))
#                     else:
#                         tempDF2 = ts.get_k_data(myCode, start='%d-%s-10' % (year, nextMonth), end='%d-%s-17' % (year, nextMonth))
#                 except:
#                     log.info('not ok %s' % (myCode))
#                 else:
#                     log.info('ok %s' % (myCode))
#                 try:
#                     closePrice = (tempDF2.loc[:, 'close']).mean()
#                 except:
#                     log.info('not ok %s' % (myCode))
#                 else:
#                     log.info('ok %s' % (myCode))
#                 # 计算收益率
#                 gain_ratio = closePrice / openPrice - 1
#                 df.iloc[i, 8] = gain_ratio
#                 # if gain_ratio >= 0:
#                 #     df.iloc[i, 9] = 1
#                 # else:
#                 #     df.iloc[i, 9] = 0
#             write_file('%dq%d.csv' % (year, quarter), df.to_csv(), append=False)