# -*- coding: utf-8 -*-
"""Time Series  - Prophet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r54zHyZOJQf0ox254OghlXXT5Tz6bKcg
"""

import pandas as pd
import io

from google.colab import files
data_to_load = files.upload()
    
df = pd.read_csv(io.BytesIO(data_to_load['covid19indo-all-bersih.csv']), error_bad_lines=False)

df.head(15)

df.info()

pip install fbprophet

pip install dask

pip install "dask[complete]"

# Commented out IPython magic to ensure Python compatibility.
from warnings import simplefilter
simplefilter (action ='ignore', category=FutureWarning)

import dask.dataframe as dd
import dask.array as da

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from sklearn.metrics import r2_score

df.corr()

df_date = df.groupby('Date')[['Total Kasus','Sembuh','Meninggal','Aktif']].sum()
df_date.head(15)

plt.figure(figsize=(15,10))
plt.plot (df_date["Sembuh"], color='g', label='Recovered')
plt.plot (df_date["Total Kasus"], color='b', label='Confirmed')
plt.plot (df_date["Meninggal"], color='r', label='Death')
plt.plot (df_date["Aktif"], color='k', label='Current Case')
plt.title ('Indonesian Covid-19 Cases')
plt.legend()

#Modelling

#Inisialization
from fbprophet import Prophet
model = Prophet()

#Adding seasonality
#30.42 is the average days in a month of a year
model.add_seasonality(name='Monthly', period=30.42, fourier_order=5)

#Data Splitting Into Test and Training Sets

df_date_reset = df_date.reset_index()
df_recovered = df_date_reset[['Date','Sembuh']]
df_confirmed = df_date_reset[['Date','Total Kasus']]
df_death = df_date_reset[['Date','Meninggal']]
df_current_case = df_date_reset[['Date','Aktif']]

#Using ds and y varibles tof prophet to predict

def rename_func (dataframe):
  cols = dataframe.columns
  dataframe = dataframe.rename(columns = {cols[0]: 'ds', cols[1]:'y'})
  return dataframe

df_recovered = rename_func(df_recovered)
df_confirmed = rename_func(df_confirmed)
df_death = rename_func(df_death)
df_current_case = rename_func(df_current_case)

df_current_case.head()

#dataframe is the dataframe to split, ratio is the training dataset ratio
def train_test_split(dataframe, ratio):
  divisor = round ((ratio/100)*dataframe.shape[0])
  train = dataframe.iloc[:divisor]
  test = dataframe.iloc[divisor:]
  return train, test, divisor

current_case_train, current_case_test, divisor = train_test_split(df_current_case,40)
current_case_train.shape, current_case_test.shape

#Model Fitting

model.fit(current_case_train)

#Model Prediction
#Creating future date
future_date = model.make_future_dataframe(periods=127)

#Doing Prediction
prediction = model.predict(future_date)

prediction.head()

model.plot_components(prediction)

#Evaluating The Model Using R-Square

def check_metrics (test, prediction):
  R2_score = r2_score(test['y'], prediction['yhat'].iloc[divisor:])
  print(R2_score)

check_metrics(current_case_test, prediction)

#Looking Deeper into Points of Changes

from fbprophet.plot import add_changepoints_to_plot
fig = model.plot(prediction)
changes = add_changepoints_to_plot(fig.gca(), model, prediction)

