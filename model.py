import os
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support as score

from config import Config
from generator import DataGenerator


os.environ["CUDA_VISIBLE_DEVICES"] = '1'

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    tf.config.experimental.set_virtual_device_configuration(
        gpus[0],
        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=8192)])
  except RuntimeError as e:
    print(e)


class CNN:
    def __init__(self, modelname):
        self.modelname = modelname
        params = {'dim': (Config.NUM_ID, 4*Config.NUM_INTVL),
          'batch_size': 256,
          'n_classes': 2,
          'n_channels': 1,
          'shuffle': True}

        data = os.listdir(Config.DATAPATH)
        data.remove('labels.npy')
        labels = np.load(Config.DATAPATH+"labels.npy")
        data_train = data[:int(len(data)/10*8)]
        data_valid = data[int(len(data)/10*8):]
        self.gen_train = DataGenerator(data_train, labels, **params)
        self.gen_valid = DataGenerator(data_valid, labels, **params)

        params['shuffle'] = False

        data_test = os.listdir(Config.DATAPATH[:-1]+"_test/")
        data_test.remove('labels.npy')
        data_test = data_test[int(len(data_test)/10*8):]
        labels_test = np.load(Config.DATAPATH+"labels.npy")
        self.gen_test = DataGenerator(data_test, labels_test, **params)

        self.model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(Config.NUM_ID, Config.NUM_INTVL*4, 1)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid'),
        ])

        self.model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy'],
        )

    def show_result(self, hist):
        plt.title("Trainning result")
        loss_ax = plt.gca()
        acc_ax = loss_ax.twinx()
        loss_ax.plot(hist.history['loss'], 'C0', marker='.', label='train loss')
        acc_ax.plot(hist.history['acc'], 'C1', marker='.', label='train acc')
        loss_ax.plot(hist.history['val_loss'], 'C2', marker='.', label='val loss')
        acc_ax.plot(hist.history['val_acc'], 'C3', marker='.', label='val acc')
        loss_ax.set_xlabel('epoch')
        loss_ax.set_ylabel('loss')
        acc_ax.set_ylabel('accuray')
        loss_ax.legend(loc='upper left')
        acc_ax.legend(loc='lower left')
        plt.grid(b=True, which='major', linestyle='--')
        plt.savefig('Trainning result.png')
        plt.show()
        
    def train(self):
        hist = self.model.fit(self.gen_train,
                        validation_data=self.gen_valid,
                        epochs=10,)
        self.model.save(self.modelname)
        self.show_result(hist)

    def test(self):
        self.model = tf.keras.models.load_model(self.modelname)
        y_pred = self.model.predict_classes(self.gen_test)
        y_true = self.gen_test.y_true[:]
        loss, acc = self.model.evaluate(self.gen_test, verbose=2)
        precision, recall, f1, _ = score(y_true, y_pred, zero_division=1)
        print(acc)
        print(precision)
        print(recall)
        
        return (loss, acc, precision, recall, f1)


if __name__ == "__main__":
    cnn = CNN(Config.MODELNAME)
    cnn.train()
    cnn.test()