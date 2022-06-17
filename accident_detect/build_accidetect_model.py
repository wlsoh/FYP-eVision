# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Building accident detection nn model
# Date Created: 20/06/2022

### !!!! Please use tensorflow 2.3.0 to create this model
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import BatchNormalization, Conv2D, Flatten, Dense, MaxPooling2D
import os
import numpy as np
import matplotlib.pyplot as plt

# Configure batch processing specs
batch_size = 100
img_h = 128
img_w = 128

src_path_train = os.path.abspath('accident_detect/accident_data/train/')
src_path_val = os.path.abspath('accident_detect/accident_data/val/')
src_path_test = os.path.abspath('accident_detect/accident_data/test/')

# Obtain the well-splitted dataset for training and validation, testing
training_ds = tf.keras.preprocessing.image_dataset_from_directory(
    src_path_train,
    seed=42,
    image_size= (img_h, img_w),
    batch_size=batch_size
)

validation_ds =  tf.keras.preprocessing.image_dataset_from_directory(
    src_path_val,
    seed=42,
    image_size= (img_h, img_w),
    batch_size=batch_size
)

testing_ds = tf.keras.preprocessing.image_dataset_from_directory(
    src_path_test,
    seed=42,
    image_size= (img_h, img_w),
    batch_size=batch_size
)

# Set class label
class_names = training_ds.class_names

# Define CNN Model
MyCNN = Sequential([
  BatchNormalization(),
  Conv2D(32, 3, activation='relu'),
  MaxPooling2D(),
  Conv2D(64, 3, activation='relu'),
  MaxPooling2D(),
  Conv2D(128, 3, activation='relu'),
  MaxPooling2D(),
  Flatten(),
  Dense(256, activation='relu'),
    
  Dense(2, activation= 'softmax')#Softmax is often used as the activation for the last layer of a classification network because the result could be interpreted as a probability distribution.
])
#Computes the crossentropy loss between the labels and predictions.

MyCNN.compile(optimizer='adam',loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model = MyCNN.fit(training_ds, validation_data= validation_ds, epochs = 16)

# Evaluate the model
AccuracyVector = []
plt.figure(figsize=(30, 30))
for images, labels in testing_ds.take(1):
    predictions = MyCNN.predict(images)
    predlabel = []
    prdlbl = []
    
    for n in predictions:
        predlabel.append(class_names[np.argmax(n)])
        prdlbl.append(np.argmax(n))
    
    AccuracyVector = np.array(prdlbl) == labels
    for i in range(40):
        ax = plt.subplot(10, 4, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        plt.title('Predict : '+ predlabel[i]+'   Real :'+class_names[labels[i]] )
        plt.axis('off')
        plt.grid(True)
plt.show()

# Save model if evaluated good
MyCNN.save("acci_cnn_model.h5")