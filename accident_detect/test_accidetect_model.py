import os
import tensorflow as tf
import numpy as np
from keras.models import load_model
from PIL import Image

model_path = os.path.abspath('accident_detect/new_acci_cnn_model.h5')
acci_model = load_model(model_path)
class_name = ['Non Accident', 'Accident']

img = Image.open("accident_detect/test/t1.jpg")
img = img.resize((28,28), Image.ANTIALIAS)
# img = tf.keras.preprocessing.image.load_img(f"accident_detect/test/non.jpg", target_size=(28,28)) # should use pil to read image

Z = tf.keras.preprocessing.image.img_to_array(img)
Z = np.expand_dims(Z,axis=0)
images = np.vstack([Z])
val = acci_model.predict([images])
ind = max(val).argmax()
print(class_name[ind])