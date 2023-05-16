#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 11:15:08 2023

@author: zackkingbackup
"""

from mlforecast import MLForecast
from sklearn.linear_model import LinearRegression
from mlforecast.target_transforms import Differences
from mlforecast.utils import PredictionIntervals

#import lightgbm as lgb
import xgboost as xgb

import pandas as pd

#df = pd.read_csv("/Users/zackkingbackup/Documents/DataScienceProjects/PyData2023 Learnings Demos/DominionBillingHistory/Usage-Table 1.csv")

df = pd.read_csv("/Users/zackkingbackup/Documents/DataScienceProjects/PyData2023 Learnings Demos/DominionBillingHistoryManuallyUpdated/Billing History-Table 1.csv")
df['const'] = 1
#df['Meter Read Date'] = pd.to_datetime(df['Meter Read Date'])
df['Statement Date'] = pd.to_datetime(df['Statement Date'])

def convert_acct_bal(bal):
    bal = bal.replace("$","").strip()
    return float(bal)

df['Total Account Balance'] = df.apply(lambda x: convert_acct_bal(x['Total Account Balance']), axis=1)
df['y'] = df['Total Account Balance']

mlf = MLForecast(
    #models = [LinearRegression(), xgb.XGBRegressor()], #lgb.LGBMRegressor(random_state=0)],
    models = [LinearRegression()],
    freq = 'M',
    lags = range(1,12),
    
    #lags = [12]
    target_transforms=[Differences([1])] #use if clear trend (might be good for training on $$$)
)
#mlf.fit(df[['const', 'Meter Read Date', 'Usage (kWh)']], 
mlf.fit(df[['const', 'Statement Date', 'y']],
        time_col='Statement Date', target_col='y', 
        id_col='const',
        prediction_intervals=PredictionIntervals(window_size=6, n_windows=2)
        )

df_pred = mlf.predict(6, level=[95.])

df_all = pd.concat([df, df_pred]).set_index('Statement Date')
df_all[['y', 'LinearRegression']].plot()#, 'XGBRegressor']].plot()


