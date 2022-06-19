# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Building accident detection nn model
# Date Created: 20/06/2022

from matplotlib import testing
import tensorflow as tf
from keras.models import Sequential
from keras.layers import BatchNormalization, Conv2D, Flatten, Dense, MaxPooling2D, InputLayer
from keras.applications import VGG19
from keras.callbacks import ModelCheckpoint
import os
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
import pandas as pd
import pickle
from PIL import Image
from sklearn.model_selection import train_test_split

# # Configure batch processing specs
# batch_size = 100
# img_h = 128
# img_w = 128

# src_path_train = os.path.abspath('accident_detect/accident_data/train/')
# src_path_val = os.path.abspath('accident_detect/accident_data/val/')
# src_path_test = os.path.abspath('accident_detect/accident_data/test/')

# # Obtain the well-splitted dataset for training and validation, testing
# datagen = tf.keras.preprocessing.image.ImageDataGenerator()

# training_ds = datagen.flow_from_directory(
#     src_path_train,
#     seed=42,
#     target_size=(img_h, img_w),
#     batch_size=batch_size
# )

# validation_ds = datagen.flow_from_directory(
#     src_path_val,
#     seed=42,
#     target_size= (img_h, img_w),
#     batch_size=batch_size
# )

# testing_ds = datagen.flow_from_directory(
#     src_path_test,
#     seed=42,
#     target_size= (img_h, img_w),
#     batch_size=batch_size
# )

# # Set class label
# class_names = ['Accidnet', 'Non Accident']

# # Define CNN Model
# base5 = VGG19(weights='imagenet', include_top=False, input_shape=(128, 128, 3))  
# NN_transfer_5 = Sequential(
#                         [InputLayer(input_shape=(128,128,3)),
#                          base5,
#                          Flatten(),  # should be fine , or add layers
#                          Dense(128, activation='relu'),
#                          Dense(64, activation='relu'),
#                          Dense(32, activation='relu'),   # 2 dense is must bcuz VGG16 model Conv2D twice and Maxpooling -> get a lot more features
#                          Dense(2, activation='sigmoid')]
#                        )

# # MyCNN = Sequential([
# #   BatchNormalization(input_shape=(128,128,3)),
# #   Conv2D(32, 3, activation='relu'),
# #   MaxPooling2D(),
# #   Conv2D(64, 3, activation='relu'),
# #   MaxPooling2D(),
# #   Conv2D(128, 3, activation='relu'),
# #   MaxPooling2D(),
# #   Flatten(),
# #   Dense(256, activation='relu'),
    
# #   Dense(2, activation= 'softmax')#Softmax is often used as the activation for the last layer of a classification network because the result could be interpreted as a probability distribution.
# # ])
# #Computes the crossentropy loss between the labels and predictions.

# NN_transfer_5.compile(optimizer='adam',loss='categorical_crossentropy', metrics=['accuracy'])

# # Train the model
# model = NN_transfer_5.fit_generator(training_ds, validation_data= validation_ds, epochs = 30, steps_per_epoch = ceil(training_ds.n/training_ds.batch_size), validation_steps = ceil(validation_ds.n/validation_ds.batch_size))

# # # Evaluate the model
# # AccuracyVector = []
# # plt.figure(figsize=(30, 30))
# # for images, labels in testing_ds.take(1):
# #     predictions = MyCNN.predict_generator(images)
# #     predlabel = []
# #     prdlbl = []
    
# #     for n in predictions:
# #         predlabel.append(class_names[np.argmax(n)])
# #         prdlbl.append(np.argmax(n))
    
# #     AccuracyVector = np.array(prdlbl) == labels
# #     for i in range(40):
# #         ax = plt.subplot(10, 4, i + 1)
# #         plt.imshow(images[i].numpy().astype("uint8"))
# #         plt.title('Predict : '+ predlabel[i]+'   Real :'+class_names[labels[i]] )
# #         plt.axis('off')
# #         plt.grid(True)
# # plt.show()

# # Evaluate model
# NN_transfer_5.evaluate_generator(generator=validation_ds, steps=ceil(validation_ds.n/validation_ds.batch_size))

# # Test model
# testing_ds.reset()
# predict = NN_transfer_5.predict_generator(testing_ds, steps = ceil(testing_ds.n/testing_ds.batch_size))
# # predict the class label
# y_classes = np.argmax(predict, axis=-1)
# labels = (training_ds.class_indices)
# print(labels)
# labels = dict((v,k) for k,v in labels.items())
# predictions = [labels[k] for k in y_classes]

# filenames=testing_ds.filenames
# results=pd.DataFrame({"Filename":filenames,
#                       "Predictions":predictions})
# results.to_csv("results.csv",index=False)

# # Save model if evaluated good
# # NN_transfer_5.save("acci_cnn_model.h5")
# NN_transfer_5.save("acci_VGG19_model.h5")

# =========================================================================

# Read all accident images in training set
list_images_accident = []
name_accident= []
for dirname, _, filenames in os.walk('accident_detect/new_data/Accident/'):
    for filename in filenames:
        list_images_accident.append(os.path.join(dirname, filename))
        name_accident.append(filename)
# print(list_images_accident)

open_file = open("list_images_accident.txt", "wb")
pickle.dump(list_images_accident, open_file)
open_file.close()

df_images_accident = pd.DataFrame()
df_images_accident["File_Name"] = name_accident
df_images_accident["Class"] = "Accident"
# print(df_images_accident)

# Read all non accident images that in training set
list_images_no_accident = []
name_no_accident= []
for dirname_2, _, filenames_2 in os.walk('accident_detect/new_data/Non Accident/'):
    for filename in filenames_2:
        list_images_no_accident.append(os.path.join(dirname_2, filename))
        name_no_accident.append(filename)
# print(list_images_no_accident)

open_file = open("list_images_no_accident.txt", "wb")
pickle.dump(list_images_no_accident, open_file)
open_file.close()

df_images_no_accident = pd.DataFrame()
df_images_no_accident["File_Name"] = name_no_accident
df_images_no_accident["Class"] = "Non Accident"
# print(df_images_no_accident)

# Combine all
df_all_images = pd.concat([df_images_accident, df_images_no_accident], ignore_index=True)

# Preprocess images
def prepare_image(img_path):
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128,128))
    x = tf.keras.preprocessing.image.img_to_array(img)
    
    return x

images = []
labels = []

directory = os.fsencode('accident_detect/new_data/')

for folder in os.listdir(directory):
    label = os.fsdecode(folder)
    for img in os.listdir(f'accident_detect/new_data/{label}'):
        img_name = os.fsdecode(img)
        images.append(prepare_image(f'accident_detect/new_data/{label}/{img_name}'))
        labels.append(label)
        
label_0_1 = [int(labels[w].replace('Non Accident', "0").replace("Accident",'1')) for w in range(len(labels))]

X, Y = images, label_0_1

# Convert to numpy array
X = np.array(X)
Y = np.array(Y)

open_file = open("img_128x128.txt", "wb")
pickle.dump(X, open_file)
open_file.close()

open_file = open("label_128x128.txt", "wb")
pickle.dump(Y, open_file)
open_file.close()

with open("img_128x128.txt", "rb") as fp: 
    x = pickle.load(fp)
    
with open("label_128x128.txt", "rb") as fp: 
    y= pickle.load(fp)
    
# Split dataset for training testing validation
x_train_val, x_test, y_train_val, y_test = (train_test_split(x, y, test_size = .1, random_state = 42))
x_train, x_val, y_train, y_val = (train_test_split(x_train_val, y_train_val, test_size = .111, random_state = 42))

# Checking the shapes of the datasets
m_train = x_train.shape[0]
num_px = x_train.shape[1]
m_val = x_val.shape[0]
m_test = x_test.shape[0]

print ("Number of training samples: " + str(m_train))
print ("Number of validation samples: " + str(m_val))
print ("Number of testing samples: " + str(m_test))
print ("train_images shape: " + str(x_train.shape))
print ("train_labels shape: " + str(y_train.shape))
print ("val_images shape: " + str(x_val.shape))
print ("val_labels shape: " + str(y_val.shape))
print ("test_images shape: " + str(x_test.shape))
print ("test_labels shape: " + str(y_test.shape))

base5 = VGG19(weights='imagenet', include_top=False, input_shape=(128, 128, 3))  

# Freeze convolutional layers
for layer in base5.layers:
    layer.trainable = False  

NN_transfer_5 = Sequential(
                        [InputLayer(input_shape=(128,128,3)),
                         base5,
                         Flatten(),  # should be fine , or add layers
                         Dense(128, activation='relu'),
                         Dense(64, activation='relu'),
                         Dense(32, activation='relu'),   # 2 dense is must bcuz VGG16 model Conv2D twice and Maxpooling -> get a lot more features
                         Dense(1, activation='sigmoid')]
                       )

NN_transfer_5.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
# base5.summary()
NN_transfer_5_model = NN_transfer_5.fit(x_train, y_train, epochs=15, validation_data=(x_val,y_val), verbose=1)

# Evaluate model
plt.plot(NN_transfer_5_model.history['acc'], label='accuracy')
plt.plot(NN_transfer_5_model.history['val_acc'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0.5, 1])
plt.legend(loc='lower right')
plt.show()

val_loss, val_acc = NN_transfer_5.evaluate(x_val,  y_val, verbose=2)

print(val_acc)

# # Test model
# predict = NN_transfer_5.predict(x_test)
# # predict the class label
# y_classes = np.argmax(predict, axis=-1)
# labels = ["Accident","No Accident"]
# # print(labels)
# labels = dict((v,k) for k,v in labels.items())
# predictions = [labels[k] for k in y_classes]

# filenames=x_test.filenames
# results=pd.DataFrame({"Filename":filenames,
#                       "Predictions":predictions})
# results.to_csv("results.csv",index=False)

# # Save model if evaluated good
NN_transfer_5.save("acci_VGG19_model.h5")