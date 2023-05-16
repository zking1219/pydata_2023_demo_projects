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
import datetime

#df = pd.read_csv("/Users/zackkingbackup/Documents/DataScienceProjects/PyData2023 Learnings Demos/DominionBillingHistory/Usage-Table 1.csv")

df = pd.read_csv("/Users/zackkingbackup/Documents/DataScienceProjects/PyData2023 Learnings Demos/DominionBillingHistoryManuallyUpdated/Billing History-Table 1.csv")
df['const'] = 1
#df['Meter Read Date'] = pd.to_datetime(df['Meter Read Date'])
df['Statement Date'] = pd.to_datetime(df['Statement Date'])
df['ds'] = df['Statement Date']
# NOTE - these dates are no good, they won't merge with dates created from pd.DateRange
# Replace with those dates
# datelist = pd.date_range(datetime.datetime(2023,5,1), periods=int(26.8*12), freq='M').tolist()
datelist = pd.date_range(datetime.datetime(2020,6,11), periods=36, freq='M').tolist()
df['ds'] = datelist


df['unique_id'] = [1 for idx in range(len(df))]

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
mlf.fit(df[['ds', 'y', 'unique_id']],
        prediction_intervals=PredictionIntervals(window_size=6, n_windows=2)
        )

df_pred = mlf.predict(6, level=[95.])

df_all = pd.concat([df, df_pred]).set_index('ds')
df_all[['y', 'LinearRegression']].plot()#, 'XGBRegressor']].plot()


