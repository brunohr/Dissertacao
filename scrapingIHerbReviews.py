import locale
import time
from datetime import date, datetime
import random

import pandas as pd
import pymysql
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains


##### MANIPULAÇÃO DE ARQUIVOS E LINKS
import os
import urllib.request
from urllib.error import HTTPError
import requests
import json

import re

# from fake_useragent import UserAgent
# ua = UserAgent()
# print(user_agent)

# ##### PARA TRADUÇÃO DAS AVALIAÇÕES
# from transformers import MarianMTModel, MarianTokenizer
# import langid
#
# model_name = 'Helsinki-NLP/opus-mt-en-ROMANCE'
# tokenizer = MarianTokenizer.from_pretrained(model_name)
# model = MarianMTModel.from_pretrained(model_name)

# locale.setlocale(locale.LC_ALL, 'pt_BR')

# Define the proxy server
# global PROXY
# PROXY = "50.207.199.80:80"

# Set ChromeOptions()
global options
# options = webdriver.FirefoxOptions()
# options.set_preference("dom.webdriver.enabled", False)
# options.set_preference('useAutomationExtension', False)
# options.set_preference("general.useragent.override",
#                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

options = Options()
options.set_preference("network.cors.enabled", False)  # Desativa temporariamente a política de CORS
options.set_preference("security.fileuri.strict_origin_policy", False)  # Evita bloqueio de origem
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)



# Add the proxy as argument
# options.add_argument("--proxy-server=%s" % PROXY)


# INICIANDO CONEXÃO COM O BANCO DE DADOS
global mydb, cursor
mydb = pymysql.connect(host="localhost", database='scraping2', user="root", passwd="", port=3307,
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()

global aux_site, palavra_chave
palavra_chave = 'buttermilk'
dominio = '.com'
cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(palavra_chave) + "';")
aux_site = cursor.fetchone()["site_id"]

# cursor.execute('select * from teste.tbl_produtos')
# res = cursor.fetchall()
# for i in res:
#     print(f"Nome: {i['nome']}")
# comando = f"insert into teste.teste values ('nome3')"
# cursor.execute(comando)
# mydb.commit() # só quando for alteração
# cursor.execute("select * from teste.teste")
# for x in cursor: print(x)
# cursor.close()
# mydb.close() #close the connection


# PARA CONSEGUIR PEGAR AS IMAGENS DE PERFIL, O IHERB PARECE ESTAR BARRANDO O URLLIB
global opener
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'MyApp/1.0')]
urllib.request.install_opener(opener)

# Dicionário para traduzir os meses do português para o inglês
meses_portugues_para_ingles = {
    "janeiro": "January", "fevereiro": "February", "março": "March", "abril": "April",
    "maio": "May", "junho": "June", "julho": "July", "agosto": "August",
    "setembro": "September", "outubro": "October", "novembro": "November", "dezembro": "December",

    "jan": "January", "fev": "February", "mar": "March", "abr": "April",
    "mai": "May", "jun": "June", "jul": "July", "ago": "August",
    "set": "September", "out": "October", "nov": "November", "dez": "December",
}

def traduzir_data(data_str):
    # Substitui os meses em português pelos equivalentes em inglês de forma insensível a maiúsculas e minúsculas
    for mes_pt, mes_en in meses_portugues_para_ingles.items():
        data_str = re.sub(mes_pt, mes_en, data_str, flags=re.IGNORECASE)
    return data_str

def converter_data(data_str):
    # Verifica se a data está no formato "dia de mês de ano"
    if re.match(r"\d{1,2} de [a-zA-Z]+ de \d{4}", data_str):
        # Traduz a data do português para o inglês
        data_str_traduzida = traduzir_data(data_str)
        # Tenta converter a string de data para datetime usando o formato específico
        try:
            data = datetime.strptime(data_str_traduzida, "%d de %B de %Y")
            return data.strftime('%Y-%m-%d')
        except ValueError:
            return "Data inválida"

    # Para outros formatos, tenta os formatos conhecidos
    formatos = [
        "%d %B %Y",  # Ex: 25 December 2023
        "%d %b %Y",  # Ex: 25 Dec 2023
        "%B %d, %Y",  # Ex: December 25, 2023
        "%b %d, %Y",  # Ex: Dec 25, 2023
        "%d/%m/%Y",  # Ex: 25/12/2023
        "%m/%d/%Y",  # Ex: 12/25/2023
    ]

    for formato in formatos:
        try:
            data = datetime.strptime(data_str, formato)
            return data.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return "Data inválida"


# for i in range(len(data)):
#     try:
#         data.loc[i, 'data'] = converter_data(data['dataavaliacao'][i].split(' on ')[1])
#     except IndexError:
#         data.loc[i, 'data'] = converter_data(data['dataavaliacao'][i].split(' em ')[1])

# def traduzReview(avaliacao):
#     src_reviews = ['>>pt<<' + str(r) for r in avaliacao['texto'].tolist()]
#     tgt_text = []
#     i = 0
#     for i, s in enumerate(src_reviews):
#         if cursor.execute(
#                 "SELECT * FROM resultadotraducao WHERE avaliacao_id = '" + str(avaliacao['avaliacao_id'][i]) + "';"):
#             continue
#
#         start = datetime.now()
#         ### CHECANDO SE A AVALIAÇÃO JÁ ESTÁ EM PORTUGUES
#         if langid.classify(avaliacao['texto'][i])[0] != 'pt':
#             translated = model.generate(**tokenizer.prepare_seq2seq_batch(s, return_tensors='pt'))
#             tgt = tokenizer.decode(translated[0], skip_special_tokens=True)
#         else:
#             tgt = avaliacao['texto'][i]
#
#         tgt_text.append(tgt)
#         auxSql = [tgt, avaliacao['avaliacao_id'][i]]
#         try:
#             cursor.execute("INSERT INTO resultadotraducao (tgt, avaliacao_id) VALUES (%s, %s);", auxSql)
#             mydb.commit()
#         except pymysql.Error as e:
#             print(e)
#             mydb.rollback()
#         print(str(i) + " " + str(datetime.now() - start))
#
#     cursor.execute(
#         "SELECT t.*, a.nota FROM `resultadotraducao` as t left join avaliacao as a on t.avaliacao_id = a.avaliacao_id;")
#     # traducao = pd.DataFrame(cursor.fetchall())


def coletaReviewNew(link_review, dominio):
    # options.headless = True
    # driver2 = webdriver.Firefox(options=options)

    # user_agent = ua.random
    # options.add_argument(f'--user-agent={user_agent}')

    driver2 = webdriver.Firefox(options = options)
    driver2.get(
        link_review + "?sort=2")  ####ORDENANDO POR MAIS RECENTE, PRA PODER ENCERRAR ASSIM QUE APARECER O PRIMEIRO COMENTÁRIO JÁ SALVO NO BANCO

    try:
        link_produto = WebDriverWait(driver2, 3).until(
            EC.presence_of_element_located((By.XPATH,
                                            ".//div/a[@class='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-1o1ny0d']"))).get_attribute(
            "href")
        codigo = re.split('/', link_produto)[-1]

        # time.sleep(3)

        try:
            js_string = "var element = document.getElementById('px-captcha-wrapper');element.remove();"
            driver2.execute_script(js_string)
        except:
            # print('erro 2')
            pass

        auxAnalises = int(
            driver2.find_element(By.XPATH, ".//h6[@data-testid='global-reviews']").text.split("(")[1].split(")")[
                0].replace(',', '').replace('.', ''))
        ##### PEGANDO A QTDE DE AVALIAÇÕES DESSE PRODUTO QUE JÁ ESTÃO NO SQL, PRA COMPARAR COM QUANTAS EXISTEM NA PÁGINA
        analisesSql = cursor.execute(
            "SELECT * FROM avaliacao WHERE produto_id = (SELECT produto_id FROM produto WHERE codigo = '" + str(
                codigo) + "' LIMIT 1);")

        ##### VERIFICAÇÃO PRA VER SE O PRODUTO TÁ LISTADO CONTENDO LEITELHO
        cursor.execute("SELECT produto_id FROM produto WHERE codigo = '" + str(
            codigo) + "' AND leitelho = 1 LIMIT 1 ;")
        flag = cursor.fetchall()
        if auxAnalises > analisesSql:

            # INICIANDO LISTA PARA ARMAZENAR
            product_review = []

            # PEGANDO CADA CARD DE AVALIAÇÃO
            # while (len(product_review) < 200):
            while flag:
                # if len(product_review) >= auxAnalises: ### só por precaução
                #     # print("ok")
                #     break
                # TENTANDO CONTORNAR StaleElementReferenceException
                try:
                    WebDriverWait(driver2, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//nav[@aria-label='pagination navigation']")))
                except:
                    print('erro 3')
                    break

                try:
                    js_string = "var element = document.getElementById('px-captcha-wrapper');element.remove();"
                    driver2.execute_script(js_string)
                except:
                    # print('erro 4')
                    pass

                # auxPosicao = WebDriverWait(driver2, 10).until(
                #     EC.presence_of_element_located((By.XPATH, ".//nav[@aria-label='pagination navigation']")))
                # driver2.execute_script("arguments[0].scrollIntoView();", auxPosicao)

                #
                # # PEGANDO CADA CARD DE AVALIAÇÃO

                # if not review_elements:
                #     break

                # while len(review_elements):

                i, j = 0, 0

                time.sleep(2)


                try:
                    # pag = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="MuiBox-root css-i9gxme"]')))
                    review_elements = WebDriverWait(driver2, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, './/div[@class="MuiBox-root css-1v71s4n"]')))
                except:
                    print('erro 5')
                    break

                while i < len(review_elements):

                    try:
                        pag = WebDriverWait(driver2, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, './/div[@class="MuiBox-root css-1v71s4n"]')))
                        review_element = pag[i]

                        # EXTRAINDO LINK DA POSTAGEM
                        review_link = review_element.find_element(By.XPATH,
                                                                  './/div[@class="MuiBox-root css-1hzdy1p"]/a[@class="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone css-bvdvm5"]').get_attribute(
                            "href")
                        review_id = review_link.split("/")[-2]

                        #### VERIFICA SE O COMENTÁRIO JÁ EXISTE.
                        #### COMO TÁ PEGANDO EM ORDEM, A FUNCÇÃO VAI SER INTERROMPIDA
                        if cursor.execute(
                                "SELECT * FROM avaliacao WHERE codigo_avaliacao = '" + str(review_id) + "';") > 0:
                            # #### SE SIM, VAI PRO PRÓXIMO
                            # i += 1
                            # continue
                            flag = False
                            break

                        # EXTRAIR NOME AUTOR/USUÁRIO
                        author_name = review_element.find_element(By.XPATH,
                                                                  './/div/a[@class="MuiTypography-root MuiTypography-body1 css-ehmaku"]').text.strip()

                        #### EXTRAIR TÍTULO AVALIAÇÃO
                        review_title = review_element.find_element(By.XPATH,
                                                                   './/span[@class="MuiTypography-root MuiTypography-body1 css-1i1gvtz"]').text.strip()

                        #### EXTRAINDO TEXTO AVALIAÇÃO
                        review_text = review_element.find_element(By.XPATH,
                                                                  './/div[@data-testid="review-text"]').text.strip()

                        #### EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
                        # review_star = float(
                        #     review_element.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent").split()[0].replace(
                        #         ',', '.'))

                        # EXTRAINDO DATA AVALIAÇÃO
                        # review_date = ' '.join(review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[-5:])
                        # review_date = datetime.strptime(review_date, "%d de %B de %Y").strftime("%Y/%m/%d")
                        review_date0 = review_element.find_element(By.XPATH,
                                                                   './/span[@data-testid="review-posted-date"]').text.strip()
                        try:
                            review_date = converter_data(review_date0.split(' on ')[1])
                        except IndexError:
                            try:
                                review_date = converter_data(review_date0.split(' em ')[1])
                            except:
                                review_date = review_date0

                        #### EXTRAINDO PAÍS AVALIAÇÃO
                        review_country = review_element.find_element(By.XPATH, './/span[@class="MuiTypography-root MuiTypography-body2 css-8uaw3d"]').text.strip()

                        #### EXTRAINDO LINK E IMAGEM DO PERFIL PARA COLETA SEGUINTE
                        profile_link = review_element.find_element(By.XPATH,
                                                                   './/div[@class="MuiBox-root css-1i27l4i"]/a[@class="MuiTypography-root MuiTypography-body1 css-ehmaku"]').get_attribute(
                            "href")
                        profile_id = profile_link.split('/')[-1]

                        try:
                            review_element.find_element(By.XPATH, ".//div/*[@data-testid='PersonIcon']")
                            profile_img = ""
                            author_img = ""
                        except NoSuchElementException:
                            # SALVANDO A IMG PRA NÃO DEPENDER DE INTERNET PRO PROCESSAMENTO DA MESMA
                            profile_img = review_element.find_element(By.XPATH,
                                                                      ".//div/img[@class='MuiAvatar-img css-1hy9t21']").get_attribute(
                                "src")
                            author_img = profile_img.replace("/s.", "/l.")
                            # urllib.request.urlretrieve(author_img,
                            #                            "results/profile_img/iherb" + dominio + "_" + profile_id + ".jpeg")

                            # profiles = pd.concat([profiles, coletaPerfil(profile_link, review_country)], ignore_index=True)
                        except NoSuchElementException:
                            profile_link, profile_id, author_img = "", "", ""

                        try:
                            review_img = review_element.find_element(By.XPATH,
                                                                     './/div/img[@class="css-1u8hqvf"]').get_attribute(
                                "src")
                        except NoSuchElementException:
                            review_img = ""

                        review_star = len(review_element.find_elements(By.XPATH, ".//*[@fill='#FAC627']"))

                        # if profile_link:
                        #     coletaPerfil(profile_link, review_country)

                        product_review.append(
                            (dominio, review_link, review_title, review_text, review_star, review_img, author_name,
                             author_img, review_date, review_country,
                             link_review, profile_link, profile_id, link_produto, codigo, review_id))

                        # ### CHECANDO SE A AVALIAÇÃO JÁ ESTÁ EM PORTUGUES
                        # if langid.classify(review_text)[0] != 'pt':
                        #     traduzReview(pd.DataFrame(product_review[-1]))

                        i += 1
                    except StaleElementReferenceException:
                        j += 1
                        print(str(len(product_review) - 1) + " " + str(j))
                    except IndexError:
                        pag
                        print(i)

                # try:
                #     driver2.find_element(By.XPATH, ".//button[@aria-label='Go to next page' and disabled='']")
                # except NoSuchElementException:
                #     pass

                try:
                    time.sleep(1)
                    # driver2.find_element(By.XPATH, ".//button[@aria-label='Go to next page']").click()
                    # js_string = "var element = document.getElementByClass('px-captcha-wrapper');element.remove();"
                    js_string = driver2.find_element(By.XPATH, ".//button[@aria-label='Go to next page']")
                    driver2.execute_script('arguments[0].click()', js_string)
                    driver2.execute_script("window.scrollTo(0, 0)")
                except:
                    print('erro 6')
                    break

                # try:
                #     WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, ".//div[@id='cm_cr-pagination_bar']/ul/li[@class='a-last']"))).click()
                # except:
                #     break
        # else:
        #     print(auxAnalises, analisesSql)

    # review = pd.DataFrame()
    # for link in review_links:
    #     review = pd.concat([review, coletaReview(link, dominio)], ignore_index=True)

    # return review  # , profiles

    except NoSuchElementException:
        # print("erro 1")
        pass

    driver2.close()

    print(link_review, str(len(product_review)) + "+" + str(analisesSql) + " / " + str(auxAnalises))
    return pd.DataFrame(data=product_review,
                        columns=["dominio", "review_link", "review_title", "review_text", "review_star", "review_img",
                                 "author_name",
                                 "author_img", "review_date", "review_country",
                                 "link_reviews", "profile_link", "profile_id", "link_produto", "codigo_produto",
                                 "codigo_avaliacao"]).fillna("")


def coletaDetalhes(link, dominio, review=False):
    driver2 = webdriver.Firefox(options=options)
    # driver = webdriver.Edge()
    driver2.get(link)

    try:
        pag = WebDriverWait(driver2, 3).until(
            EC.presence_of_element_located((By.XPATH, './/div[@class="product-grouping-wrapper defer-block"]')))
        # try:
        #     driver.find_element(By.ID, "sp-cc-all-link").click()
        # except NoSuchElementException:
        #     pass
    except:
        driver2.close()
        return pd.DataFrame()

    nome = pag.find_element(By.ID, 'name').get_attribute("textContent").strip()
    marca = pag.find_element(By.XPATH, './/div/div/a[@class="last"][1]').text.strip()
    tag = pag.find_elements(By.XPATH, './/div[@id="breadCrumbs"]/a')[-1].text.strip()

    try:
        js_string = "var element = document.getElementById('px-captcha-wrapper');element.remove();"
        driver2.execute_script(js_string)
        js_string = "var element = document.getElementById('px-captcha-modal');element.remove();"
        driver2.execute_script(js_string)
        js_string = "var element = document.getElementByClass('modal-wrap');element.remove();"
        driver2.execute_script(js_string)
    except:
        pass

    # DESMEMBRANDO PREÇO (INCLUIR MOEDA TBM?)
    # try:
    #     moeda = pag.find_element('xpath', './/span[@class="a-price-symbol"]').text.strip()
    #     whole_price = pag.find_element('xpath', './/span[@class="a-price-whole"]').text.strip()
    #     fraction_price = pag.find_element('xpath', './/span[@class="a-price-fraction"]').text.strip()
    #     price = float(('.'.join([whole_price, fraction_price])))
    # except NoSuchElementException:
    #     moeda, price = None, None
    moeda, price = "", ""

    descricao, uso, ingredientes, advertencia, aviso = "", "", "", "", ""

    aux = pag.find_elements(By.XPATH,
                            './/div[@class="row"]/div[contains(@class, "col-xs-24")]/div[@class="row item-row"]')

    tabela = pag.find_element(By.XPATH, ".//div[@class='item-row']/div[@class='row']").get_attribute("textContent")
    ### tentando separar essa tabela
    for bloco in aux:
        if "Descr" in bloco.get_attribute("innerText"):  ### descrição / description
            descricao = bloco.get_attribute("innerText")
        elif "Suge" in bloco.get_attribute("innerText"):  ### uso sugerido / sugested
            uso = bloco.get_attribute("innerText")
        elif "Ingred" in bloco.get_attribute("innerText"):  ### ingredientes / ingredients
            ingredientes = bloco.get_attribute("innerText")
        elif "Advert" in bloco.get_attribute("innerText") or "Warning" in bloco.get_attribute(
                "innerText"):  ### advertencia / warning
            advertencia = bloco.get_attribute("innerText")
        elif "Legal" in bloco.get_attribute("innerText"):  ### Uso legal / Legal use
            aviso = bloco.get_attribute("innerText")
    ######## SEGUINDO A ORDEM codcoletaproduto_id
    obs = 1 if re.search("leitelho|buttermilk", tabela, re.IGNORECASE) else (2 if re.search("soro de leitelho coalhado", tabela, re.IGNORECASE) else 3)

    driver2.close()

    # try:
    #     if not review:
    #         sql = 'insert into teste.tbl_detalhes (site, codigo, nome, marca, moeda, price, tag, overview, features, details, description, information, documents) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #         cursor.execute(sql, (site, codigo, nome, marca, moeda, price, tag, overview, features, details, description, information, documents))
    #     else:
    #         sql = 'insert into teste.tbl_detalhes_review (site, codigo, nome, marca, price, tag, overview, features, details, description, information, documents, review) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #         cursor.execute(sql, (site, codigo, nome, marca, moeda, price, tag, overview, features, details, description, information, documents, review))
    #     print(f"Detalhes do produto {codigo} inseridos")
    #     mydb.commit()
    # except pymysql.Error as e:
    #     mydb.rollback()
    #     print(e)

    return pd.DataFrame(
        data=[[dominio, nome, marca, tag, moeda, price, descricao, uso, ingredientes, advertencia, aviso, tabela, obs]],
        columns=['dominio', 'nome', 'marca', 'tag', 'moeda', 'price', 'descricao', 'uso', 'ingredientes', 'advertencia',
                 'aviso', 'tabela', 'obs']).fillna("")


#
# def coletaPerfil(link_perfil, dominio, coletaProdutos=False):
#     # driver = webdriver.Firefox(options=options)
#     driver = webdriver.Edge()
#     driver.get(link_perfil)
#
#     try:
#         driver.find_element(By.ID, "sp-cc-rejectall-link").click()
#     except NoSuchElementException:
#         pass
#
#     try:
#         pag = WebDriverWait(driver, 3).until(
#             EC.visibility_of_element_located((By.CLASS_NAME, "MuiBox-root css-134cxvg")))
#     except:
#         driver.close()
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
#
#     compras = pd.DataFrame()
#     lista_reviews = pd.DataFrame()
#     id_perfil = link_perfil.split('/me/.')[-1]
#
#     nome = pag.find_element(By.XPATH, ".//h5[@data-testid='me-profile-name']").text.strip()
#     img = pag.find_element(By.XPATH,
#                            ".//div[@class='MuiAvatar-root MuiAvatar-circular css-19hztas']/img").get_attribute("src")
#
#     try:
#         bio = pag.find_element(By.XPATH, ".//div[@class='a-section pw-bio']").text.strip()
#     except NoSuchElementException:
#         bio = None
#
#     # sql = "insert into profile values (%s, %s, %s, %s)"
#     # cursor.execute(sql, (link, nome, img, profile_country))
#     if coletaProdutos:
#         while True:
#             pagreviews = pag.find_element(By.XPATH, './/div[@data-testid="me-page-reviews"]')
#             reviews = pagreviews.find_elements(By.XPATH, './/div[@data-testid="me-my-reviews"]')
#             for review in reviews:
#                 link_review = review.find_element(By.XPATH, ".//div[@class='MuiBox-root css-1yx24u3']/a").get_attribute(
#                     "href")
#                 auxReview = coletaReview(link_review, dominio)
#                 lista_reviews = pd.concat([lista_reviews, auxReview], ignore_index=True)
#
#                 # driver2 = webdriver.Firefox(options = options)
#                 # driver2.get(link_review)
#                 # link_produto = driver2.find_element(By.CSS_SELECTOR, "a[data-hook='product-link']").get_attribute("href")
#                 # codigo = re.split('/dp/|/ref', link_produto)[1]
#                 # driver2.close()
#                 compras = pd.concat([compras, coletaDetalhes(auxReview.link_produto[0], dominio, link_perfil)],
#                                     ignore_index=True)
#             try:
#                 pagreviews.find_element(By.XPATH, ".//svg[@data-testid='NavigateNextIcon']").click()
#             except NoSuchElementException:
#                 break
#
#     profile = pd.DataFrame(data=[[nome, img, bio, link_perfil, id_perfil]],
#                            columns=['nome', 'img', 'bio', 'link', 'id_profile']).fillna("")
#     return profile, lista_reviews, compras
#

def coletaElemento(palavra_chave, dominio):
    today = date.today().strftime("%Y%m%d")
    cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(palavra_chave) + "';")
    aux_site = cursor.fetchone()["site_id"]
    # options.set_preference("network.cookie.cookieBehavior", 2)

    # INICIANDO DATAFRAMES
    product = pd.DataFrame()
    product_descr = pd.DataFrame()
    profiles = pd.DataFrame()
    avaliacoes = pd.DataFrame()

    # INICIALIZE O DRIVER DO SELENIUM
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Edge()
    driver.get("https://iherb.com/search/?kw=" + palavra_chave)

    while True:
        time.sleep(2)
        # CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
        items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, './/div[@class="product-cell-container col-xs-12 col-sm-12 col-md-8 col-lg-6"]')))

        start = time.time()
        while len(items):

            item = items.pop(0)

            name = item.find_element(By.CLASS_NAME, 'product-title').text.strip()

            codigo = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
                "data-product-id")

            # DESMEMBRANDO PREÇO (INCLUIR MOEDA TBM?)
            moeda = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
                "data-ga-discount-price")
            # whole_price = item.find_elements('xpath', './/span[@class="a-price-whole"]')
            # fraction_price = item.find_elements('xpath', './/span[@class="a-price-fraction"]')
            # if whole_price and fraction_price:
            #     price = float('.'.join([whole_price[0].text.replace('.', '').replace(',', ''), fraction_price[0].text]))
            # else:
            #     price = 0.0
            price = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
                "data-ga-discount-price")

            try:
                ratings = float(
                    item.find_element(By.XPATH, ".//div/a[@class='rating-count scroll-to']").get_attribute(
                        "title").split(
                        "/")[0])
                ratings_num = int(
                    item.find_element(By.XPATH, ".//div/a[@class='rating-count scroll-to']").get_attribute(
                        "title").split(
                        " ")[-2].replace(',', '').replace('.', ''))
            except NoSuchElementException:
                ratings = 0.0
                ratings_num = 0

            # LINK DE CADA PRODUTO
            link = item.find_element('xpath', './/div/a[@class="absolute-link product-link"]').get_attribute("href")

            #### LINK DA IMAGEM -> DEPOIS BAIXAR O ARQUIVO
            img = item.find_element('xpath', ".//div[@class='product-image-wrapper']/span/img").get_attribute("src")
            #### SALVANDO NO DATAFRAME
            product = pd.concat(
                [product,
                 pd.DataFrame(data=[[dominio, codigo, name, moeda, price, ratings, ratings_num, img, link]],
                              columns=['dominio', 'codigo', 'name', 'moeda', 'price', 'ratings', 'ratings_num',
                                       'img', 'link'])],
                ignore_index=True).fillna("")

            auxDetalhes = pd.DataFrame()
            observacao = 4
            if not cursor.execute(
                    "SELECT iherb_id FROM iherb WHERE produto_id IN (SELECT produto_id FROM produto WHERE codigo = '" + str(
                        codigo) + "');"):
                try:
                    aux_tempo = random.randint(1, 30) + 0 if (end - start) >= 120 else 120 - (end - start)
                    print("Aguardando " + str(int(aux_tempo)) + "s para coletaDetalhes(" + str(codigo) + ")")
                    time.sleep(aux_tempo)
                    auxDetalhes = coletaDetalhes(link, dominio)
                    if not auxDetalhes.empty:
                        auxDetalhes.fillna("", inplace=True)
                        product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
                        print(link + " Descr ok")
                        try:
                            auxSql = auxDetalhes.loc[:,
                                     ['tag', 'marca', 'descricao', 'uso', 'ingredientes', 'advertencia',
                                      'aviso', 'tabela', 'obs']].values.flatten().tolist()
                            auxSql.extend([aux_produto])
                            cursor.execute(
                                "INSERT INTO iherb (tag, marca, descricao, uso, ingredientes, advertencias, aviso, tabela, produto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                auxSql)
                            mydb.commit()

                            # if cursor.execute("SELECT produto_id FROM iherb WHERE produto_id = '" + str(
                            #         aux_produto) + "' AND tabela NOT REGEXP 'leitelho|buttermilk';"):
                            #     try:
                            #         cursor.execute(
                            #             "UPDATE produto SET observacao = CONCAT_WS('\n', observacao, '- NÃO CONTÉM PALAVRA LEITELHO OU BUTTERMILK NA DESCRIÇÃO'), leitelho = FALSE WHERE produto_id = '" + str(
                            #                 aux_produto) + "';")
                            #         mydb.commit()
                            #         print("Produto não contém leitelho nem buttermilk na descrição")
                            #         continue
                            #     except pymysql.Error as e:
                            #         print(e)
                            #         mydb.rollback()

                        except pymysql.Error as e:
                            print(e)
                            mydb.rollback()
                except:
                    pass
            else:
                cursor.execute("SELECT observacao FROM produto WHERE codigo = '" + str(codigo) + "';")
                observacao = cursor.fetchone()['observacao']

            start = time.time()

            observacao = observacao if auxDetalhes.empty else auxDetalhes['obs']

            try:
                ####VERIFICAR VAZIOS
                img = "" if not len(img) else img
                ####VERIFICAR VAZIOS
                auxSql = [name, codigo, ratings, price, ratings_num, img, link, observacao]
                # cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(
                #     palavra_chave) + "' LIMIT 1;")
                auxSql.extend([aux_site])
                cursor.execute(
                    """INSERT INTO produto (nome, codigo, nota, preco, avaliacoes, img, link, observacao, site_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE nota = '""" + str(ratings) + """', avaliacoes = '""" + str(ratings_num) + """', preco = '""" + str(price) + """';""", auxSql)
                mydb.commit()
            except pymysql.Error as e:
                print(e)
                mydb.rollback()

            cursor.execute("SELECT produto_id from produto WHERE codigo = '" + str(codigo) + "' LIMIT 1;")
            aux_produto = cursor.fetchone()["produto_id"]

            end = time.time()

            # cursor.execute("SELECT leitelho FROM produto WHERE codigo = '" + str(codigo) + "';")
            # if not cursor.fetchone()["leitelho"]:
            #     continue

            if observacao > 2: ############ SEGUINDO ORDEM codcoletaproduto_id
                continue

            #### ACESSANDO PÁGINA DE AVALIAÇÃO DO PRODUTO (SE HOUVER - SE FOR O CASO DE TER AVALIAÇÃO MAS SEM COMENTÁRIO, VAI SÓ ABRIR E FECHAR)
            if (ratings_num > cursor.execute(
                    "SELECT * FROM avaliacao WHERE produto_id = (SELECT produto_id FROM produto WHERE codigo = '" + str(
                            codigo) + "' LIMIT 1);")):
                link_review = item.find_element(By.XPATH, ".//a[@class='rating-count scroll-to']").get_attribute("href")
                tempAvaliacoes = coletaReviewNew(link_review, dominio).fillna("")
                # for link_perfil in tempAvaliacoes.link_perfil:
                #     tempPerfil, tempReview, tempCompras = coletaPerfil(link_perfil, dominio, False)
                #     if not tempPerfil.empty:
                #         profiles = pd.concat([profiles, tempPerfil], ignore_index=True)
                #     if not tempReview.empty:
                #         avaliacoes = pd.concat([avaliacoes, tempReview], ignore_index=True)
                #     if not tempCompras.empty:
                #         product_descr = pd.concat([product_descr, tempCompras], ignore_index=True)
                if not tempAvaliacoes.empty:
                    avaliacoes = pd.concat([avaliacoes, tempAvaliacoes], ignore_index=True)
                    tempAvaliacoes.fillna("", inplace=True)
                    for perfil in range(len(tempAvaliacoes)):
                        try:
                            if not cursor.execute("SELECT * FROM usuario WHERE codigo_perfil = '" + str(
                                    tempAvaliacoes.loc[perfil]["profile_id"]) + "';"):
                                auxSql = tempAvaliacoes.loc[perfil][
                                    ["author_name", "author_img", "profile_id", "profile_link"]].to_list()
                                auxSql.extend([aux_site])
                                cursor.execute(
                                    "INSERT INTO usuario (nome, img, codigo_perfil, link, site_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE img = '" + str(
                                        auxSql[1]) + "';", auxSql)
                                mydb.commit()
                                profiles = pd.concat([profiles, pd.DataFrame([auxSql],
                                                                             columns=["author_name", "author_img",
                                                                                      "profile_id", "profile_link",
                                                                                      "site_id"])],
                                                     ignore_index=True)

                                print("row " + str(perfil) + "/" + str(len(tempAvaliacoes) - 1))
                                if "" != tempAvaliacoes.loc[perfil]["author_img"]:
                                    caminho = "results/profile_img/iherb_" + tempAvaliacoes.loc[perfil][
                                        "profile_id"] + ".jpeg"
                                    if not os.path.exists(caminho):
                                        try:
                                            urllib.request.urlretrieve(
                                                tempAvaliacoes.loc[perfil]["author_img"].replace("/s.", "/l."), caminho)
                                        except HTTPError:
                                            pass
                        except pymysql.Error as e:
                            print(e)
                            mydb.rollback()

                    try:
                        auxSql = tempAvaliacoes.loc[:, [
                                                           "review_title", "review_text", "review_star",
                                                           "review_img", "author_name",
                                                           "review_date", "review_date",
                                                           "review_link", "codigo_avaliacao",
                                                           "profile_id"]].values.tolist()
                        cursor.execute(
                            'SELECT produto_id FROM produto WHERE codigo = "' + str(codigo) + '" LIMIT 1;')
                        # aux_produto = cursor.fetchone()["produto_id"]
                        for i in range(len(auxSql)):
                            cursor.execute('SELECT usuario_id FROM usuario WHERE codigo_perfil = "' + str(
                                auxSql[i][9]) + '" LIMIT 1;')
                            aux_profile = cursor.fetchone()["usuario_id"]
                            auxSql2 = auxSql[i][0:9]
                            auxSql2.extend([aux_produto, aux_profile])
                            cursor.execute(
                                'INSERT INTO avaliacao (titulo, texto, nota, img, autor, pais, dataavaliacao, link_avaliacao, codigo_avaliacao, produto_id, usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                                auxSql2)
                        mydb.commit()
                    except pymysql.Error as e:
                        print(e)
                        mydb.rollback()

        # for i in product_codigo:
        #    coletaReview(i)

        # IR PRA PRÓXIMA PÁGINA (SE HOUVER)
        try:
            driver.find_element('xpath', ".//a[contains(@class, 'pagination-next')]").click()
        except NoSuchElementException:
            break
        # paginacao.find_element(By.CLASS_NAME, "s-pagination-next").click()

    print("Exportando para excel")
    product.to_excel('results/iherb_' + palavra_chave + '_(produtos)_' + today + '.xlsx',
                     index=False)
    product_descr.to_excel('results/iherb_' + palavra_chave + '_(detalhes)_' + today + '.xlsx',
                           index=False)
    avaliacoes.to_excel('results/iherb_' + palavra_chave + '_(avaliacoes)_' + today + '.xlsx',
                        index=False)
    profiles.to_excel('results/iherb_' + palavra_chave + '_(perfis)_' + today + '.xlsx',
                      index=False)

    # print("Salvando imagens de perfil:")
    # for row in range(len(profiles)):
    #     print("row " + str(row) + "/" + str(len(profiles) - 1))
    #     if "" != profiles.loc[row]["author_img"]:
    #         caminho = "results/profile_img/iherb_" + profiles.loc[row]["profile_id"] + ".jpeg"
    #         if not os.path.exists(caminho):
    #             try:
    #                 urllib.request.urlretrieve(profiles.loc[row]["author_img"].replace("/s.", "/l."), caminho)
    #             except HTTPError:
    #                 pass
    # response = requests.get(profiles.loc[row]["author_img"])
    # nome_img = "results/profile_img/iherb_" + profiles.loc[row]["profile_id"] + ".jpeg"
    # # Verificar se a requisição foi bem-sucedida
    # if response.status_code == 200:
    #     # Abrir um arquivo em modo de escrita binária
    #     with open(nome_img, 'wb') as file:
    #         # Escrever o conteúdo da resposta no arquivo
    #         for chunk in response.iter_content(1024):
    #             file.write(chunk)
    # else:
    #     print(f'Falha ao baixar a imagem. Status code: {response.status_code}')

    #### CONCLUINDO INSERÇÕES NO BANCO DE DADOS
    cursor.close()
    mydb.close()

    driver.close()

    # for link_perfil in avaliacoes.link_perfil:
    #     tempPerfil, tempReview, tempCompras = coletaPerfil(link_perfil, dominio)
    #     profiles = pd.concat([profiles, tempPerfil], ignore_index=True)
    #     avaliacoes = pd.concat([avaliacoes, tempReview], ignore_index=True)
    #     product_descr = pd.concat([product_descr, tempCompras], ignore_index=True)

    return product, product_descr, avaliacoes, profiles

#
# def coletaProdutoNew():
#     # INICIANDO DATAFRAMES
#     product = pd.DataFrame()
#     product_descr = pd.DataFrame()
#
#     # INICIALIZE O DRIVER DO SELENIUM
#     driver = webdriver.Firefox(options=options)
#     # driver = webdriver.Edge()
#     driver.get("https://iherb.com/search/?kw=" + palavra_chave)
#     cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(palavra_chave) + "';")
#     aux_site = cursor.fetchone()["site_id"]
#
#     while True:
#         time.sleep(2)
#         # CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
#         items = WebDriverWait(driver, 5).until(
#             EC.presence_of_all_elements_located(
#                 (By.XPATH, './/div[@class="product-cell-container col-xs-12 col-sm-12 col-md-8 col-lg-6"]')))
#
#         while len(items):
#             item = items.pop(0)
#             name = item.find_element(By.CLASS_NAME, 'product-title').text.strip()
#             codigo = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
#                 "data-product-id")
#             link = item.find_element('xpath', './/div/a[@class="absolute-link product-link"]').get_attribute("href")
#             img = item.find_element('xpath', ".//div[@class='product-image-wrapper']/span/img").get_attribute("src")
#             product = pd.concat([product, pd.DataFrame([[name, codigo, link, img]],
#                                                        columns=["name", "codigo", "link", "img"])],
#                                 ignore_index=True)
#         for i in range(len(product)):
#             auxDetalhes = pd.DataFrame()
#             if not cursor.execute(
#                     "SELECT a.iherb_id FROM iherb AS a LEFT JOIN produto AS p ON p.produto_id = a.produto_id AND p.codigo = '" + str(
#                         product["codigo"][i]) + "';"
#             ):
#                 try:
#                     time.sleep(120)
#                     print(link)
#                     auxDetalhes = coletaDetalhes(link, dominio)
#                     if not auxDetalhes.empty:
#                         product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
#                         cursor.execute(
#                             "SELECT produto_id FROM produto WHERE codigo = '" + str(product["codigo"][i]) + "';")
#
#                         auxDetalhes.values.tolist()
#                 except:
#                     pass
#
#             # #### IR PRA PRÓXIMA PÁGINA (SE HOUVER)
#             # try:
#             #     driver.find_element('xpath', ".//a[contains(@class, 'pagination-next')]").click()
#             # except NoSuchElementException:
#             #     break
#
#         # for i in range(len(product)):
#         #     auxDetalhes = pd.DataFrame()
#         #     if not cursor.execute("SELECT a.iherb_id FROM iherb AS a LEFT JOIN produto AS p ON p.produto_id = a.produto_id AND p.codigo = '" + str(codigo) + "';"
#         #     ):
#         #         try:
#         #             time.sleep(120)
#         #             print(product["link"][i])
#         #             auxDetalhes = coletaDetalhes(product["link"][i], dominio)
#         #             if not auxDetalhes.empty:
#         #                 product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
#         #                 cursor.execute("SELECT produto_id FROM produto WHERE codigo = '%s';", product["codigo"][i])
#         #
#         #
#         #                 print("ok")
#         #         except:
#         #             pass


def coletaProdutoPerfil():
    # INICIALIZE O DRIVER DO SELENIUM
    driver2 = webdriver.Firefox(options=options)

    cursor.execute("SELECT * FROM usuario WHERE length(img) > 0 and site_id = " + str(aux_site) + ";")
    usuarios = pd.DataFrame(cursor.fetchall())
    product_descr = pd.DataFrame()

    for i in range(len(usuarios)):
        usuario = usuarios.iloc[i]
        driver2.get(usuario["link"])
        start = time.time()

        bio = driver2.find_element(By.XPATH, ".//div[@data-testid='me-profile-about']").text
        pais = driver2.find_element(By.XPATH, ".//div[@data-testid='me-profile-country']").text.split(": ")[-1]

        try:
            auxSql = [bio, pais, usuario["usuario_id"]]
            cursor.execute("UPDATE usuario SET bio = %s, pais = %s WHERE usuario_id = %s;", auxSql)
            mydb.commit()
        except pymysql.err as e:
            print(e)
            mydb.rollback()

        while True:
            reviews = driver2.find_elements(By.XPATH, ".//div[@data-testid='me-my-reviews']")
            while len(reviews):
                review_element = reviews.pop(0)
                link = review_element.find_element(By.XPATH, ".//div/a").get_attribute("href")
                end = time.time()
                aux_tempo = random.randint(1, 30) + 0 if (end - start) >= 120 else 120 - (end - start)
                print("Aguardando " + str(int(aux_tempo)) + "s para coletaDetalhes(" + str(link.split("/")[-1]) + ")")
                time.sleep(aux_tempo)
                auxDetalhes = pd.DataFrame()
                auxDetalhes = coletaDetalhes(link, dominio, usuario["link"])
                if not auxDetalhes.empty:
                    auxDetalhes.fillna("", inplace=True)
                    product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
                    print(link + " Descr ok")
                start = time.time()

                try:
                    driver2.find_element(By.XPATH, ".//button[@aria-label='Go to next page']").click()
                except:
                    break


palavra_chave = "buttermilk"

#### .com.br, .com, .co.uk, .ca, .de (buttermilch), .fr (lait ribot), .com.mx, .it, .es (mazada, suero de mantequilla), .co.jp, .sg, .ae, .com.au, .in, .nl, .sa, .com.tu, .se, .pl, .com.be, .eg, .at,
dominio = ".com"


# coletaElemento(palavra_chave, dominio)

# coletaReview("B07HM62FL3")

# coletaDetalhes('B09ZMTBTSV')
#


###### PRA TESTAR TEMPO DE ESPERA PRA COLETAR O PRODUTO
# def coletaElemento2(palavra_chave, dominio):
#     today = date.today().strftime("%Y%m%d")
#     cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(palavra_chave) + "';")
#     aux_site = cursor.fetchone()["site_id"]
#     # options.set_preference("network.cookie.cookieBehavior", 2)
#
#     # INICIANDO DATAFRAMES
#     product = pd.DataFrame()
#     product_descr = pd.DataFrame()
#     profiles = pd.DataFrame()
#     avaliacoes = pd.DataFrame()
#
#     # INICIALIZE O DRIVER DO SELENIUM
#     driver = webdriver.Firefox(options=options)
#     # driver = webdriver.Edge()
#     driver.get("https://iherb.com/search?kw=" + palavra_chave)
#
#     while True:
#         time.sleep(2)
#         # CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
#         items = WebDriverWait(driver, 5).until(
#             EC.presence_of_all_elements_located(
#                 (By.XPATH, './/div[@class="product-cell-container col-xs-12 col-sm-12 col-md-8 col-lg-6"]')))
#
#         start = time.time()
#         while len(items):
#
#             item = items.pop(0)
#
#             name = item.find_element(By.CLASS_NAME, 'product-title').text.strip()
#
#             codigo = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
#                 "data-product-id")
#
#             # DESMEMBRANDO PREÇO (INCLUIR MOEDA TBM?)
#             moeda = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
#                 "data-ga-discount-price")
#             # whole_price = item.find_elements('xpath', './/span[@class="a-price-whole"]')
#             # fraction_price = item.find_elements('xpath', './/span[@class="a-price-fraction"]')
#             # if whole_price and fraction_price:
#             #     price = float('.'.join([whole_price[0].text.replace('.', '').replace(',', ''), fraction_price[0].text]))
#             # else:
#             #     price = 0.0
#             price = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
#                 "data-ga-discount-price")
#
#             try:
#                 ratings = float(
#                     item.find_element(By.XPATH, ".//div/a[@class='rating-count scroll-to']").get_attribute(
#                         "title").split(
#                         "/")[0])
#                 ratings_num = int(
#                     item.find_element(By.XPATH, ".//div/a[@class='rating-count scroll-to']").get_attribute(
#                         "title").split(
#                         " ")[-2].replace(',', '').replace('.', ''))
#             except NoSuchElementException:
#                 ratings = 0.0
#                 ratings_num = 0
#
#             # LINK DE CADA PRODUTO
#             link = item.find_element('xpath', './/div/a[@class="absolute-link product-link"]').get_attribute("href")
#
#             # LINK DA IMAGEM -> DEPOIS BAIXAR O ARQUIVO
#             img = item.find_element('xpath', ".//div[@class='product-image-wrapper']/span/img").get_attribute("src")
#
#             # SALVANDO NO DATAFRAME
#             product = pd.concat(
#                 [product,
#                  pd.DataFrame(data=[[dominio, codigo, name, moeda, price, ratings, ratings_num, img, link]],
#                               columns=['dominio', 'codigo', 'name', 'moeda', 'price', 'ratings', 'ratings_num',
#                                        'img', 'link'])],
#                 ignore_index=True).fillna("")
#
#             try:
#                 ####VERIFICAR VAZIOS
#                 img = "" if not len(img) else img
#                 ####VERIFICAR VAZIOS
#                 auxSql = [name, codigo, ratings, price, ratings_num, img, link]
#                 cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(
#                     palavra_chave) + "' LIMIT 1;")
#                 auxSql.extend([aux_site])
#                 cursor.execute(
#                     "INSERT INTO produto (nome, codigo, nota, preco, avaliacoes, img, link, site_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE nota = '" + str(
#                         ratings) + "', avaliacoes = '" + str(ratings_num) + "';", auxSql)
#                 mydb.commit()
#             except pymysql.Error as e:
#                 print(e)
#                 mydb.rollback()
#
#             cursor.execute("SELECT produto_id from produto WHERE codigo = '" + str(codigo) + "' LIMIT 1;")
#             aux_produto = cursor.fetchone()["produto_id"]
#
#             end = time.time()
#
#             auxDetalhes = pd.DataFrame()
#             if not cursor.execute(
#                     "SELECT iherb_id FROM iherb WHERE produto_id IN (SELECT produto_id FROM produto WHERE codigo = '" + str(
#                             codigo) + "');"):
#                 tempo = 120
#                 while tempo <= 240:
#                     try:
#                         aux_tempo = random.randint(1, 30) + 0 if (end - start) >= tempo else tempo - (end - start)
#                         print("Aguardando " + str(int(aux_tempo)) + "s para coletaDetalhes(" + str(codigo) + ")")
#                         time.sleep(aux_tempo)
#                         auxDetalhes = coletaDetalhes(link, dominio)
#                         if not auxDetalhes.empty:
#                             auxDetalhes.fillna("", inplace=True)
#                             product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
#                             print(link + " Descr ok")
#                             try:
#                                 auxSql = auxDetalhes.loc[:,
#                                          ['tag', 'marca', 'descricao', 'uso', 'ingredientes', 'advertencia',
#                                           'aviso', 'tabela']].values.flatten().tolist()
#                                 auxSql.extend([aux_produto])
#                                 cursor.execute(
#                                     "INSERT INTO iherb (tag, marca, descricao, uso, ingredientes, advertencias, aviso, tabela, produto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
#                                     auxSql)
#                                 mydb.commit()
#
#                                 try:
#                                     ##### VERIFICA SE TEM LEITELHO OU BUTTERMILK EM ALGUM DETALHE DO PRODUTO
#                                     if cursor.execute("SELECT produto_id FROM iherb WHERE produto_id = '" + str(
#                                             aux_produto) + "' AND tabela NOT REGEXP 'leitelho|buttermilk';"):
#                                         cursor.execute(
#                                             "UPDATE produto SET observacao = CONCAT_WS('\n', observacao, '- NÃO CONTÉM PALAVRA LEITELHO OU BUTTERMILK NA DESCRIÇÃO'), leitelho = FALSE WHERE produto_id = '" + str(
#                                                 aux_produto) + "';")
#                                         mydb.commit()
#                                         print("Produto não contém leitelho nem buttermilk na descrição")
#                                         continue
#                                     elif cursor.execute("SELECT produto_id FROM iherb WHERE produto_id = '" + str(
#                                             aux_produto) + "' AND tabela REGEXP 'leitelho|buttermilk';"):
#                                         cursor.execute(
#                                             "UPDATE produto SET leitelho = TRUE WHERE produto_id = '" + str(
#                                                 aux_produto) + "';")
#                                         mydb.commit()
#                                 except pymysql.Error as e:
#                                     print(e)
#                                     mydb.rollback()
#                             except pymysql.Error as e:
#                                 print(e)
#                                 mydb.rollback()
#                             break
#                         else:
#                             tempo += 60
#                             print("aumentando tempo de espera para %s", tempo)
#                     except:
#                         pass
#
#             start = time.time()
#
#             cursor.execute("SELECT leitelho FROM produto WHERE codigo = '" + str(codigo) + "';")
#             if not cursor.fetchone()["leitelho"]:
#                 continue
#
#             #### ACESSANDO PÁGINA DE AVALIAÇÃO DO PRODUTO (SE HOUVER - SE FOR O CASO DE TER AVALIAÇÃO MAS SEM COMENTÁRIO, VAI SÓ ABRIR E FECHAR)
#             if (ratings_num > cursor.execute(
#                     "SELECT * FROM avaliacao WHERE produto_id = (SELECT produto_id FROM produto WHERE codigo = '" + str(
#                             codigo) + "' LIMIT 1);")):
#                 link_review = item.find_element(By.XPATH, ".//a[@class='rating-count scroll-to']").get_attribute("href")
#                 tempAvaliacoes = coletaReviewNew(link_review, dominio).fillna("")
#                 # for link_perfil in tempAvaliacoes.link_perfil:
#                 #     tempPerfil, tempReview, tempCompras = coletaPerfil(link_perfil, dominio, False)
#                 #     if not tempPerfil.empty:
#                 #         profiles = pd.concat([profiles, tempPerfil], ignore_index=True)
#                 #     if not tempReview.empty:
#                 #         avaliacoes = pd.concat([avaliacoes, tempReview], ignore_index=True)
#                 #     if not tempCompras.empty:
#                 #         product_descr = pd.concat([product_descr, tempCompras], ignore_index=True)
#                 if not tempAvaliacoes.empty:
#                     avaliacoes = pd.concat([avaliacoes, tempAvaliacoes], ignore_index=True)
#                     tempAvaliacoes.fillna("", inplace=True)
#                     for perfil in range(len(tempAvaliacoes)):
#                         try:
#                             if not cursor.execute("SELECT * FROM usuario WHERE codigo_perfil = '" + str(
#                                     tempAvaliacoes.loc[perfil]["profile_id"]) + "';"):
#                                 auxSql = tempAvaliacoes.loc[perfil][
#                                     ["author_name", "author_img", "profile_id", "profile_link"]].to_list()
#                                 auxSql.extend([aux_site])
#                                 cursor.execute(
#                                     "INSERT INTO usuario (nome, img, codigo_perfil, link, site_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE img = '" + str(
#                                         auxSql[1]) + "';", auxSql)
#                                 mydb.commit()
#                                 profiles = pd.concat([profiles, pd.DataFrame([auxSql],
#                                                                              columns=["author_name", "author_img",
#                                                                                       "profile_id", "profile_link",
#                                                                                       "site_id"])],
#                                                      ignore_index=True)
#
#                                 print("row " + str(perfil) + "/" + str(len(tempAvaliacoes) - 1))
#                                 if "" != tempAvaliacoes.loc[perfil]["author_img"]:
#                                     caminho = "results/profile_img/iherb_" + tempAvaliacoes.loc[perfil][
#                                         "profile_id"] + ".jpeg"
#                                     if not os.path.exists(caminho):
#                                         try:
#                                             urllib.request.urlretrieve(
#                                                 tempAvaliacoes.loc[perfil]["author_img"].replace("/s.", "/l."), caminho)
#                                         except HTTPError:
#                                             pass
#                         except pymysql.Error as e:
#                             print(e)
#                             mydb.rollback()
#
#                     try:
#                         auxSql = tempAvaliacoes.loc[:, [
#                                                            "review_title", "review_text", "review_star",
#                                                            "review_img", "author_name",
#                                                            "review_date", "review_date",
#                                                            "review_link", "codigo_avaliacao",
#                                                            "profile_id"]].values.tolist()
#                         cursor.execute(
#                             'SELECT produto_id FROM produto WHERE codigo = "' + str(codigo) + '" LIMIT 1;')
#                         # aux_produto = cursor.fetchone()["produto_id"]
#                         for i in range(len(auxSql)):
#                             cursor.execute('SELECT usuario_id FROM usuario WHERE codigo_perfil = "' + str(
#                                 auxSql[i][9]) + '" LIMIT 1;')
#                             aux_profile = cursor.fetchone()["usuario_id"]
#                             auxSql2 = auxSql[i][0:9]
#                             auxSql2.extend([aux_produto, aux_profile])
#                             cursor.execute(
#                                 'INSERT INTO avaliacao (titulo, texto, nota, img, autor, pais, dataavaliacao, link_avaliacao, codigo_avaliacao, produto_id, usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
#                                 auxSql2)
#                         mydb.commit()
#                     except pymysql.Error as e:
#                         print(e)
#                         mydb.rollback()
#
#         # for i in product_codigo:
#         #    coletaReview(i)
#
#         # IR PRA PRÓXIMA PÁGINA (SE HOUVER)
#         try:
#             driver.find_element('xpath', ".//a[contains(@class, 'pagination-next')]").click()
#         except NoSuchElementException:
#             break
#         # paginacao.find_element(By.CLASS_NAME, "s-pagination-next").click()
#
#     print("Exportando para excel")
#     product.to_excel('results/iherb_' + palavra_chave + '_(produtos)_' + today + '.xlsx',
#                      index=False)
#     product_descr.to_excel('results/iherb_' + palavra_chave + '_(detalhes)_' + today + '.xlsx',
#                            index=False)
#     avaliacoes.to_excel('results/iherb_' + palavra_chave + '_(avaliacoes)_' + today + '.xlsx',
#                         index=False)
#     profiles.to_excel('results/iherb_' + palavra_chave + '_(perfis)_' + today + '.xlsx',
#                       index=False)
#
#     # print("Salvando imagens de perfil:")
#     # for row in range(len(profiles)):
#     #     print("row " + str(row) + "/" + str(len(profiles) - 1))
#     #     if "" != profiles.loc[row]["author_img"]:
#     #         caminho = "results/profile_img/iherb_" + profiles.loc[row]["profile_id"] + ".jpeg"
#     #         if not os.path.exists(caminho):
#     #             try:
#     #                 urllib.request.urlretrieve(profiles.loc[row]["author_img"].replace("/s.", "/l."), caminho)
#     #             except HTTPError:
#     #                 pass
#     # response = requests.get(profiles.loc[row]["author_img"])
#     # nome_img = "results/profile_img/iherb_" + profiles.loc[row]["profile_id"] + ".jpeg"
#     # # Verificar se a requisição foi bem-sucedida
#     # if response.status_code == 200:
#     #     # Abrir um arquivo em modo de escrita binária
#     #     with open(nome_img, 'wb') as file:
#     #         # Escrever o conteúdo da resposta no arquivo
#     #         for chunk in response.iter_content(1024):
#     #             file.write(chunk)
#     # else:
#     #     print(f'Falha ao baixar a imagem. Status code: {response.status_code}')
#
#     #### CONCLUINDO INSERÇÕES NO BANCO DE DADOS
#     cursor.close()
#     mydb.close()
#
#     driver.close()
#
#     # for link_perfil in avaliacoes.link_perfil:
#     #     tempPerfil, tempReview, tempCompras = coletaPerfil(link_perfil, dominio)
#     #     profiles = pd.concat([profiles, tempPerfil], ignore_index=True)
#     #     avaliacoes = pd.concat([avaliacoes, tempReview], ignore_index=True)
#     #     product_descr = pd.concat([product_descr, tempCompras], ignore_index=True)
#
#     return product, product_descr, avaliacoes, profiles

import requests
import pandas as pd
import json
import os

def coletaReviewsV3():
    cursor.execute("SELECT codigo FROM produto WHERE leitelho = 1 AND produto_id IN (SELECT produto_id from iherb);")
    ids = pd.DataFrame(cursor.fetchall())
    # driver2 = webdriver.Firefox(options = options)
    # driver2 = webdriver.Edge()

    options.set_preference('devtools.jsonview.enabled', False)
    driver2 = webdriver.Firefox(options = options)

    reviews = []

    for i, id in enumerate(ids['codigo']):
        # Nome do arquivo para salvar o conteúdo
        file_name = id+"_reviews.txt"
        if os.path.isfile('reviews/'+file_name):
            continue

        # URL da API
        url = "https://br.iherb.com/ugc/api/review/v1/search?pid="+id+"&lc=pt-BR&textToSearch=&tag=&sortId=2&withImagesOnly=false&isShowTranslated=true&withUgcSummary=true&page=1&limit=100000"
        driver2.get(url)

        try:
            data = json.loads(WebDriverWait(driver2, 5).until(
                    EC.presence_of_element_located(('tag name', 'pre'))).text)
        except TimeoutException as e:
            print(i, id, e)
            continue

        with open('reviews/'+file_name, "w") as f:
            f.write(json.dumps(data))

        for j, item in enumerate(data['items']):
            try:
                reviewText = item['reviewText']
            except KeyError:
                reviewText: ''

            try:
                country = item['profileInfo']['country']
            except KeyError:
                country: ''

            try:
                profileImg = item['profileInfo']['image']['thumbnails'][2]['fullPath']
            except KeyError:
                profileImg = ''

            try:
                user_id = item['profileInfo']['username']
            except KeyError:
                user_id = ''

            reviews.append({
                'product_id': id,
                'review_id': item['id'],
                'user_id': user_id,
                'user': item['customerNickname'],
                'country': country,
                'reviewTitle': item['reviewTitle'],
                'reviewText': reviewText,
                'idioma': item['languageCode'],
                # 'ratingValue': item['ratingValue'],
                'postedDate': item['postedDate'],
                'profileImg': profileImg
            })
            # print(i,j)
    Review = pd.DataFrame(reviews)
    Review.to_excel('reviews/Reviews.xlsx')
    driver2.close()
