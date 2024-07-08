import locale
import time
from datetime import date
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

import urllib.request
import requests

import re

locale.setlocale(locale.LC_ALL, 'pt_BR')

# Define the proxy server
# global PROXY
# PROXY = "50.207.199.80:80"

# Set ChromeOptions()
global options
options = webdriver.FirefoxOptions()

# Add the proxy as argument
# options.add_argument("--proxy-server=%s" % PROXY)

# INICIANDO CONEXÃO COM O BANCO DE DADOS
global mydb, cursor
mydb = pymysql.connect(host="localhost", database='scraping2', user="root", passwd="", port = 3307,
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()
mydb.rollback()

global opener
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'MyApp/1.0')]
urllib.request.install_opener(opener)


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
#
# def coletaReview(link_review, dominio):
#     driver = webdriver.Firefox(options=options)
#
#     driver.get(link_review)
#     try:
#         driver.find_element(By.ID, "sp-cc-rejectall-link").click()
#     except NoSuchElementException:
#         pass
#
#     link_produto = driver.find_element(By.CSS_SELECTOR, "a[data-hook='product-link']").get_attribute("href")
#     asin = re.split('/dp/|/ref', link_produto)[1]
#
#     # print(" - Reviews: " + asin)
#
#     # INICIANDO LISTA PARA ARMAZENAR
#     product_review = []
#
#     # PEGANDO CADA CARD DE AVALIAÇÃO
#     while True:
#         # time.sleep(3)
#         # coletaDetalhes(link, dominio)
#         # # PEGANDO CADA CARD DE AVALIAÇÃO
#         # review_elements = driver.find_elements(By.CSS_SELECTOR, '[id*=review-card]')
#         try:
#             review_element = WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.ID, "cm_cr-review_list")))
#         except:
#             break
#
#         # EXTRAINDO NOME DO AUTOR
#         author_name = review_element.find_element(By.CLASS_NAME, 'a-profile-name').text.strip()
#
#         # EXTRAIR TÍTULO AVALIAÇÃO
#         review_title = review_element.find_element(By.CLASS_NAME, 'review-title-content').text.strip()
#
#         # EXTRAINDO TEXTO AVALIAÇÃO
#         review_text = review_element.find_element(By.CLASS_NAME, 'review-text').text.strip()
#
#         # EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
#         review_star = float(
#             review_element.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent").split()[0].replace(
#                 ',', '.'))
#
#         # EXTRAINDO DATA AVALIAÇÃO
#         # review_date = ' '.join(review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[-5:])
#         # review_date = datetime.strptime(review_date, "%d de %B de %Y").strftime("%Y/%m/%d")
#         review_date = review_element.find_element(By.CLASS_NAME, 'review-date').text.strip()
#
#         # EXTRAINDO PAÍS AVALIAÇÃO
#         review_country = review_element.find_element(By.CLASS_NAME, 'review-date').text.split()  ##arrumar
#
#         # EXTRAINDO LINK E IMAGEM DO PERFIL PARA COLETA SEGUINTE
#         try:
#             profile_link = review_element.find_element(By.CLASS_NAME, 'a-profile').get_attribute("href")
#             profile_id = profile_link.split('.')[-1].split('/')[0]
#             profile_img = review_element.find_element(By.XPATH, ".//div/div/img[@class='']").get_attribute("src")
#             author_img = re.sub(r"SX.*_", "", profile_img)
#             # SALVANDO A IMG PRA NÃO DEPENDER DE INTERNET PRO PROCESSAMENTO DA MESMA
#             if "default._" not in profile_img:
#                 urllib.request.urlretrieve(author_img,
#                                            "results/profile_img/amazon" + dominio + "_" + profile_id + ".png")
#             # profiles = pd.concat([profiles, coletaPerfil(profile_link, review_country)], ignore_index=True)
#         except NoSuchElementException:
#             profile_link, profile_id, author_img = None, None, None
#
#         try:
#             review_img = review_element.find_element(By.XPATH, './/img[@class="review-image-tile"]').get_attribute(
#                 "src")
#         except NoSuchElementException:
#             review_img = None
#
#         # if profile_link:
#         #     coletaPerfil(profile_link, review_country)
#
#         product_review.append(
#             (dominio, review_title, review_text, review_img, review_star, author_name, author_img, review_date,
#              review_country, link_review, profile_link, profile_id, link_produto, asin))
#         break
#         # print("ASIN: ", asin)
#         # print("Title: ", review_title)
#         # print("Review: ", review_text)
#         # print("Stars: ", review_star)
#         # print("Author: ", author_name)
#         # print("Review Date: ", review_date)
#         # print("\n")
#
#     # PASSAR PRA PRÓXIMA PAG
#     # try:
#     #     driver.find_element(By.CLASS_NAME, 'a-pagination').find_element(By.CLASS_NAME, "a-last").click()
#     # except NoSuchElementException:
#     #     break
#     # try:
#     #     driver.find_element(By.CLASS_NAME, "a-disabled a-last")
#     # except NoSuchElementException:
#     #     break
#
#     driver.close()
#
#     # ENVIANDO PARA O BANCO DE DADOS
#     # try:
#     #     sql = 'insert into teste.tbl_avaliacoes (dominio, asin, titulo, texto, nota, autor, date, pais, helpful_votes, link_avaliacao, link_perfil, id_perfil) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
#     #     cursor.executemany(sql, product_review)
#     #     print(f"Avaliações do produto {asin} inseridas")
#     #     mydb.commit()
#     # except pymysql.Error as e:
#     #     mydb.rollback()
#     #     print(e)
#
#     # SALVANDO AS LISTAS EM DF
#     review = pd.DataFrame(data=product_review,
#                           columns=['dominio', 'title', 'text', 'img', 'star', 'user', 'user_img', 'date', 'country',
#                                    'link_avaliacao',
#                                    'link_perfil', 'id_perfil', 'link_produto', 'asin'])
#
#     return review  # , profiles
#
# def coletaReviewAux(asin, dominio):
#     driver = webdriver.Firefox(options=options)
#     numPag = 1
#
#     # PÁGINA DAS AVALIAÇÕES DO PRODUTO
#     link_reviews = 'https://www.amazon' + dominio + '/product-reviews/' + asin + '?pageNumber='
#     driver.get(link_reviews + str(numPag))
#     try:
#         driver.find_element(By.ID, "sp-cc-acceptall-link").click()
#     except NoSuchElementException:
#         pass
#
#     # INICIANDO LISTA PARA ARMAZENAR
#     review_links = []
#
#     # PEGANDO CADA CARD DE AVALIAÇÃO
#     while True:
#         # time.sleep(3)
#         #
#         # # PEGANDO CADA CARD DE AVALIAÇÃO
#         # review_elements = driver.find_elements(By.CSS_SELECTOR, '[id*=review-card]')
#         try:
#             pag = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'cm_cr-review_list')))
#             review_elements = WebDriverWait(pag, 10).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[id*=review-card]')))
#         except:
#             break
#         # if not review_elements:
#         #     break
#         for review_element in review_elements:
#             # EXTRAINDO LINK DA POSTAGEM
#             review_link = review_element.find_element(By.CLASS_NAME, 'review-title-content').get_attribute("href")
#             if review_link:
#                 review_links.append(review_link)
#         numPag += 1
#         driver.get(link_reviews + str(numPag))
#         # try:
#         #     WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, ".//div[@id='cm_cr-pagination_bar']/ul/li[@class='a-last']"))).click()
#         # except:
#         #     break
#
#     driver.close()
#
#     # ENVIANDO PARA O BANCO DE DADOS
#     # try:
#     #     sql = 'insert into teste.tbl_avaliacoes (dominio, asin, titulo, texto, nota, autor, date, pais, helpful_votes, link_avaliacao, link_perfil, id_perfil) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
#     #     cursor.executemany(sql, product_review)
#     #     print(f"Avaliações do produto {asin} inseridas")
#     #     mydb.commit()
#     # except pymysql.Error as e:
#     #     mydb.rollback()
#     #     print(e)
#
#     review = pd.DataFrame()
#     for link in review_links:
#         review = pd.concat([review, coletaReview(link, dominio)], ignore_index=True)
#
#     return review  # , profiles


def coletaReviewNew(data_asin, dominio):
    # options.headless = True
    numPag = 1

    #### PÁGINA DAS AVALIAÇÕES DO PRODUTO
    link_reviews = 'https://www.amazon' + dominio + '/product-reviews/' + data_asin + '?pageNumber='

    driver2 = webdriver.Firefox(options=options)
    driver2.get(link_reviews + str(numPag))

    try:
        driver2.find_element(By.ID, "sp-cc-acceptall-link").click()
    except NoSuchElementException:
        pass

    # INICIANDO LISTA PARA ARMAZENAR
    product_review = []
    link_produto = driver2.find_element(By.XPATH, ".//a[@data-hook='product-link']").get_attribute("href")
    codigo = data_asin

    # time.sleep(3)

    #### PEGANDO CADA CARD DE AVALIAÇÃO
    while True:
        #### TENTANDO CONTORNAR StaleElementReferenceException
        try:
            WebDriverWait(driver2, 3).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@class='a-section a-spacing-none reviews-content a-size-base']")))
        except:
            break

        # # PEGANDO CADA CARD DE AVALIAÇÃO

        i, j = 0, 0

        try:
            # pag = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="MuiBox-root css-i9gxme"]')))
            review_elements = WebDriverWait(driver2, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, './/div[@class="a-section review aok-relative"]')))
        except:
            break

        while i < len(review_elements):
            try:
                review_element = WebDriverWait(driver2, 3).until(
                    EC.presence_of_all_elements_located((By.XPATH, './/div[@class="a-section review aok-relative"]')))[i]

                review_id = review_element.get_attribute("id")

                #### VERIFICA SE O COMENTÁRIO JÁ EXISTE NO BANCO
                if cursor.execute("SELECT * FROM avaliacao where codigo_avaliacao = '" + str(review_id) + "';") > 0:
                    #### SE SIM, VAI PRO PRÓXIMO
                    i += 1
                    continue

                # EXTRAINDO LINK DA POSTAGEM
                review_link = review_element.find_element(By.XPATH, './/*[@data-hook="review-title"]').get_attribute("href")

                # EXTRAIR NOME AUTOR/USUÁRIO
                author_name = review_element.find_element(By.XPATH, './/span[@class="a-profile-name"]').text.strip()

                # EXTRAIR TÍTULO AVALIAÇÃO
                review_title = review_element.find_element(By.XPATH, './/*[@data-hook="review-title"]').text.strip()

                # EXTRAINDO TEXTO AVALIAÇÃO
                review_text = review_element.find_element(By.XPATH, './/span[@data-hook="review-body"]').text.strip()

                # EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
                review_star = float(review_element.find_element(By.XPATH, ".//span[@class='a-icon-alt']").get_attribute("textContent").split()[0].replace(',', '.'))

                # EXTRAINDO DATA AVALIAÇÃO
                # review_date = ' '.join(review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[-5:])
                # review_date = datetime.strptime(review_date, "%d de %B de %Y").strftime("%Y/%m/%d")
                review_date = review_element.find_element(By.XPATH, './/span[@data-hook="review-date"]').text.strip()

                # EXTRAINDO PAÍS AVALIAÇÃO
                # review_country = review_element.find_element(By.CLASS_NAME, 'review-date').text.strip  ##arrumar

                # EXTRAINDO LINK E IMAGEM DO PERFIL PARA COLETA SEGUINTE
                try:
                    profile_link = review_element.find_element(By.XPATH, './/a[@class="a-profile"]').get_attribute("href")
                    profile_id = profile_link.split('/')[5]
                    ## VERIFICANDO SE É IMG PADRÃO / SEM IMG
                    if "default" in review_element.find_element(By.XPATH, ".//div[@class='a-profile-avatar']/img").get_attribute("src"):
                        profile_img = author_img = ""
                    else:

                        profile_img = review_element.find_element(By.XPATH, ".//div[@class='a-profile-avatar']/img[@class='']").get_attribute("src")
                        author_img = re.sub("SX48_", "", profile_img)
                        # urllib.request.urlretrieve(author_img,
                        #                            "results/profile_img/amazon" + dominio + "_" + profile_id + ".jpeg")

                    # profiles = pd.concat([profiles, coletaPerfil(profile_link, review_country)], ignore_index=True)
                except NoSuchElementException:
                    profile_link, profile_id, author_img = None, None, None

                try:
                    review_img = review_element.find_element(By.XPATH,'.//img[@class="review-image-tile"]').get_attribute("src")
                    review_img = re.sub("._SY88", "", review_img)
                except NoSuchElementException:
                    review_img = ""

                product_review.append(
                    (dominio, review_link, review_title, review_text, review_star, review_img, author_name, author_img, review_date,
                     link_reviews, profile_link, profile_id, link_produto, codigo, review_id))

            except StaleElementReferenceException:
                j += 1
                print(str(len(product_review) - 1) + " " + str(j))

            i+=1

        numPag += 1
        driver2.get(link_reviews + str(numPag))

    driver2.close()

    print(link_reviews, len(product_review))

    return pd.DataFrame(data=product_review,
                        columns=["dominio", "review_link", "review_title", "review_text", "review_star", "review_img",
                                 "author_name", "author_img", "review_date", "link_reviews", "profile_link", "profile_id", "link_produto", "codigo_produto", "codigo_avaliacao"]).fillna("")


def coletaDetalhes(url, dominio, review=False):
    driver = webdriver.Firefox(options=options)
    # url = "https://www.amazon"+dominio+"/dp/"+asin
    driver.get(url)

    asin = re.split("/dp/", url)[1].split('/')[0]
    if review:
        print(" - Review - Detalhe: " + asin)
    else:
        print("Detalhe: " + asin)

    try:
        pag = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'dp-container')))
    except:
        print("Verificar  " + url)
        driver.close()
        return pd.DataFrame()

    try:
        driver.find_element(By.ID, "sp-cc-all-link").click()
    except NoSuchElementException:
        pass

    nome = pag.find_element(By.ID, 'productTitle').text.strip()

    try:
        marca = pag.find_element(By.ID, 'BylineInfo').text.strip()
    except NoSuchElementException:
        try:
            marca = pag.find_element(By.ID, 'bylineInfo_feature_div').text.strip()
        except NoSuchElementException:
            marca = None

    try:
        price = pag.find_element(By.XPATH,
                                 ".//span[@class='a-price a-text-price a-size-medium apexPriceToPay']").text.strip()
        moeda = price
    except NoSuchElementException:
        moeda, price = 0.0, None

    try:
        overview = pag.find_element(By.ID, 'productOverview_feature_div').text.strip()
    except NoSuchElementException:
        overview = None

    try:
        features = pag.find_element(By.ID, 'featurebullets_feature_div').text.strip()
    except NoSuchElementException:
        try:
            features = pag.find_element(By.ID, 'productFactsDesktop_feature_div').text.strip()
        except NoSuchElementException:
            features = None

    try:
        details = pag.find_element(By.ID, 'productDetails_feature_div').text.strip()
    except NoSuchElementException:
        try:
            details = pag.find_element(By.ID, 'detailBulletsWrapper_feature_div').text.strip()
        except NoSuchElementException:
            details = None
    try:
        description = pag.find_element(By.ID, 'productDescription_feature_div').text.strip()
    except NoSuchElementException:
        try:
            description = pag.find_element(By.ID, 'bookDescription_feature_div').text.strip()
        except NoSuchElementException:
            description = None

    try:
        information = pag.find_element(By.ID, 'importantInformation_feature_div').text.strip()
    except NoSuchElementException:
        information = None

    try:
        documents = pag.find_element(By.ID, 'productDocuments_feature_div').text.strip()
    except NoSuchElementException:
        documents = None

    try:
        tag = driver.find_element(By.XPATH, './/a[@class="nav-a nav-b"]').text.strip()
    except NoSuchElementException:
        try:
            tag = driver.find_element(By.XPATH, './/ul/li[1]/span/a').text.strip()
        except NoSuchElementException:
            tag = None

    driver.close()

    return pd.DataFrame(data=[
        [dominio, asin, nome, marca, moeda, price, tag, overview, features, details, description, information,
         documents,
         review]],
        columns=['dominio', 'asin', 'nome', 'marca', 'moeda', 'price', 'tag', 'overview', 'features',
                 'details', 'description', 'information', 'documents', 'review'])

def coletaPerfil(link_perfil, dominio, coletaProdutos=False):
    driver2 = webdriver.Firefox(options=options)
    driver2.get(link_perfil)
    try:
        driver2.find_element(By.ID, "sp-cc-accepttall-link").click()
    except NoSuchElementException:
        pass

    while True:
        try:
            pag = WebDriverWait(driver2, 3).until(EC.visibility_of_element_located((By.ID, "profile_v5")))
        except:
            driver2.close()
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        compras = pd.DataFrame()
        lista_reviews = pd.DataFrame()
        id_perfil = link_perfil.split('.account.')[1].split('/ref')[0]

        nome = pag.find_element(By.ID, "customer-profile-name-header").text.strip()
        imgAux = pag.find_element(By.XPATH, ".//img[@id='avatar-image']").get_attribute("src")

        try:
            bio = pag.find_element(By.XPATH, ".//div[@class='a-section pw-bio']").text.strip()
        except NoSuchElementException:
            bio = None

        if coletaProdutos:
            reviews = pag.find_elements(By.XPATH, './/a[@class="a-link-normal your-content-card"]')
            driver3 = webdriver.Firefox()
            for review in reviews:

                # link_review = review.get_attribute("href")
                # auxReview = coletaReview(link_review, dominio)
                # lista_reviews = pd.concat([lista_reviews, auxReview], ignore_index=True)
                #
                # # driver2 = webdriver.Firefox(options = options)
                # # driver2.get(link_review)
                # # link_produto = driver2.find_element(By.CSS_SELECTOR, "a[data-hook='product-link']").get_attribute("href")
                # # asin = re.split('/dp/|/ref', link_produto)[1]
                # # driver2.close()

                link_review = review.get_attribute("href")
                driver3.get(link_review)
                link_produto = driver3.find_element(By.XPATH, ".//a[@data-hook='product-link']").get_attribute("href")

                compras = pd.concat([compras, coletaDetalhes(link_produto, dominio, link_perfil)],
                                    ignore_index=True)

        driver2.close()
        profile = pd.DataFrame(data=[[nome, "", bio, link_perfil, id_perfil]],
                               columns=['nome', 'img', 'bio', 'link', 'id_profile'])
        return profile, lista_reviews, compras


def coletaElemento(palavra_chave, dominio):
    today = date.today().strftime("%Y%m%d")

    # INICIALIZE O DRIVER DO SELENIUM

    driver = webdriver.Firefox(options=options)

    # LOGANDO PARA PODER ACESSAR PÁGINA DE QUEM AVALIOU O PRODUTO
    # login = input("Login")
    # senha = input("Senha")
    # driver.get('https://www.amazon'+dominio+'/login')
    # driver.find_element(By.ID, 'ap_email').send_keys(login)
    # driver.find_element(By.ID, 'continue').click()
    # driver.find_element(By.ID, 'ap_email').send_keys(senha)
    # driver.find_element(By.NAME, 'rememberMe').click()
    # driver.find_element(By.ID, 'signInSubmit').click()

    url = 'https://www.amazon' + dominio + '/s?k=' + palavra_chave + "&dc="
    # url = 'https://www.amazon.com.br/'

    driver.get(url)
    try:
        driver.find_element(By.ID, "sp-cc-acceptall-link").click()
    except NoSuchElementException:
        pass

    # # create WebElement for a search box
    # search_box = driver.find_element(By.ID, 'twotabsearchtextbox')  # type the keyword in searchbox
    # search_box.send_keys(palavra_chave)
    #
    # # create WebElement for a search button
    # search_button = driver.find_element(By.ID, 'nav-search-submit-button')  # click search_button
    # search_button.click()

    #### INICIANDO DATAFRAMES
    product = pd.DataFrame()
    product_descr = pd.DataFrame()
    avaliacoes = pd.DataFrame()
    profiles = pd.DataFrame()

    while True:
        #### CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
        items = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, './/div[contains(@class, "s-result-item s-asin")]')))

        while len(items):
            item = items.pop(0)

            data_asin = item.get_attribute("data-asin")

            name = item.find_element('xpath', './/span[@class="a-size-base-plus a-color-base a-text-normal"]').text

            #### VERIFICA SE É PAG DE MÚSICA
            try:
                "mp3" in item.find_element('xpath',
                                           ".//a[@class='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-bold']").text.strip()
                name = name + " (AMAZON MUSIC)"
                continue
            except NoSuchElementException:
                pass

            try:
                item.find_element('class name', "puis-label-popover-default")
                name = name + " (PROPAGANDA)"
                continue
            except NoSuchElementException:
                pass

            try:
                item.find_element('class name', "puis-label-popover puis-sponsored-label-text")
                name = name + " (PROPAGANDA)"
                continue
            except NoSuchElementException:
                pass

            #### DESMEMBRANDO PREÇO (INCLUIR MOEDA TBM?)
            moeda = item.find_elements('xpath', './/span[@class="a-price-symbol"]')
            moeda = moeda[0] if moeda else None
            whole_price = item.find_elements('xpath', './/span[@class="a-price-whole"]')
            fraction_price = item.find_elements('xpath', './/span[@class="a-price-fraction"]')
            if whole_price and fraction_price:
                price = float('.'.join([whole_price[0].text.replace('.', '').replace(',', ''), fraction_price[0].text]))
            else:
                price = 0.0
            # price = None

            #### DESMEMBRANDO A AVALIAÇÃO - MANTENDO NA PÁG DE RESULTS PRA EVITAR UM LOOP COM A COLETA DE DETALHES VINDA DA PÁGINA DO USUÁRIO
            ratings_box = item.find_elements('xpath', './/div[@class="a-row a-size-small"]/span')
            if ratings_box:
                #### ADAPTA OS PONTOS E VIRGULAS NOS NÚMEROS
                ratings = locale.atof(ratings_box[0].get_attribute('aria-label').split()[0])
                ratings_num = locale.atoi(ratings_box[1].text.replace(',', '').replace('.', ''))
            else:
                ratings, ratings_num = 0.0, 0

            if (ratings >= 10):  #### CORRIGINDO POSSÍVEIS PROBLEMSA DE CONVERSÃO DE DECIMAIS
                ratings = ratings / 10

            #### LINK DE CADA PRODUTO
            link = item.find_element('xpath', './/a[@class="a-link-normal s-no-outline"]').get_attribute("href")

            #### LINK DA IMAGEM -> DEPOIS BAIXAR O ARQUIVO
            img = item.find_element('class name', "s-image").get_attribute("src")

            if not cursor.execute("SELECT a.produto_id, p.codigo FROM amazon AS a LEFT JOIN produto AS p ON p.codigo = '" + str(data_asin) + "';"):
                auxDetalhes = coletaDetalhes(link, dominio)
                if not auxDetalhes.empty:
                    product_descr = pd.concat([product_descr, auxDetalhes], ignore_index=True)

            #### VERIFICA SE O MESMO PRODUTO TEVE INCLUSÃO DE ANÁLISES
            # cursor.execute("SELECT avaliacoes FROM produto WHERE codigo = '" + str(data_asin) + "';")
            # comparaSql = cursor.fetchall()
            # if len(comparaSql) and ratings_num > 0:
            #     if ratings_num > comparaSql[-1]["avaliacoes"]:
            if ratings_num > cursor.execute(
                    "SELECT * FROM avaliacao WHERE produto_id = (SELECT produto_id FROM produto WHERE codigo = '" + str(
                            data_asin) + "' LIMIT 1);"):
                tempAvaliacoes = coletaReviewNew(data_asin, dominio)
                if not tempAvaliacoes.empty:
                    avaliacoes = pd.concat([avaliacoes, tempAvaliacoes], ignore_index=True)
                    # for link_perfil in tempAvaliacoes.link_perfil:
                    #     tempPerfil, tempReview, tempCompras = coletaPerfil(link_perfil, dominio, False)
                    #     if not tempPerfil.empty:
                    #         profiles = pd.concat([profiles, tempPerfil], ignore_index=True)
                    #     if not tempReview.empty:
                    #         avaliacoes = pd.concat([avaliacoes, tempReview], ignore_index=True)
                    #     if not tempCompras.empty:
                    #         product_descr = pd.concat([product_descr, tempCompras], ignore_index=True)

            # SALVANDO NO DATAFRAME
            product = pd.concat(
                [product, pd.DataFrame(data=[[dominio, data_asin, name, moeda, price, ratings, ratings_num, img, link]],
                                       columns=['dominio', 'asin', 'name', 'moeda', 'price', 'ratings', 'ratings_num',
                                                'img', 'link'])],
                ignore_index=True)

            # profiles = pd.concat([profiles, tempAvaliacoes[["author_name", "author_img", "profile_id", "profile_link", "review_date"]].drop_duplicates()], ignore_index=True)

            try:
                ####VERIFICAR VAZIOS
                img = "" if not len(img) else img
                auxSql = [name, data_asin, ratings, price, ratings_num, img, link]
                cursor.execute("INSERT INTO produto (nome, codigo, nota, preco, avaliacoes, img, link, site_id) VALUES (%s, %s, %s, %s, %s, %s, %s, (SELECT site_id FROM site WHERE nome = 'amazon' AND dominio = '" + str(dominio) + "' AND palavra_chave = '" + str(palavra_chave) + "' LIMIT 1)) ON DUPLICATE KEY UPDATE nota = '" + str(ratings) + "', avaliacoes = '" + str(ratings_num) + "';", auxSql)
                cursor.fetchone()

                if 'auxDetalhes' in locals():
                    if not auxDetalhes.empty:
                        auxDetalhes.fillna("", inplace = True)
                        auxSql = auxDetalhes.loc[:,['tag', 'marca', 'overview', 'features', 'details', 'description', 'information', 'documents']].values.flatten().tolist()

                    cursor.execute("INSERT INTO amazon (tag, marca, overview, features, details, description, information, documents, produto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, (SELECT produto_id FROM produto WHERE codigo = '" + str(data_asin) + "' LIMIT 1));", auxSql)
                    cursor.fetchone()

                if 'tempAvaliacoes' in locals():
                    if not tempAvaliacoes.empty:

                        for perfil in range(len(tempAvaliacoes)):
                            if not cursor.execute("SELECT * FROM usuario WHERE codigo_perfil = '" + str(tempAvaliacoes.loc[perfil]["profile_id"]) + "';"):
                                auxSql = tempAvaliacoes.loc[perfil][["author_name", "author_img", "profile_id", "profile_link"]]
                                cursor.execute("INSERT INTO usuario (nome, img, codigo_perfil, link,  site_id) VALUES (%s, %s, %s, %s, (SELECT site_id FROM site WHERE nome = 'amazon' AND dominio = '" + str(
                                        dominio) + "' LIMIT 1)) ON DUPLICATE KEY UPDATE img = '" + str(auxSql["author_img"]) + "';", auxSql.to_list())
                                cursor.fetchone()
                                profiles = pd.concat([profiles, auxSql.to_frame().T], ignore_index=True)

                        tempAvaliacoes.fillna("", inplace = True)
                        auxSql = tempAvaliacoes.loc[:,[
                            "review_title", "review_text", "review_star", "review_img", "author_name", "review_date", "review_date",
                             "review_link", "codigo_avaliacao", "profile_id"]].values.tolist()
                        cursor.executemany('INSERT INTO avaliacao (titulo, texto, nota, img, autor, pais, dataavaliacao, link_avaliacao, codigo_avaliacao, produto_id, usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (SELECT produto_id FROM produto WHERE codigo = "' + str(data_asin) + '" LIMIT 1), (SELECT usuario_id FROM usuario WHERE codigo_perfil = " %s " LIMIT 1));', auxSql)

                        cursor.fetchall()

                mydb.commit()

            except pymysql.Error as e:
                print(e)
                mydb.rollback()


        # for i in product_asin:
        #    coletaReview(i)

        # IR PRA PRÓXIMA PÁGINA (SE HOUVER)
        try:
            driver.find_element('xpath', ".//a[contains(@class, 's-pagination-next')]").click()
        except NoSuchElementException:
            break
        # paginacao.find_element(By.CLASS_NAME, "s-pagination-next").click()

    #### SALVANDO TUDO NO BANCO DE DADOS
    cursor.close()
    mydb.close()
    driver.close()

    # Salvando os dataframes em arquivos csv -> 'amazon' + pais + palavra_chave
    # final.to_csv('results/amazon'+dominio+'_'+palavra_chave+'_(produtos)_'+today+'.csv', index=False)
    print("Exportando para excel")
    product.to_excel('results/amazon' + dominio + '_' + palavra_chave + '_(produtos)_' + today + '.xlsx', index=False)
    product_descr.to_excel('results/amazon' + dominio + '_' + palavra_chave + '_(detalhes)_' + today + '.xlsx',
                           index=False)
    avaliacoes.to_excel('results/amazon' + dominio + '_' + palavra_chave + '_(avaliacoes)_' + today + '.xlsx',
                        index=False)
    profiles.to_excel('results/amazon' + dominio + '_' + palavra_chave + '_(perfis)_' + today + '.xlsx', index=False)

    #### SALVANDO AS IMG DE PERFIL
    print("Salvando imagens de perfil:")
    for row in range(len(profiles)):
        print("row "+str(row)+"/"+str(len(profiles)-1))
        if "" != profiles.loc[row]["author_img"] and not "grey-pixel" in profiles.loc[row]["author_img"]:
            urllib.request.urlretrieve(profiles.loc[row]["author_img"],
                                       "results/profile_img/amazon_" + profiles.loc[row]["profile_id"] + ".jpeg")
            # response = requests.get(profiles.loc[row]["author_img"])
            # nome_img = "results/profile_img/amazon_" + profiles.loc[row]["profile_id"] + ".jpeg"
            # # Verificar se a requisição foi bem-sucedida
            # if response.status_code == 200:
            #     # Abrir um arquivo em modo de escrita binária
            #     with open(nome_img, 'wb') as file:
            #         # Escrever o conteúdo da resposta no arquivo
            #         for chunk in response.iter_content(1024):
            #             file.write(chunk)
            # else:
            #     print(f'Falha ao baixar a imagem. Status code: {response.status_code}')
        else:
            print(profiles.loc[row]["profile_link"])
    #
    # cursor.close()
    # mydb.close()

    return product, product_descr, avaliacoes, profiles


palavra_chave = "buttermilk"

#### .com.br, .com, .co.uk, .ca, .de (buttermilch), .fr (lait ribot), .com.mx, .it, .es (mazada, suero de mantequilla), .co.jp, .sg, .ae, .com.au, .in, .nl, .sa, .com.tu, .se, .pl, .com.be, .eg, .at,
dominio = ".com"

mydb = pymysql.connect(host="localhost", database='scraping2', user="root", passwd="", port = 3307,
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()

# coletaElemento(palavra_chave, dominio)

# coletaReview("B07HM62FL3")

product, product_descr, avaliacoes, profiles = coletaElemento(palavra_chave, dominio)

from transformers import MarianMTModel, MarianTokenizer

src_reviews = ['>>pt<<' + str(r) for r in avaliacoes.text.tolist()]
model_name = 'Helsinki-NLP/opus-mt-en-ROMANCE'
tokenizer = MarianTokenizer.from_pretrained(model_name)
print(tokenizer.supported_language_codes)
model = MarianMTModel.from_pretrained(model_name)
translated = model.generate(**tokenizer.prepare_seq2seq_batch(src_reviews, return_tensors='pt'))
tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]

# coletaReview("B07HM62FL3")

# coletaDetalhes('B09ZMTBTSV')


# from deepface import DeepFace
#
# def pegaImagem(url):
#     headOption = webdriver.FirefoxOptions()
#     headOption.add_argument("--headless")
#     driver = webdriver.Firefox(options = options)
#     driver.get(url)
#     try:
#         img = WebDriverWait(driver, 3).until(
#                         EC.presence_of_all_elements_located((By.XPATH, ".//img")))
#     except:
#         img = "VERIFICAR"
#     driver.close()
#     return img
#
# def processamentoImgs(url):
#     count = 0
#     backends = [
#         'opencv',
#         'ssd',
#         'dlib',
#         'mtcnn',
#         'fastmtcnn',
#         'retinaface',
#         'mediapipe',
#         'yolov8',
#         'yunet',
#         'centerface',
#     ]
#     results = []
#     for i in url:
#         print(count)
#         img = pegaImagem(i)
#         if img == "VERIFICAR":
#             results.append("VERIFICAR")
#         elif "amazon-avatars-global/default._" not in img:
#             results.append(DeepFace.analyze(
#                 img_path=img,
#                 actions=['gender', 'age', 'race', 'emotion'],
#                 enforce_detection=False,
#                 detector_backend=backends[7],
#             ))
#         else:
#             results.append("SEM IMAGEM")
#         count+=1
#
# profiles = pd.read_excel("results/amazon.com_buttermilk_(perfis)_20240522.xlsx")
#
# resultadosImg = processamentoImgs(profiles.img)
