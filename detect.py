import argparse
import math

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tensorflow as tf
from time import time as timing
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler

gpus = None


def average(seq, total=0.0):
    num = 0
    for item in seq:
        total += item
        num += 1
    return total / num


def get_args():
    parser = argparse.ArgumentParser()

def detect_init():
    global gpus
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)


def detect():
    GNSS_ERROR = 1.5
    LSTM_PREDICT_ERROR = 0.058002
    SPOOFING_THRESHOLD = GNSS_ERROR + LSTM_PREDICT_ERROR 

    csv_file_path = 'test/test.csv' 
    df = pd.read_csv(csv_file_path)
    values = df.to_numpy()
    times = values[:, -1]
    distance = values[:, -2]
    model = tf.keras.models.load_model('lstm_all_data.h5')
    test_X = values[:, :3]

    scaler = MinMaxScaler(feature_range=(0, 1))
    test_X = scaler.fit_transform(test_X)
    test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
    
    test_y = distance
    yhat = model.predict(test_X)[:, 0]
    
    for idx, y_predict_point in enumerate(yhat):
        if abs(y_predict_point - distance[idx]) > SPOOFING_THRESHOLD:
            print('>>> WARNING! <<<')
            print(f'GNSS SPOOFING OCCURED AT {idx}')
            input()
    
if __name__ == '__main__':
    detect_init()
    detect()
