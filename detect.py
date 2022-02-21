import argparse
import math

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tensorflow as tf
from time import time as timing
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


def average(seq, total=0.0):
    num = 0
    for item in seq:
        total += item
        num += 1
    return total / num


def get_args():
    parser = argparse.ArgumentParser()


def main():
    actual_distance = np.array() # calculated from IMU data, odometer data, etc.    
    GNSS_ERROR = 10
    LSTM_PREDICT_ERROR = 0.058002
    SPOOFING_THRESHOLD = GNSS_ERROR + LSTM_PREDICT_ERROR 

    csv_file_path = '/root/autodl-nas/Chunk_03/99c94dc769b5d96e|2018-05-01--08-13-53.csv'
    df = pd.read_csv(csv_file_path)
    values = df.to_numpy()
    times = values[:, -1]
    distance = values[:, -2]
    model = tf.keras.models.load_model('gnss_spoofing_detect.h5')
    test_X = values[:, :3]

    scaler = MinMaxScaler(feature_range=(0, 1))
    test_X = scaler.fit_transform(test_X)
    test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
    
    test_y = distance
    yhat = model.predict(test_X)[:, 0]
    
    for idx, y_predict_point in enumerate(yhat):
        if abs(y_predict_point - actual_distance[idx]) > SPOOFING_THRESHOLD:
            print('>>> WARNING! <<<')
            print(f'GNSS SPOOFING OCCURED AT {idx}')

    # print(f'Test MAE: {mae}')
    # scores = model.evaluate(test_X, test_y)

    # plt.plot(times, yhat, label='prediction')
    # plt.plot(times, distance, label='round_truth')
    # plt.title('Comparison between truth and prediction', fontsize=18)
    # plt.xlabel('Boot time (s)', fontsize=18)
    # plt.ylabel('Distance travelled during single timestamp (m) ', fontsize=12)
    # plt.legend()
    # plt.savefig('eval.png')
    


if __name__ == '__main__':
    main()