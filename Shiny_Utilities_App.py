#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 08:32:05 2023

@author: zackkingbackup

Shiny demo application scratch work

Part 1: Display graph of average monthly power bills 
 - until 2050 increasing at ~4.5% APR
 - also include alternative fixed rate (horizontal asymptote)
 - display the date of intersection
"""
import datetime
import plotly
import pandas as pd
import numpy as np

avg_bill = 170 # 2023 pre July rate hike of 10%
rate = 0.045

# Get list of months to plot
datelist = pd.date_range(datetime.datetime(2023,5,1), periods=int(26.8*12), freq='M').tolist()
#bills = avg_bill + np.random.normal(0,30, len(datelist)) + 
bills = []
start_year = int(datelist[0].year)
for dt in datelist:
    # Apply annual increases - perturb rates later to be more realistic
    years_from_today = dt.year - start_year
    base_bill = avg_bill*((1+rate)**years_from_today)
    
    # Add noise to monthly bill - get kwH used from mlforecast later and convert to a bill
    # in today's dollars
    bills.append(base_bill + np.random.normal(0,30*((1+rate)**years_from_today)))
    
bills_df = pd.DataFrame({"date" : datelist, "power_bill" : bills})


# When is the breakeven date?
bills_df['net_metering'] = 300

bills_df['delta'] = bills_df['power_bill'] - bills_df['net_metering']

