import numpy as np
import pandas as pd
import os
import json
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import tensorflow
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Embedding, LSTM, LayerNormalization, Dense, Dropout
import re
import random

with open('CSV/tagged_dataset.csv', 'r') as f:
    data = csv.load(f)

df = pd.DataFrame(data['intents'])
pd.options.display.max_colwidth=None
dic = {"tag":[], "patterns":[], "responses":[]}
for example in data['intents']:
    for pattern in example['patterns']:
        dic['patterns'].append(pattern)
        dic['tag'].append(example['tag'])
        dic['responses'].append(example['responses'])

tokenizer = Tokenizer(lower=True, split=' ')
#  lists to be a token 
tokenizer.fit_on_texts(df['patterns'])
# serialized JSON dictionary
tokenizer.get_config()
vacab_size = len(tokenizer.word_index)
vacab_size = 1000

ptrn2seq = tokenizer.texts_to_sequences(df['patterns'])
X = pad_sequences(ptrn2seq, padding='post')
lbl_enc = LabelEncoder()
y = lbl_enc.fit_transform(df['tag'])

model = Sequential()
model.add(Input(shape=(X.shape[1])))
model.add(Embedding(input_dim=vacab_size+1, output_dim=100))
model.add(LSTM(32, return_sequences=True))
model.add(LayerNormalization())
model.add(LSTM(32, return_sequences=True))
model.add(LayerNormalization())
model.add(LSTM(32))
model.add(LayerNormalization())
model.add(Dense(128, activation="relu"))
model.add(LayerNormalization())
model.add(Dropout(0.2))
model.add(Dense(len(np.unique(y)), activation="softmax"))
model.compile(optimizer='adam', loss="sparse_categorical_crossentropy", metrics=['accuracy'])

model.summary()

model_history = model.fit(x=X,
                          y=y,
                          batch_size=10,
                          callbacks=[tensorflow.keras.callbacks.EarlyStopping(monitor='accuracy', patience=3)],
                          epochs=100)

def generate_answer(pattern): 
    while True:
        text = []
        txt = re.sub('[^a-zA-Z\']', ' ', pattern)
        txt = txt.lower()
        txt = txt.split()
        txt = " ".join(txt)
        text.append(txt)

        x_test = tokenizer.texts_to_sequences(text)
        x_test = np.array(x_test).squeeze()
        x_test = pad_sequences([x_test], padding='post', maxlen=X.shape[1])
        y_pred = model.predict(x_test)
        y_pred = y_pred.argmax()
        tag = lbl_enc.inverse_transform([y_pred])[0]
        responses = df[df['tag'] == tag]['responses'].values[0]
        print("model: {}".format(random.choice(responses)))
        if pattern=='quite':
            break
    return responses