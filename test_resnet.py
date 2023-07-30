import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import os
import numpy as np
import cv2
import random
import bisect
from tensorflow.keras.utils import Sequence
root_dir = "/home2/random_bev_carla/rgb_bev/Town01_1"

val_images = []
val_labels = []
for root, subdirs, files in os.walk(root_dir):
    for f in files:
        if 'observation_rgb.npy' in f:
            print(root)
            rgb = np.load(os.path.join(root, f), mmap_mode='r')
            print(rgb.shape)
            val_images.append(rgb)

        elif 'label' in f:
            l = np.load(os.path.join(root, f))
            val_labels.append(l)


class DataGenerator(Sequence):
    def __init__(self, x_set, y_set, batch_size):
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size
        self.each_len = self.cal_len()

    def __len__(self):
        return int(np.ceil(self.each_len[-1] / float(self.batch_size)))

    def __getitem__(self, idx):
        idx = idx * self.batch_size
        file_ind = bisect.bisect_right(self.each_len, idx)
        if file_ind == 0:
            im_ind = idx
        else:
            im_ind = idx - self.each_len[file_ind - 1]
        # print(idx, file_ind, im_ind, self.each_len)

        batch_x = self.x[file_ind][im_ind:im_ind + self.batch_size] / 255.0
        batch_y = self.y[file_ind][im_ind:im_ind + self.batch_size]
        return batch_x, batch_y

    def cal_len(self):
        each_len = []
        for i in range(len(self.y)):
            if len(each_len) == 0:
                each_len.append(self.y[i].shape[0])
            else:
                each_len.append(self.y[i].shape[0] + each_len[-1])
        return each_len

reconstructed_model = models.load_model("/lab/kiran/img2cmd_data/model")
reconstructed_model.compile(loss="sparse_categorical_crossentropy",
                                    metrics=['accuracy'])

train_gen = DataGenerator(val_images, val_labels, 256)
print(reconstructed_model.evaluate(train_gen))
