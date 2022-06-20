# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Building accident detection nn model
# Date Created: 20/06/2022

import tensorflow as tf
from keras.models import Sequential
from keras.layers import BatchNormalization, Conv2D, Flatten, Dense, MaxPooling2D, InputLayer
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split

# Read all accident images in training set
list_images_accident = []
name_accident= []
for dirname, _, filenames in os.walk('accident_detect/new_dataset/Accident/'):
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
for dirname_2, _, filenames_2 in os.walk('accident_detect/new_dataset/Non Accident/'):
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
    img = tf.keras.preprocessing.image.load_img(img_path) #, target_size=(128,128)
    x = tf.keras.preprocessing.image.img_to_array(img)
    
    return x

images = []
labels = []

directory = os.fsencode('accident_detect/new_dataset/')

for folder in os.listdir(directory):
    label = os.fsdecode(folder)
    for img in os.listdir(f'accident_detect/new_dataset/{label}'):
        img_name = os.fsdecode(img)
        images.append(prepare_image(f'accident_detect/new_dataset/{label}/{img_name}'))
        labels.append(label)
        
label_0_1 = [int(labels[w].replace('Non Accident', "0").replace("Accident",'1')) for w in range(len(labels))]

X, Y = images, label_0_1

# Convert to numpy array
X = np.array(X)
Y = np.array(Y)

open_file = open("img_28x28.txt", "wb")
pickle.dump(X, open_file)
open_file.close()

open_file = open("label_28x28.txt", "wb")
pickle.dump(Y, open_file)
open_file.close()

with open("img_28x28.txt", "rb") as fp: 
    x = pickle.load(fp)
    
with open("label_28x28.txt", "rb") as fp: 
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

# base5 = VGG19(weights='imagenet', include_top=False, input_shape=(28, 28, 3))  

# # Freeze convolutional layers
# for layer in base5.layers:
#     layer.trainable = False  

# NN_transfer_5 = Sequential(
#                         [InputLayer(input_shape=(28,28,3)),
#                          base5,
#                          Flatten(),  # should be fine , or add layers
#                          Dense(128, activation='relu'),
#                          Dense(64, activation='relu'),
#                          Dense(32, activation='relu'),   # 2 dense is must bcuz VGG16 model Conv2D twice and Maxpooling -> get a lot more features
#                          Dense(1, activation='sigmoid')]
#                        )

MY_CNN = Sequential([
  Conv2D(16, 3, activation='relu', padding='same', input_shape=(28,28,3)),
  BatchNormalization(),
  MaxPooling2D(pool_size=(2,2), strides=(2,2)),
  Conv2D(32, 3, activation='relu', padding='same'),
  BatchNormalization(),
  MaxPooling2D(pool_size=(2,2), strides=(2,2)),
  Conv2D(64, 3, activation='relu', padding='same'),
  BatchNormalization(),
  MaxPooling2D(pool_size=(2,2), strides=(2,2)),
  Conv2D(128, 3, activation='relu', padding='same'),
  BatchNormalization(),
  MaxPooling2D(pool_size=(2,2), strides=(2,2)),
  Flatten(),
  Dense(64, activation='relu'),
    
  Dense(2, activation= 'softmax')
])

MY_CNN.compile(loss='sparse_categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
print(MY_CNN.summary())
cnn_model = MY_CNN.fit(x_train, y_train, epochs=10, validation_data=(x_val,y_val), verbose=1)

# Evaluate model
plt.plot(cnn_model.history['acc'], label='accuracy')
plt.plot(cnn_model.history['val_acc'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title("Model Accuracy")
plt.ylim([0.5, 1])
plt.legend(loc='lower right')
plt.show()

val_loss, val_acc = MY_CNN.evaluate(x_val,  y_val, verbose=2)

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
MY_CNN.save("new_acci_cnn_model.h5")