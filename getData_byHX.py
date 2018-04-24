def getData():
    for year in range(2006, 2007):
        for quarter in range(1, 2):
            '''获取当季度的沪深300成份股'''
            month = quarter*3-2
            if month < 10:
                HS300 = get_index_stocks('000300.XSHG', '%d-%s-10' % (year, '0{}'.format(month)))
            else:
                HS300 = get_index_stocks('000300.XSHG', '%d-%d-10' % (year, month))
            #-------------------------------------------------开始获取数据--------------------------------------------------------
            '''获取财务数据'''
            df = get_fundamentals(query(
                valuation, income, indicator, cash_flow
            ).filter(
                # 这里不能使用 in 操作, 要使用in_()函数
                valuation.code.in_(HS300)
            ), statDate = '%dq%d' % (year, quarter))
            df.index=df['code']
            for i in range(1,48):
                a = eval('alpha_'+"%03d" % i)(str(year)+'-'+str(quarter*3)+'-10','000300.XSHG')
                df['alpha_'+"%03d" % i]=a
    return df