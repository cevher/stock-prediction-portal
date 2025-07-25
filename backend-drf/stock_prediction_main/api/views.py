from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from django.conf import settings

from .serializers import StockPredictionSerializer
from .utils import save_plot
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from sklearn.metrics import mean_squared_error, r2_score


class StockPredictionAPIView(APIView):
    
    def post(self, request):
        serializer = StockPredictionSerializer(data=request.data)
        
        if serializer.is_valid():
            ticker = serializer.validated_data['ticker']  
            
            # the ticker data from yfinance
            now = datetime.now()
            start = datetime(now.year-10, now.month, now.day)
            end = now
            df = yf.download(ticker, start, end)
            print(df)
            if(df.empty):
                return Response({"error": "No data found for the given ticker.", "status": status.HTTP_404_NOT_FOUND})
            df = df.reset_index()
            
            # Generate basic plot
            plt.switch_backend('AGG') #save the plot into img file
            plt.figure(figsize=(12,5))
            plt.plot(df.Close, label='Closing Price')
            plt.title(f'Closing Price of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Close Price')
            plt.legend()
            #save the plot to media folder
            plot_img_path =f'{ticker}_plot.png'
            
            plot_img = save_plot(plot_img_path)
            
            
            ma100 = df.Close.rolling(100).mean()
            plt.switch_backend('AGG') #save the plot into img file
            plt.figure(figsize=(12,5))
            plt.plot(df.Close, label='Closing Price')
            plt.plot(ma100, 'r', label='100 MA')
            plt.title(f'Closing Price of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Close Price')
            plt.legend()
            plot_img_path =f'{ticker}_100_dma.png'
            plot_100_dma = save_plot(plot_img_path)
            
            
            ma200 = df.Close.rolling(200).mean()
            plt.switch_backend('AGG') #save the plot into img file
            plt.figure(figsize=(12,5))
            plt.plot(df.Close, label='Closing Price')
            plt.plot(ma100, 'r', label='100 MA')
            plt.plot(ma200, 'y', label='200 MA')
            plt.title(f'Closing Price of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Close Price')
            plt.legend()
            plot_img_path =f'{ticker}_200_dma.png'
            plot_200_dma = save_plot(plot_img_path)
            
            
            #splitting data into Training and Testing datasets
            data_training = pd.DataFrame(df.Close[0:int(len(df)*0.7)]) 
            data_testing = pd.DataFrame(df.Close[int(len(df)*0.7):]) 
            
            
            # Normalize data
            scaler = MinMaxScaler(feature_range=(0,1))
            
            #load model
            model = load_model('stock_predictor.keras')
            
            # preparing test data
            past_100_days = data_training.tail(100)
            final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
            input_data = scaler.fit_transform(final_df)
            print("input_data==>", input_data)
            
            x_test = []
            y_test = []

            for i in range(100, input_data.shape[0]):
                x_test.append(input_data[i-100:i])
                y_test.append(input_data[i, 0])
            
            x_test = np.array(x_test)
            y_test = np.array(y_test)
            
            #Making predictions
            y_predicted = model.predict(x_test)
            
            # Revert the scaled prices to original prices
            
            y_predicted = scaler.inverse_transform(y_predicted.reshape(-1, 1)).flatten()
            y_test = scaler.inverse_transform(y_test.reshape(-1,1)).flatten()
         
            
            # Plot the final prediction
            plt.switch_backend('AGG') #save the plot into img file
            plt.figure(figsize=(12,5))
            plt.plot(y_test, 'b', label='Original Price')
            plt.plot(y_predicted, 'r', label='Predicted Price')
            plt.title(f'Final Prediction for {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            
            plot_img_path =f'{ticker}_final_prediction.png'
            plot_prediction = save_plot(plot_img_path)
            
            
            # Model evaluation
            # MSE RMSE
            mse = mean_squared_error(y_test, y_predicted)
            print("MSE: ", mse)
            rmse = np.sqrt(mse)
            print("RMSE: ", rmse)   
            r2 = r2_score(y_test, y_predicted)
            print("R2 :", r2)
            
            return Response({'status': 'success', 
                             'plot_img': plot_img,
                             'plot_100_dma': plot_100_dma,
                             'plot_200_dma': plot_200_dma,
                             'plot_prediction': plot_prediction,
                             'mse': mse,
                             'rmse': rmse,
                             'r_score': r2})
