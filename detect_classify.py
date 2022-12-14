# -*- coding: utf-8 -*-
"""detect_classify.ipynb

"""

#!/usr/bin/env python
##ripeness
#classify
#use My_weights.model My_model.h5
"""
Created on Sat Nov 14 21:07:30 2020

@author: zobidasabah
"""
#connect google drive in Colab
#from google.colab import drive
#drive.mount('/content/drive')

#import libraries

import numpy as np
import cPickle as pickle
import cv2
import os
import matplotlib.pyplot as plt
from os import listdir
from sklearn.preprocessing import LabelBinarizer
from keras.models import Sequential
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation, Flatten, Dropout, Dense
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.preprocessing import image
from keras.preprocessing.image import img_to_array
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
import tensorflow as tf
from threading import Thread 
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)
#########################################


# Dimension of resized image
DEFAULT_IMAGE_SIZE = tuple((28, 28))
EPOCHS = 25
LR = 1e-3
BATCH_SIZE = 32
WIDTH = 28
HEIGHT = 28
DEPTH = 3

# Path to the dataset folder
root_dir = './drive/MyDrive/Ripeness/DATASET'

train_dir = os.path.join(root_dir, 'train')
val_dir = os.path.join(root_dir, 'val')
#test_dir= os.path.join(root_dir, 'test')
def convert_image_to_array(image_dir):
    try:
        image = cv2.imread(image_dir)
        if image is not None:
            image = cv2.resize(image, DEFAULT_IMAGE_SIZE)   
            return img_to_array(image)
        else:
            return np.array([])
    except Exception as e:
        print("Error : {e}")
        return None 

print("Done converting")

image_list, label_list = [], []

try:
    
    plant_disease_folder_list = listdir(train_dir)
    for directory in train_dir :
        # remove .DS_Store from list
        if directory == ".DS_Store" :
            train_dir.remove(directory)
    print("[INFO] .DS_Store files removed")
  
    print("[INFO] Files and directories in ./. ")  
    print(plant_disease_folder_list)
    print("[INFO] Loading images ...")

    for plant_disease_folder in plant_disease_folder_list:

      plant_disease_image_list = listdir(train_dir+'/'+plant_disease_folder)
      
      for image in plant_disease_image_list:
          image_directory = train_dir+'/'+plant_disease_folder+'/'+image
          if image_directory.endswith(".jpg")==True or image_directory.endswith(".JPG")==True:
               image_list.append(convert_image_to_array(image_directory))
               label_list.append(plant_disease_folder)
      print('[INFO] Loading',plant_disease_folder)

    print("[INFO] Image loading completed")  
except Exception, e:
    print("Error :",e)
# Transform the loaded training image data into numpy array

np_image_list = np.array(image_list, dtype=np.float16) / 225.0
print('[INFO] Transform the loaded training image data into numpy array Complete')

# Check the number of images loaded for training
image_len = len(image_list)
print("Total number of images: ", image_len)

#check the number of classes 

label_binarizer = LabelBinarizer()
image_labels = label_binarizer.fit_transform(label_list)

pickle.dump(label_binarizer,open('/content/drive/MyDrive/Ripeness/plant_disease_label_transform.pkl', 'wb'))
n_classes = len(label_binarizer.classes_)

print("Total number of classes: ", n_classes)

augment = ImageDataGenerator(rotation_range=25, width_shift_range=0.2,
                             height_shift_range=0.1, shear_range=0.1, 
                             zoom_range=0.2, horizontal_flip=True, 
                             fill_mode="nearest")

print("[INFO] Splitting data to train and test...")
#x_train, x_test, y_train, y_test = train_test_split(np_image_list, image_labels, test_size=0.2, random_state = 1, stratify=image_labels)

trainX, x_test, trainY, y_test = train_test_split(np_image_list, image_labels, test_size=0.1, random_state = 1, stratify=image_labels)

# test is now 10% of the initial data set
# validation is now x% of the initial data set
x_train, x_val, y_train, y_val = train_test_split(trainX, trainY, test_size=0.2,  random_state = 1,stratify=trainY) 





#Build Model


#Creating a sequential model and adding Convolutional, Normalization, Pooling, Dropout and Activation layers at the appropriate positions.
print("[INFO] Summay of creating a sequential model and adding layers at the appropriate positions")
model = Sequential()

inputShape = (HEIGHT, WIDTH, DEPTH)
chanDim = -1

if K.image_data_format() == "channels_first":
    inputShape = (DEPTH, HEIGHT, WIDTH)
    chanDim = 1

model.add(Conv2D(32, (3, 3), padding="same",input_shape=inputShape))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=chanDim))
model.add(MaxPooling2D(pool_size=(3, 3)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=chanDim))
model.add(Dropout(0.5))

model.add(Conv2D(64, (3, 3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=chanDim))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))

model.add(Conv2D(128, (3, 3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=chanDim))
model.add(Dropout(0.5))

model.add(Conv2D(128, (3, 3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=chanDim))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))

model.add(Flatten())
model.add(Dense(1024))
model.add(Activation("relu"))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Dense(1024))
model.add(Activation("relu"))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Dense(n_classes))
model.add(Activation("softmax"))

model.summary()
#############################################

#Train Model

# Initialize optimizer
opt = Adam(lr=LR, decay=LR / EPOCHS)


# Compile model
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

# Train model
print("[INFO] Training network...")



history = model.fit(augment.flow(x_train, y_train, batch_size=BATCH_SIZE),
                                 validation_data= (x_val, y_val),
                                 steps_per_epoch=len(x_train) // BATCH_SIZE,
                                 epochs=EPOCHS, 
                                 verbose=1)

#Evaluate model

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)

# Train and validation accuracy
# plot the training loss and accuracy
plt.style.use("ggplot")
plt.figure()
N = EPOCHS
plt.plot(np.arange(0, N), history.history["loss"], label="train_loss")
plt.plot(np.arange(0, N), history.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, N), history.history["accuracy"], label="train_acc")
plt.plot(np.arange(0, N), history.history["val_accuracy"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend(loc="lower left")

#######


#accuracy evaluation

print("[INFO] Calculating model accuracy")
scores = model.evaluate(x_test, y_test)
#scores = model.evaluate_generator(valid_generator)
print("Test accuracy = ", (scores[1]*100))

#######################################

print("[INFO] Saving model...")

model.save("/content/drive/MyDrive/Ripeness/new_try.h5")
model.save_weights('/content/drive/MyDrive/Ripeness/new_weights.model')
###################################


####################################


print("[INFO] Saving label transform...")
filename = '/content/drive/MyDrive/Ripeness/plant_disease_label_transform.pkl'
image_labels = pickle.load(open(filename, 'rb'))

###############################

#Test_Model
def predict_ripe(image_path):
    image_array = convert_image_to_array(image_path)
    np_image = np.array(image_array, dtype=np.float16) / 225.0
    np_image = np.expand_dims(np_image,0)
    plt.figure()
    plt.imshow(plt.imread(image_path))
    result= np.argmax(model.predict(np_image), axis=-1)
    #result = model.predict_classes(np_image)
    print((image_labels.classes_[result][0]))
  
predict_ripe('/content/drive/MyDrive/Ripeness/DATASET/test/Tomato_Ripe/10_100.jpg')



test_data= (x_test, y_test)
Y_pred = model.predict(test_data)
y_pred = np.argmax(Y_pred, axis=1)


#Print Classification Report

print('Classification Report')

print(classification_report(image_labels, y_pred, target_names=target_names))
