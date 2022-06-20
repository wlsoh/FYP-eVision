import os
import tensorflow as tf
import numpy as np
from keras.models import load_model

model_path = os.path.abspath('accident_detect/new_acci_cnn_model.h5')
acci_model = load_model(model_path)
class_name = ['Non Accident', 'Accident']

img = tf.keras.preprocessing.image.load_img(f"accident_detect/test/non4.jpg")

Z = tf.keras.preprocessing.image.img_to_array(img)
Z = np.expand_dims(Z,axis=0)
images = np.vstack([Z])
val = acci_model.predict([images])
ind = max(val).argmax()
print(class_name[ind])