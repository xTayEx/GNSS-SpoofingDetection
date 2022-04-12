import os
import pandas as pd
import math
import numpy as np
import argparse
from tqdm import tqdm
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Masking
from keras.layers import LSTM
from keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from keras import optimizers
import tensorflow as tf
import requests
from tqdm import tqdm
from time import time as timing
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


def create_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, input_shape=input_shape))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam')
    return model


def process_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    values = df.to_numpy()
    times = values[:, -1]
    distance = values[:, -2]
    scaler = MinMaxScaler(feature_range=(0, 1))
    X, y = scaler.fit_transform(values[:, :-2]), distance
    X = X.reshape((X.shape[0], 1, X.shape[1]))
    # print(X.shape)
    # print(X)
    return X, y


def train(model, train_csv_file_path, test_csv_file_path):
    train_X, train_y = process_data(train_csv_file_path)
    test_X, test_y = process_data(test_csv_file_path)
    
    history = model.fit(train_X, train_y, epochs=1, batch_size=64, validation_data=(test_X, test_y), verbose=2, shuffle=False)

    return model, history    


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shutdown', action='store_true')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--data_root', type=str, default='/root/autodl-nas/')
    parser.add_argument('--test_csv_path', type=str, default="/root/99c94dc769b5d96e|2018-07-10--10-01-44.csv")

    args = parser.parse_args()
    return args


def main(args):
    epochs = args.epochs
    data_root = args.data_root
    test_csv_path = args.test_csv_path
    chunks = os.listdir(data_root)
    
    loss = []
    val_loss = []
    model = create_model((1, 3))
    for epoch in tqdm(range(epochs)):
        for chunk in chunks:
            chunk_path = os.path.join(data_root, chunk)
            if not os.path.isdir(chunk_path):
                print(f'{chunk_path} is not dir!')
                continue
            csv_files = filter(lambda f: f.split('.')[-1] == 'csv', os.listdir(chunk_path))
            for csv in csv_files:
                print(f'csv file is {csv}')
                model, history = train(model, os.path.join(data_root, chunk, csv), test_csv_path)
                loss += history.history['loss']
                val_loss += history.history['val_loss']

    print(loss)
    print(val_loss)
    model.save('lstm_all_data.h5')

    # plot history
    plt.plot(loss, label='train')
    plt.plot(val_loss, label='test')
    plt.legend()
    plt.savefig('train_result.png')


if __name__ == '__main__':
    args = get_args()
    print(args)
    try:
        main(args)
    except Exception as e:
        resp = requests.post('https://www.autodl.com/api/v1/wechat/message/push', json={
            'token': '9ae892707a79',
            'title': 'Exception',
            'name': 'GNSS Spoofing Detection',
            'content': str(e)
        })

    else:
        success_content = 'Done!'
        if args.shutdown:
            success_content += ' Server will be shutdown in 1 min...'
        
        resp = requests.post('https://www.autodl.com/api/v1/wechat/message/push', json={
            'token': '9ae892707a79',
            'title': 'Success',
            'name': 'GNSS Spoofing Detection',
            'content': 'Done'
        })
        if args.shutdown:
            os.system('shutdown +1')
