import locale
import time
from datetime import date
import os
from datetime import datetime

import pandas as pd
import pymysql

from transformers import MarianMTModel, MarianTokenizer
import langid

### INICIANDO CONEXÃO COM O BANCO DE DADOS
global mydb, cursor
mydb = pymysql.connect(host="localhost", database='scraping2', user="root", passwd="", port = 3307,
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()

# avaliacoes = pd.read_sql_query("SELECT avaliacao_id, nota, titulo, texto FROM avaliacao;", mydb)
cursor.execute("SELECT avaliacao_id, nota, titulo, texto FROM avaliacao WHERE avaliacao_id NOT IN (SELECT avaliacao_id FROM resultadotraducao);")
avaliacoes = pd.DataFrame(cursor.fetchall())

src_reviews = ['>>pt<<' + str(r) for r in avaliacoes['texto'].tolist()]
model_name = 'Helsinki-NLP/opus-mt-en-ROMANCE'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)
tgt_text = []
i = 0
for i, s in enumerate(src_reviews):
    if cursor.execute("SELECT * FROM resultadotraducao WHERE avaliacao_id = '" + str(avaliacoes['avaliacao_id'][i]) + "';"):
        continue

    start = datetime.now()
    ### CHECANDO SE A AVALIAÇÃO JÁ ESTÁ EM PORTUGUES
    if langid.classify(avaliacoes['texto'][i])[0] != 'pt':
        translated = model.generate(**tokenizer.prepare_seq2seq_batch(s, return_tensors='pt'))
        tgt = tokenizer.decode(translated[0], skip_special_tokens=True)
    else: tgt = avaliacoes['texto'][i]

    tgt_text.append(tgt)
    auxSql = [tgt, avaliacoes['avaliacao_id'][i]]
    try:
        cursor.execute("INSERT INTO resultadotraducao (tgt, avaliacao_id) VALUES (%s, %s);", auxSql)
        mydb.commit()
    except pymysql.Error as e:
        print(e)
        mydb.rollback()
    print(str(i) + " " + str(datetime.now() - start))
