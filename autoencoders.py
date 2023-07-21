# -*- coding: utf-8 -*-
"""Autoencoders.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Wt5Kefp9j13f_IwEMaYU06lGuRwegeAN
"""

# Commented out IPython magic to ensure Python compatibility.
from tensorflow.keras.datasets import mnist
import numpy as np
np.set_printoptions(precision = 2)

import matplotlib.pyplot as plt
# %matplotlib inline
(x_train,y_train) , (x_test,y_test) = mnist.load_data()

x_train.shape

x_train[4]

#preprocessing or scaling images pixels

x_train = x_train.astype('float32')/255
x_test = x_test.astype('float32')/255

#DIMENSIONALITY REDUCTION

#first using PCA-Unsupervised technique as baseline to compared with other deep learning models

x_train_flat = x_train.reshape(len(x_train) , np.prod(x_train.shape[1:]))
x_test_flat = x_test.reshape(len(x_test) , np.prod(x_test.shape[1:]))
print(x_train_flat.shape)
print(x_test_flat.shape)

from sklearn.preprocessing import MinMaxScaler
s = MinMaxScaler().fit(x_train_flat)
x_train_scaled = s.transform(x_train_flat)

from sklearn.decomposition import PCA

def mnist_PCA(x_data,n_components):  #to how dimension it has to be reduced
     pca = PCA( n_components = n_components)

     fit_pca = pca.fit(x_data)

     print("Variance employed with {} components .".format(n_components) , round(sum(fit_pca.explained_variance_ratio_) , 2))

     return fit_pca ,  fit_pca.transform(x_data)

pca_full , mnist_pca_full = mnist_PCA(x_train_scaled , 784)

len(pca_full.explained_variance_ratio_)

plt.plot(np.cumsum(pca_full.explained_variance_ratio_))
plt.title("Proportion of PCA variance \n explained by number of components")
plt.xlabel("Number of components")
plt.ylabel("Proportion of variance explained")

pca_2 , mnist_pca2 = mnist_PCA(x_train_scaled , 2)

len(y_train)

num_images_per_class = 250
fig = plt.figure(figsize = (12,12))
for number in list(range(10)):
  mask = y_train == number
  x_data = mnist_pca2[mask , 0][:num_images_per_class]
  y_data = mnist_pca2[mask , 1][:num_images_per_class]
  plt.scatter(x_data, y_data , label = number , alpha = 1)
plt.legend()

pca_64 , mnist_data_64 = mnist_PCA(x_train_scaled , 64)

x_test_scaled = s.transform(x_test_flat)

x_test_flat_64 = pca_64.transform(x_test_scaled)
x_test_reconstructed_64 = pca_64.inverse_transform(x_test_flat_64)

x_test_reconstructed_64.shape

true = x_test_scaled
reconstructed = x_test_reconstructed_64

def mse_reconstruction(true, reconstructed):
  return np.sum(np.power(true - reconstructed , 2)/true.shape[1])

mse_reconstruction(true,reconstructed) #this defines the baseline of performance using 64 components for PCA for further models like autoencoder and their variants

#COMPRESSION OF INPUT'S DIMENSION USING SIMPLE AUTOENCODER
#(using functional API instead of sequential building)

from tensorflow.keras.layers import Input,Dense
from tensorflow.keras.models import Model

ENCODING_DIM = 64 #constructing latent space of 64*64 dimension to measure against prescribed baseline

#Encoder Model
input = Input(shape = (784,))  #introduce a blank tensor
encoded = Dense(ENCODING_DIM , activation = "sigmoid")(input)
encoder_model = Model(input,encoded , name = "encoder")

#Decoder Model
encoded_inputs = Input(shape = (ENCODING_DIM , ) , name = 'encoding')
reconstruction = Dense(784 , activation = 'sigmoid')(encoded_inputs)
decoder_model = Model(encoded_inputs , reconstruction , name = 'decoder')

#Defining full model as the combination of the two

outputs = decoder_model(encoder_model(input))
full_model = Model(input , outputs , name = 'full_ae')

full_model = Model(inputs = input ,
                   outputs = outputs)

full_model.compile(optimizer = 'rmsprop' ,
                   loss = 'binary_crossentropy',
                   metrics = ['accuracy'])

len(x_train_flat)

history = full_model.fit(x_train_flat,x_train_flat ,shuffle = True , epochs = 1 , batch_size =batch_size)

full_model.summary()

encoded_images = encoder_model.predict(x_test_flat)
encoded_images.shape

encoded_images[0]

# GENERATE RECONSTRUCTED IMAGE

deconstructed_images = full_model.predict(x_test_flat)
mse_reconstruction(deconstructed_images , x_test_flat)

# the mse performance is quite worse as compared to baseline so we
# implement more deeper model with large no. of hidden layers with more epochs iterations

ENCODING_DIM = 64
HIDDEN_DIM = 256

#ENCODER MODEL
inputs = Input(shape=(784,))
encoder_hidden = Dense(HIDDEN_DIM , activation = 'relu')(inputs)
encoded = Dense(ENCODING_DIM , activation = "sigmoid")(encoder_hidden)
encoder_model = Model(inputs, encoded , name = 'encoder')

#DECODER MODEL
encoded_inputs = Input(shape = (ENCODING_DIM ,), name = 'encoding')
decoder_hidden = Dense(HIDDEN_DIM , activation = 'relu')(encoded_inputs)
reconstruction = Dense(784, activation = 'sigmoid')(decoder_hidden)
decoder_model = Model(encoded_inputs , reconstruction , name = 'decoder')

#FULL MODEL OF COMBINATION OF THESE TWO MODEL
outputs = decoder_model(encoder_model(inputs))
full_model = Model(inputs , outputs, name = 'full_se')

full_model.summary()

full_model = Model(inputs = inputs,
                   outputs = outputs)

full_model.compile(optimizer = 'rmsprop',
                   loss = 'binary_crossentropy',
                   metrics = ['accuracy'])

history = full_model.fit(x_train_flat, x_train_flat , shuffle = True , epochs = 5, batch_size =32)

# GENERATING RECONSTRUCTED IMAGES

decoded_images = full_model.predict(x_test_flat)
mse_reconstruction(decoded_images , x_test_flat)

#This model gives better performance than earlier model but we can
#further tune this performance by increasing the epochs.

def train_ae_epochs(num_epochs):
  ENCODING_DIM = 64
  HIDDEN_DIM = 256

  #ENCODER MODEL
  inputs = Input(shape=(784,))
  encoder_hidden = Dense(HIDDEN_DIM , activation = 'relu')(inputs)
  encoded = Dense(ENCODING_DIM , activation = "sigmoid")(encoder_hidden)
  encoder_model = Model(inputs, encoded , name = 'encoder')

  #DECODER MODEL
  encoded_inputs = Input(shape = (ENCODING_DIM ,), name = 'encoding')
  decoder_hidden = Dense(HIDDEN_DIM , activation = 'relu')(encoded_inputs)
  reconstruction = Dense(784, activation = 'sigmoid')(decoder_hidden)
  decoder_model = Model(encoded_inputs , reconstruction , name = 'decoder')

  #FULL MODEL OF COMBINATION OF THESE TWO MODEL
  outputs = decoder_model(encoder_model(inputs))
  full_model = Model(inputs , outputs, name = 'full_se')

  full_model = Model(inputs = inputs,
                   outputs = outputs)

  full_model.compile(optimizer = 'rmsprop',
                   loss = 'binary_crossentropy',
                   metrics = ['accuracy'])

  mse_res = []
  for i in range(num_epochs):
    history = full_model.fit(x_train_flat, x_train_flat , shuffle = True , epochs = 5, batch_size =32)

    decoded_images = full_model.predict(x_test_flat)
    reconstruction_loss = mse_reconstruction(decoded_images , x_test_flat)
    mse_res.append(reconstruction_loss)
    print('Reconstruction loss after epoch {0} is {1}'.
          format(i+1 , reconstruction_loss))

    return mse_res

train_ae_epochs(10)

# lets model this with variational autoencoders

from tensorflow.keras.layers import Lambda, Input, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.datasets import mnist
from tensorflow.keras.losses import mse, binary_crossentropy
from tensorflow.keras.utils import plot_model
from tensorflow.keras import backend as K

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

import tensorflow as tf

def sampling(args):

  mu, log_sigma = args
  episilon = K.random_normal(shape = tf.shape(mu)) # creating white noise vector
  sigma = K.exp(log_sigma)
  return mu + sigma*episilon

hidden_dims = 256
batch_size = 128
latent_dim = 2

epochs = 2

#ENCODER LAYER
inputs = Input(shape = (784,), name = "encoder_input")
x = Dense(hidden_dims , activation = 'relu' )(inputs)

z_mean = Dense(latent_dim , name = 'z_mean')(x)
z_log_var = Dense(latent_dim , name = 'z_log_var')(x)

z = Lambda(sampling , name = 'z')([z_mean, z_log_var])
encoder_model = Model(inputs , [z_mean , z_log_var , z] , name = 'encoder')

#DECODER MODEL

latent_inputs = Input(shape = (latent_dim,),)
x = Dense(hidden_dims , activation = 'relu')(latent_inputs)
outputs = Dense(784 , activation = 'sigmoid')(x)
decoder_model = Model(latent_inputs, outputs, name = 'decoder')

#INSTANTIATE VAE MODEL

outputs = decoder_model(encoder_model(inputs)[2]) # here 2 refers to third item 'z' in encoder model which pass tuple of mean and std of ditribution as output
vae_model = Model(inputs , outputs , name = 'vae_mlp')

vae_model.summary()

#ARCHITECTURE STRUCTURE IN DETAIL

for i,layer in enumerate(vae_model.layers):
  print('Layer', i+1)
  print('Name' , layer.name)
  print('Input Shape' , layer.input_shape )
  print('Output Shape' , layer.output_shape )
  if not layer.weights:
    print("No weights for this layer")
    continue
  for i, weight in enumerate(layer.weights):
    print("Weights" , i+1)
    print("Name" , weight.name)
    print("Weight shape" , weight.shape.as_list())

#EVALUATING PERFORMANCE AND METRICS

reconstruction_loss = binary_crossentropy(inputs,outputs)
reconstruction_loss

# using KL Divergence loss

kl_loss = 0.5*(K.exp(z_log_var) - (1+z_log_var) + K.square(z_mean))
kl_loss = K.sum(kl_loss , axis = -1)
total_vae_loss = K.mean(reconstruction_loss + kl_loss)

vae_model.add_loss(total_vae_loss)

vae_model.compile(optimizer = 'rmsprop',
                  metrics = ['accuracy'])

vae_model.summary()

vae_model.fit(x_train_flat,x_train_flat,epochs = epochs ,batch_size = batch_size)

decoded_images = vae_model.predict(x_test_flat)
mse_reconstruction(decoded_images,x_test_flat)

#Though performance is worse but this model is designed to increase
#interpretability of model of latent space and
# not to minimise the reconstruction error.

#plotting the latent space

models = encoder_model , decoder_model
data = x_test_flat , y_test

def plot_results_var(models , data,batch_size = 128,model_name = 'vae_mnist' , lim =4):

  encoder ,decoder = models
  x_test, y_test = data
  os.makedirs(model_name ,exist_ok = True)

  filename = os.path.join(model_name , "vae_mean.png")

  #displaying 2D plot of the digit classes in the latent space
  z_mean , z_log_var , z = encoder.predict(x_test , batch_size = batch_size)

  print(z)
  plt.figure(figsize = (12,10))
  plt.scatter(z[:,0] ,z[:,1] ,c = y_test)
  plt.colourbar()
  plt.xlabel('z[0]')
  plt.ylabel('z[1]')
  plt.savefig(filename)
  plt.show()


  filename = os.path.join(model_name, "digits_over_latent.png")
  # display a 10x10 2D manifold of digits
  n = 10
  digit_size = 28
  figure = np.zeros((digit_size * n, digit_size * n))
  # linearly spaced coordinates corresponding to the 2D plot
  # of digit classes in the latent space
  grid_x = np.linspace(-1.0 * lim, lim, n)
  grid_y = np.linspace(-1.0 * lim, lim, n)[::-1]

  for i, yi in enumerate(grid_y):
      for j, xi in enumerate(grid_x):
          z_sample = np.array([[xi, yi]])
          x_decoded = decoder.predict(z_sample, verbose=0)
          digit = x_decoded[0].reshape(digit_size, digit_size)
          figure[i * digit_size: (i + 1) * digit_size,
                   j * digit_size: (j + 1) * digit_size] = digit

  plt.figure(figsize=(8, 8))
  start_range = digit_size // 2
  end_range = n * digit_size + start_range + 1
  pixel_range = np.arange(start_range, end_range, digit_size+1)
  sample_range_x = np.round(grid_x, 1)
  sample_range_y = np.round(grid_y, 1)
  plt.xticks(pixel_range, sample_range_x)
  plt.yticks(pixel_range, sample_range_y)
  plt.xlabel("z[0]")
  plt.ylabel("z[1]")
  plt.imshow(figure, cmap='Greys_r')
  plt.savefig(filename)
  plt.show()

loss_ae = train_ae_epochs(10)

