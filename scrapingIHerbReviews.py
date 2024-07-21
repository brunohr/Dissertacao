import locale
import time
from datetime import date
import random
from datetime import datetime

import pandas as pd
import pymysql
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

import os
import urllib.request
from urllib.error import HTTPError
import requests

import re

locale.setlocale(locale.LC_ALL, 'pt_BR')

# Define the proxy server
# global PROXY
# PROXY = "50.207.199.80:80"

# Set ChromeOptions()
global options
options = webdriver.FirefoxOptions()
options.set_preference("dom.webdriver.enabled", False)
options.set_preference('useAutomationExtension', False)
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Add the proxy as argument
# options.add_argument("--proxy-server=%s" % PROXY)


# INICIANDO CONEXÃO COM O BANCO DE DADOS
global mydb, cursor
mydb = pymysql.connect(host="localhost", database='scraping2', user="root", passwd="", port = 3307,
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()

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


def coletaReview(link_review, dominio):
    driver = webdriver.Firefox(options=options)

    driver.get(link_review)
    try:
        driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    except NoSuchElementException:
        pass

    link_produto = driver.find_element(By.XPATH,
                                       ".//div/a[@class='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-1o1ny0d']").get_attribute(
        "href")
    codigo = re.split('/', link_produto)[-1]

    # print(" - Reviews: " + codigo)

    # INICIANDO LISTA PARA ARMAZENAR
    product_review = []

    # PEGANDO CADA CARD DE AVALIAÇÃO
    while True:
        # time.sleep(3)
        # coletaDetalhes(link, dominio)
        # # PEGANDO CADA CARD DE AVALIAÇÃO
        # review_elements = driver.find_elements(By.CSS_SELECTOR, '[id*=review-card]')
        try:
            review_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@class='MuiBox-root css-jer996']")))
        except:
            break

        try:
            js_string = "var element = document.getElementById('px-captcha-wrapper');element.remove();"
            driver.execute_script(js_string)
        except:
            pass

        # EXTRAINDO NOME DO AUTOR
        author_name = review_element.find_element(By.XPATH,
                                                  './/div/a[@class="MuiTypography-root MuiTypography-body1 css-ehmaku"]').text.strip()

        # EXTRAIR TÍTULO AVALIAÇÃO
        review_title = review_element.find_element(By.XPATH,
                                                   './/span[@class="MuiTypography-root MuiTypography-body1 css-1dbe95"]').text.strip()

        # EXTRAINDO TEXTO AVALIAÇÃO
        review_text = review_element.find_element(By.XPATH, './/div[@data-testid="review-text"]').text.strip()

        # EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
        # review_star = float(
        #     review_element.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent").split()[0].replace(
        #         ',', '.'))

        # EXTRAINDO DATA AVALIAÇÃO
        # review_date = ' '.join(review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[-5:])
        # review_date = datetime.strptime(review_date, "%d de %B de %Y").strftime("%Y/%m/%d")
        review_date = review_element.find_element(By.XPATH, './/span[@data-testid="review-posted-date"]').text.strip()

        # EXTRAINDO PAÍS AVALIAÇÃO
        # review_country = review_element.find_element(By.CLASS_NAME, 'review-date').text.split()  ##arrumar

        # EXTRAINDO LINK E IMAGEM DO PERFIL PARA COLETA SEGUINTE
        try:
            profile_link = review_element.find_element(By.XPATH,
                                                       './/div/a[@class="MuiTypography-root MuiTypography-body1 css-ehmaku"]').get_attribute(
                "href")
            profile_id = profile_link.split('/')[-1]
            try:
                review_element.find_element(By.XPATH, ".//div/svg[@data-testid='PersonIcon']")
                profile_img = ""
                author_img = ""
            except NoSuchElementException:
                # SALVANDO A IMG PRA NÃO DEPENDER DE INTERNET PRO PROCESSAMENTO DA MESMA
                profile_img = review_element.find_element(By.XPATH,
                                                          ".//div/img[@class='MuiAvatar-img css-1hy9t21']").get_attribute(
                    "src")
                author_img = re.sub("/s.jpeg", "/l.jpeg", profile_img)

                urllib.request.urlretrieve(author_img,
                                           "results/profile_img/iherb" + dominio + "_" + profile_id + ".jpeg")

            # profiles = pd.concat([profiles, coletaPerfil(profile_link, review_country)], ignore_index=True)
        except NoSuchElementException:
            profile_link, profile_id, author_img = None, None, None

        try:
            review_img = review_element.find_element(By.XPATH, './/div/img[@class="css-1u8hqvf"]').get_attribute("src")
        except NoSuchElementException:
            review_img = None

        # if profile_link:
        #     coletaPerfil(profile_link, review_country)

        product_review.append(
            (dominio, review_title, review_text, review_img, "", author_name, author_img, review_date,
             "", link_review, profile_link, profile_id, link_produto, codigo))
        break
        # print("codigo: ", codigo)
        # print("Title: ", review_title)
        # print("Review: ", review_text)
        # print("Stars: ", review_star)
        # print("Author: ", author_name)
        # print("Review Date: ", review_date)
        # print("\n")

    # PASSAR PRA PRÓXIMA PAG
    # try:
    #     driver.find_element(By.CLASS_NAME, 'a-pagination').find_element(By.CLASS_NAME, "a-last").click()
    # except NoSuchElementException:
    #     break
    # try:
    #     driver.find_element(By.CLASS_NAME, "a-disabled a-last")
    # except NoSuchElementException:
    #     break

    driver.close()

    # ENVIANDO PARA O BANCO DE DADOS
    # try:
    #     sql = 'insert into teste.tbl_avaliacoes (dominio, codigo, titulo, texto, nota, autor, date, pais, helpful_votes, link_avaliacao, link_perfil, id_perfil) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #     cursor.executemany(sql, product_review)
    #     print(f"Avaliações do produto {codigo} inseridas")
    #     mydb.commit()
    # except pymysql.Error as e:
    #     mydb.rollback()
    #     print(e)

    # SALVANDO AS LISTAS EM DF
    review = pd.DataFrame(data=product_review,
                          columns=['dominio', 'title', 'text', 'img', 'star', 'user', 'user_img', 'date', 'country',
                                   'link_avaliacao',
                                   'link_perfil', 'id_perfil', 'link_produto', 'codigo'])

    return review  # , profiles

def coletaReviewAux(link_review, dominio):
    driver = webdriver.Firefox(options=options)
    # numPag = 1
    #
    # # PÁGINA DAS AVALIAÇÕES DO PRODUTO
    # link_reviews = 'https://www.amazon' + dominio + '/product-reviews/' + codigo + '?pageNumber='
    # driver.get(link_reviews + str(numPag))
    # try:
    #     driver.find_element(By.ID, "sp-cc-acceptall-link").click()
    # except NoSuchElementException:
    #     pass

    driver.get(link_review)

    # INICIANDO LISTA PARA ARMAZENAR
    review_links = []

    # PEGANDO CADA CARD DE AVALIAÇÃO
    while True:
        time.sleep(2)

        try:
            js_string = "var element = document.getElementById('px-captcha-wrapper');element.remove();"
            driver.execute_script(js_string)
        except:
            pass

        #
        # # PEGANDO CADA CARD DE AVALIAÇÃO
        # review_elements = driver.find_elements(By.CSS_SELECTOR, '[id*=review-card]')
        try:
            # pag = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="MuiBox-root css-i9gxme"]')))
            review_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, './/div[@class="MuiBox-root css-1v71s4n"]')))
        except:
            break
        # if not review_elements:
        #     break
        for review_element in review_elements:
            # EXTRAINDO LINK DA POSTAGEM
            review_link = review_element.find_element(By.XPATH,
                                                      './/div/a[@class="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone css-bvdvm5"]').get_attribute(
                "href")
            if review_link:
                review_links.append(review_link)

        try:
            driver.find_element(By.XPATH, ".//button[@aria-label='Go to next page' and disabled='']")
        except NoSuchElementException:
            pass

        try:
            driver.find_element(By.XPATH, ".//button[@aria-label='Go to next page']").click()
        except:
            break

        # try:
        #     WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, ".//div[@id='cm_cr-pagination_bar']/ul/li[@class='a-last']"))).click()
        # except:
        #     break

    driver.close()

    # ENVIANDO PARA O BANCO DE DADOS
    # try:
    #     sql = 'insert into teste.tbl_avaliacoes (dominio, codigo, titulo, texto, nota, autor, date, pais, helpful_votes, link_avaliacao, link_perfil, id_perfil) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #     cursor.executemany(sql, product_review)
    #     print(f"Avaliações do produto {codigo} inseridas")
    #     mydb.commit()
    # except pymysql.Error as e:
    #     mydb.rollback()
    #     print(e)

    # review = pd.DataFrame()
    # for link in review_links:
    #     review = pd.concat([review, coletaReview(link, dominio)], ignore_index=True)

    # return review  # , profiles

    return pd.DataFrame(data=review_links, columns=["link"])


def coletaReviewNew(link_review, dominio):
    # options.headless = True
    # driver2 = webdriver.Firefox(options=options)

    driver2 = webdriver.Edge()
    driver2.get(link_review+"?sort=2") ####ORDENANDO POR MAIS RECENTE, PRA PODER ENCERRAR ASSIM QUE APARECER O PRIMEIRO COMENTÁRIO JÁ SALVO NO BANCO

    # INICIANDO LISTA PARA ARMAZENAR
    product_review = []
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
            pass

        auxAnalises = int(driver2.find_element(By.XPATH, ".//h6[@data-testid='global-reviews']").text.split("(")[1].split(")")[0].replace(',', '').replace('.', ''))
        analisesSql = cursor.execute(
                "SELECT * FROM avaliacao WHERE produto_id = (SELECT produto_id FROM produto WHERE codigo = '" + str(
                    codigo) + "' LIMIT 1);")

        flag = True
        if auxAnalises > analisesSql:

            # PEGANDO CADA CARD DE AVALIAÇÃO
            # while (len(product_review) < 200):
            while flag:
                if len(product_review) >= auxAnalises: ### só por precaução
                    # print("ok")
                    break
                # TENTANDO CONTORNAR StaleElementReferenceException
                try:
                    WebDriverWait(driver2, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//nav[@aria-label='pagination navigation']")))
                except:
                    break

                try:
                    js_string = "var element = document.getElementById('px-captcha-wrapper');element.remove();"
                    driver2.execute_script(js_string)
                except:
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
                        if cursor.execute("SELECT * FROM avaliacao WHERE codigo_avaliacao = '" + str(review_id) + "';") > 0:
                            # #### SE SIM, VAI PRO PRÓXIMO
                            # i += 1
                            # continue
                            flag = False
                            break

                        # EXTRAIR NOME AUTOR/USUÁRIO
                        author_name = review_element.find_element(By.XPATH,
                                                                  './/div/a[@class="MuiTypography-root MuiTypography-body1 css-ehmaku"]').text.strip()

                        # EXTRAIR TÍTULO AVALIAÇÃO
                        review_title = review_element.find_element(By.XPATH,
                                                                   './/span[@class="MuiTypography-root MuiTypography-body1 css-1dbe95"]').text.strip()

                        # EXTRAINDO TEXTO AVALIAÇÃO
                        review_text = review_element.find_element(By.XPATH, './/div[@data-testid="review-text"]').text.strip()

                        # EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
                        # review_star = float(
                        #     review_element.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent").split()[0].replace(
                        #         ',', '.'))

                        # EXTRAINDO DATA AVALIAÇÃO
                        # review_date = ' '.join(review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[-5:])
                        # review_date = datetime.strptime(review_date, "%d de %B de %Y").strftime("%Y/%m/%d")
                        review_date = review_element.find_element(By.XPATH,
                                                                  './/span[@data-testid="review-posted-date"]').text.strip()

                        # EXTRAINDO PAÍS AVALIAÇÃO
                        # review_country = review_element.find_element(By.CLASS_NAME, 'review-date').text.split()  ##arrumar

                        # EXTRAINDO LINK E IMAGEM DO PERFIL PARA COLETA SEGUINTE
                        profile_link = review_element.find_element(By.XPATH, './/div[@class="MuiBox-root css-1i27l4i"]/a[@class="MuiTypography-root MuiTypography-body1 css-ehmaku"]').get_attribute("href")
                        profile_id = profile_link.split('/')[-1]

                        try:
                            review_element.find_element(By.XPATH, ".//div/*[@data-testid='PersonIcon']")
                            profile_img = ""
                            author_img = ""
                        except NoSuchElementException:
                            # SALVANDO A IMG PRA NÃO DEPENDER DE INTERNET PRO PROCESSAMENTO DA MESMA
                            profile_img = review_element.find_element(By.XPATH, ".//div/img[@class='MuiAvatar-img css-1hy9t21']").get_attribute("src")
                            author_img = profile_img.replace("/s.", "/l.")
                            # urllib.request.urlretrieve(author_img,
                            #                            "results/profile_img/iherb" + dominio + "_" + profile_id + ".jpeg")

                            # profiles = pd.concat([profiles, coletaPerfil(profile_link, review_country)], ignore_index=True)
                        except NoSuchElementException:
                            profile_link, profile_id, author_img = "", "", ""

                        try:
                            review_img = review_element.find_element(By.XPATH,
                                                                     './/div/img[@class="css-1u8hqvf"]').get_attribute("src")
                        except NoSuchElementException:
                            review_img = ""

                        review_star = len(review_element.find_elements(By.XPATH, ".//*[@fill='#FAC627']"))

                        # if profile_link:
                        #     coletaPerfil(profile_link, review_country)

                        product_review.append(
                            (dominio, review_link, review_title, review_text, review_star, review_img, author_name, author_img, review_date,
                             link_review, profile_link, profile_id, link_produto, codigo, review_id))

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
                    driver2.find_element(By.XPATH, ".//button[@aria-label='Go to next page']").click()
                except:
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
        pass

    driver2.close()

    print(link_review, str(len(product_review)) + "+" + str(analisesSql) + " / " + str(auxAnalises))
    return pd.DataFrame(data=product_review,
                        columns=["dominio", "review_link", "review_title", "review_text", "review_star", "review_img", "author_name",
                                 "author_img", "review_date",
                                 "link_reviews", "profile_link", "profile_id", "link_produto", "codigo_produto", "codigo_avaliacao"]).fillna("")


def coletaDetalhes(link, dominio, review=False):
    driver2 = webdriver.Firefox(options = options)
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
    moeda, price = None, None

    descricao, uso, ingredientes, advertencia, aviso = None, None, None, None, None

    aux = pag.find_elements(By.XPATH,
                            './/div[@class="row"]/div[contains(@class, "col-xs-24")]/div[@class="row item-row"]')

    tabela = pag.find_element(By.XPATH, ".//div[@class='item-row']/div[@class='row']").get_attribute("textContent")
    ### tentando separar essa tabela
    for bloco in aux:
        if "Descr" in bloco.get_attribute("innerText"): ### descrição / description
            descricao = bloco.get_attribute("innerText")
        elif "Suge" in bloco.get_attribute("innerText"): ### uso sugerido / sugested
            uso = bloco.get_attribute("innerText")
        elif "Ingred" in bloco.get_attribute("innerText"): ### ingredientes / ingredients
            ingredientes = bloco.get_attribute("innerText")
        elif "Advert" in bloco.get_attribute("innerText") or "Warning" in bloco.get_attribute("innerText"): ### advertencia / warning
            advertencia = bloco.get_attribute("innerText")
        elif "Legal" in bloco.get_attribute("innerText"): ### Uso legal / Legal use
            aviso = bloco.get_attribute("innerText")

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
        data=[[dominio, nome, marca, tag, moeda, price, descricao, uso, ingredientes, advertencia, aviso, tabela]],
        columns=['dominio', 'nome', 'marca', 'tag', 'moeda', 'price', 'descricao', 'uso', 'ingredientes', 'advertencia',
                 'aviso', 'tabela']).fillna("")


def coletaPerfil(link_perfil, dominio, coletaProdutos=False):
    # driver = webdriver.Firefox(options=options)
    driver = webdriver.Edge()
    driver.get(link_perfil)

    try:
        driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    except NoSuchElementException:
        pass

    try:
        pag = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "MuiBox-root css-134cxvg")))
    except:
        driver.close()
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    compras = pd.DataFrame()
    lista_reviews = pd.DataFrame()
    id_perfil = link_perfil.split('/me/.')[-1]

    nome = pag.find_element(By.XPATH, ".//h5[@data-testid='me-profile-name']").text.strip()
    img = pag.find_element(By.XPATH,
                           ".//div[@class='MuiAvatar-root MuiAvatar-circular css-19hztas']/img").get_attribute("src")

    try:
        bio = pag.find_element(By.XPATH, ".//div[@class='a-section pw-bio']").text.strip()
    except NoSuchElementException:
        bio = None

    # sql = "insert into profile values (%s, %s, %s, %s)"
    # cursor.execute(sql, (link, nome, img, profile_country))
    if coletaProdutos:
        while True:
            pagreviews = pag.find_element(By.XPATH, './/div[@data-testid="me-page-reviews"]')
            reviews = pagreviews.find_elements(By.XPATH, './/div[@data-testid="me-my-reviews"]')
            for review in reviews:
                link_review = review.find_element(By.XPATH, ".//div[@class='MuiBox-root css-1yx24u3']/a").get_attribute(
                    "href")
                auxReview = coletaReview(link_review, dominio)
                lista_reviews = pd.concat([lista_reviews, auxReview], ignore_index=True)

                # driver2 = webdriver.Firefox(options = options)
                # driver2.get(link_review)
                # link_produto = driver2.find_element(By.CSS_SELECTOR, "a[data-hook='product-link']").get_attribute("href")
                # codigo = re.split('/dp/|/ref', link_produto)[1]
                # driver2.close()
                compras = pd.concat([compras, coletaDetalhes(auxReview.link_produto[0], dominio, link_perfil)],
                                    ignore_index=True)
            try:
                pagreviews.find_element(By.XPATH, ".//svg[@data-testid='NavigateNextIcon']").click()
            except NoSuchElementException:
                break

    profile = pd.DataFrame(data=[[nome, img, bio, link_perfil, id_perfil]],
                           columns=['nome', 'img', 'bio', 'link', 'id_profile']).fillna("")
    return profile, lista_reviews, compras


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
                    item.find_element(By.XPATH, ".//div/a[@class='rating-count scroll-to']").get_attribute("title").split(
                        "/")[0])
                ratings_num = int(
                    item.find_element(By.XPATH, ".//div/a[@class='rating-count scroll-to']").get_attribute("title").split(
                        " ")[-2].replace(',', '').replace('.', ''))
            except NoSuchElementException:
                ratings = 0.0
                ratings_num = 0

            # LINK DE CADA PRODUTO
            link = item.find_element('xpath', './/div/a[@class="absolute-link product-link"]').get_attribute("href")

            # LINK DA IMAGEM -> DEPOIS BAIXAR O ARQUIVO
            img = item.find_element('xpath', ".//div[@class='product-image-wrapper']/span/img").get_attribute("src")

                # SALVANDO NO DATAFRAME
            product = pd.concat(
                [product,
                 pd.DataFrame(data=[[dominio, codigo, name, moeda, price, ratings, ratings_num, img, link]],
                              columns=['dominio', 'codigo', 'name', 'moeda', 'price', 'ratings', 'ratings_num',
                                       'img', 'link'])],
                ignore_index=True).fillna("")

            try:
                    ####VERIFICAR VAZIOS
                img = "" if not len(img) else img
                    ####VERIFICAR VAZIOS
                auxSql = [name, codigo, ratings, price, ratings_num, img, link]
                cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(palavra_chave) + "' LIMIT 1;")
                auxSql.extend([aux_site])
                cursor.execute("INSERT INTO produto (nome, codigo, nota, preco, avaliacoes, img, link, site_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE nota = '" + str(ratings) + "', avaliacoes = '" + str(ratings_num) + "';", auxSql)
                mydb.commit()
            except pymysql.Error as e:
                print(e)
                mydb.rollback()

            end = time.time()

            auxDetalhes = pd.DataFrame()
            if not cursor.execute("SELECT iherb_id FROM iherb WHERE produto_id IN (SELECT produto_id FROM produto WHERE codigo = '" + str(codigo) + "');"):
                try:
                    aux_tempo = random.randint(1,30) + 0 if (end-start) >= 120 else 120-(end-start)
                    print("Aguardando " + str(int(aux_tempo)) + "s para coletaDetalhes("+str(codigo)+")")
                    time.sleep(aux_tempo)
                    auxDetalhes = coletaDetalhes(link, dominio)
                    if not auxDetalhes.empty:
                        product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
                        print(link + " Descr ok")
                        auxDetalhes.fillna("", inplace=True)
                        try:
                            auxSql = auxDetalhes.loc[:,
                                     ['tag', 'marca', 'descricao', 'uso', 'ingredientes', 'advertencia',
                                      'aviso', 'tabela']].values.flatten().tolist()
                            cursor.execute(
                                "SELECT produto_id from produto WHERE codigo = '" + str(codigo) + "' LIMIT 1;")
                            aux_produto = cursor.fetchone()["produto_id"]
                            auxSql.extend([aux_produto])
                            cursor.execute(
                                "INSERT INTO iherb (tag, marca, descricao, uso, ingredientes, advertencias, aviso, tabela, produto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                auxSql)
                            mydb.commit()
                        except pymysql.Error as e:
                            print(e)
                            mydb.rollback()
                except:
                    pass

                if cursor.execute("SELECT produto_id FROM iherb WHERE produto_id = '"+str(aux_produto)+"' AND tabela NOT REGEXP 'leitelho|buttermilk';"):
                    try:
                        cursor.execute("UPDATE produto SET observacao = CONCAT_WS('\n', observacao, '- NÃO CONTÉM PALAVRA LEITELHO OU BUTTERMILK NA DESCRIÇÃO'), leitelho = FALSE WHERE produto_id = '" + str(aux_produto) + "';")
                        mydb.commit()
                        print("Produto não contém leitelho nem buttermilk na descrição")
                        continue
                    except pymysql.Error as e:
                        print(e)
                        mydb.rollback()
            start = time.time()

            cursor.execute("SELECT leitelho FROM produto WHERE codigo = '" + str(codigo) + "';")
            if not cursor.fetchone()["leitelho"]:
                continue

            #### ACESSANDO PÁGINA DE AVALIAÇÃO DO PRODUTO (SE HOUVER - SE FOR O CASO DE TER AVALIAÇÃO MAS SEM COMENTÁRIO, VAI SÓ ABRIR E FECHAR)
            if (ratings_num > cursor.execute("SELECT * FROM avaliacao WHERE produto_id = (SELECT produto_id FROM produto WHERE codigo = '" + str(codigo) + "' LIMIT 1);")):
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
                                cursor.execute(
                                    "SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(
                                        palavra_chave) + "' LIMIT 1;")
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
                                    caminho = "results/profile_img/iherb_" + tempAvaliacoes.loc[perfil]["profile_id"] + ".jpeg"
                                    if not os.path.exists(caminho):
                                        try:
                                            urllib.request.urlretrieve(tempAvaliacoes.loc[perfil]["author_img"].replace("/s.", "/l."), caminho)
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


def coletaProdutoNew():
    # INICIANDO DATAFRAMES
    product = pd.DataFrame()
    product_descr = pd.DataFrame()

    # INICIALIZE O DRIVER DO SELENIUM
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Edge()
    driver.get("https://iherb.com/search/?kw=" + palavra_chave)
    cursor.execute("SELECT site_id FROM site WHERE nome = 'iherb' AND palavra_chave = '" + str(palavra_chave) + "';")
    aux_site = cursor.fetchone()["site_id"]

    while True:
        time.sleep(2)
        # CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
        items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, './/div[@class="product-cell-container col-xs-12 col-sm-12 col-md-8 col-lg-6"]')))

        while len(items):
            item = items.pop(0)
            name = item.find_element(By.CLASS_NAME, 'product-title').text.strip()
            codigo = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute(
                "data-product-id")
            link = item.find_element('xpath', './/div/a[@class="absolute-link product-link"]').get_attribute("href")
            img = item.find_element('xpath', ".//div[@class='product-image-wrapper']/span/img").get_attribute("src")
            product = pd.concat([product, pd.DataFrame([[name, codigo, link, img]],
                                                       columns=["name", "codigo", "link", "img"])],
                                ignore_index=True)
        for i in range(len(product)):
            auxDetalhes = pd.DataFrame()
            if not cursor.execute(
                    "SELECT a.iherb_id FROM iherb AS a LEFT JOIN produto AS p ON p.produto_id = a.produto_id AND p.codigo = '" + str(
                            product["codigo"][i]) + "';"
                    ):
                try:
                    time.sleep(120)
                    print(link)
                    auxDetalhes = coletaDetalhes(link, dominio)
                    if not auxDetalhes.empty:
                        product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
                        cursor.execute("SELECT produto_id FROM produto WHERE codigo = '" + str(product["codigo"][i]) + "';")

                        auxDetalhes.values.tolist()
                except:
                    pass

            # #### IR PRA PRÓXIMA PÁGINA (SE HOUVER)
            # try:
            #     driver.find_element('xpath', ".//a[contains(@class, 'pagination-next')]").click()
            # except NoSuchElementException:
            #     break

        # for i in range(len(product)):
        #     auxDetalhes = pd.DataFrame()
        #     if not cursor.execute("SELECT a.iherb_id FROM iherb AS a LEFT JOIN produto AS p ON p.produto_id = a.produto_id AND p.codigo = '" + str(codigo) + "';"
        #     ):
        #         try:
        #             time.sleep(120)
        #             print(product["link"][i])
        #             auxDetalhes = coletaDetalhes(product["link"][i], dominio)
        #             if not auxDetalhes.empty:
        #                 product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)
        #                 cursor.execute("SELECT produto_id FROM produto WHERE codigo = '%s';", product["codigo"][i])
        #
        #
        #                 print("ok")
        #         except:
        #             pass

palavra_chave = "buttermilk"

#### .com.br, .com, .co.uk, .ca, .de (buttermilch), .fr (lait ribot), .com.mx, .it, .es (mazada, suero de mantequilla), .co.jp, .sg, .ae, .com.au, .in, .nl, .sa, .com.tu, .se, .pl, .com.be, .eg, .at,
dominio = ".com"

# coletaElemento(palavra_chave, dominio)

# coletaReview("B07HM62FL3")

# coletaDetalhes('B09ZMTBTSV')
