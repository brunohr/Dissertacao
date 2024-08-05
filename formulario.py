#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 14:36:30 2024

@author: cachaco
"""

import pandas as pd
import string
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

import os
os.chdir("/home/cachaco/Documentos/scraping")


df = pd.read_excel("Formulário (respostas).xlsx")
print(df.head())
df.columns



df2 = df.loc[(df['31. Primeira palavra, sentimento e/ou impressão'].str.translate(str.maketrans('', '', string.punctuation)).str.len() > 1) &
    (df['32. Segunda palavra, sentimento e/ou impressão'].str.translate(str.maketrans('', '', string.punctuation)).str.len() > 1) &
    (df['33. Terceira palavra, sentimento e/ou impressão'].str.translate(str.maketrans('', '', string.punctuation)).str.len() > 1) &
    (df['34. Quarta palavra, sentimento e/ou impressão'].str.translate(str.maketrans('', '', string.punctuation)).str.len() > 1)]

wc = WordCloud().generate(' '.join(df2['31. Primeira palavra, sentimento e/ou impressão']))
plt.imshow(wc)
plt.axis("off")
plt.show()


aux = []
aux.append(df2['31. Primeira palavra, sentimento e/ou impressão'].str)
aux.append(df2['32. Segunda palavra, sentimento e/ou impressão'].str)
aux.append(df2['33. Terceira palavra, sentimento e/ou impressão'].str)
aux.append(df2['34. Quarta palavra, sentimento e/ou impressão'].str)

wc = WordCloud().generate(str(aux))
plt.imshow(wc)
plt.axis("off")
plt.show()
