import os
import pandas as pd
import math
import numpy as np
import argparse
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from keras import optimizers
import tensorflow as tf
from tqdm import tqdm
from time import time as timing
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


def create_model():
    # 设计网络
    model = Sequential()
    model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(Dense(1))
    # 设置学习率等参数
    # adam = optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    model.compile(loss='mae', optimizer='adam')
    return model


def process_data(csv_file_path):
    df = pd.read_csv(CSV_FILE_PATH)
    values = df.to_numpy()
    times = values[:, -1]
    distance = values[:, -2]
    scaler = MinMaxScaler(feature_range=(0, 1))
    X, y = scaler.fit_transform(values[:, :-2]), distance
    X = X.reshape((X.shape[0], 1, X.shape[1]))

    return X, y


def train(model, train_csv_file_path, test_csv_file_path):
    train_X, train_y = process_data(train_csv_file_path)
    test_X, test_y = process_data(test_csv_file_path)
    
    model.fit(train_X, train_y, epochs=100, batch_size=64, validation_data=(test_X, test_y), verbose=2, shuffle=False)

    return model    


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root', type=str, default='/root/autodl-nas/')
    parser.add_argument('--test_csv_path', type=str, default='')

    args = parser.parse_args()
    return args


def main(args):
    data_root = args.data_root
    test_csv_path = args.test_csv_path
    chunks = os.listdir(data_root)
    
    model = create_model()
    for chunk in chunks:
        csv_files = filter(lambda f: f.split('.')[-1] == 'csv', os.listdir(chunk))
        for csv in csv_files:
            model = train(model, os.path.join(data_root, chunk, csv), test_csv_path)
    
    # plot history
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='test')
    plt.legend()
    plt.savefig('train_result.png')


if __name__ == '__main__':
    args = get_args()
    main(args)
