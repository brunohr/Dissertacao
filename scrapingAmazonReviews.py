import time
from datetime import date
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pymysql

# CONVERSÃO DE DECIMAIS (',' para '.')
import locale
locale.setlocale(locale.LC_ALL, '')

# INICIANDO CONEXÃO COM O BANCO DE DADOS
global mydb, cursor
mydb = pymysql.connect(host="localhost", database='teste', user="root", passwd="@Bruno123",
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

def coletaReview(asin, site):
    driver = webdriver.Firefox()

    # PÁGINA DAS AVALIAÇÕES DO PRODUTO
    link_reviews = 'https://www.amazon'+site+'/product-reviews/' + asin
    driver.get(link_reviews)
    try:
        driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    except NoSuchElementException:
        pass

    # product_site = []
    # product_asin = []
    # product_review_text = []
    # product_review_user = []
    # product_review_star = []
    # product_review_date = []
    # product_review_title = []

    # INICIANDO LISTA PARA ARMAZENAR
    product_review = []

    while True:
        time.sleep(3)

        # PEGANDO CADA CARD DE AVALIAÇÃO
        review_elements = driver.find_elements(By.CSS_SELECTOR, '[id*=review-card]')
        for review_element in review_elements:
            # EXTRAINDO NOME DO AUTOR
            author_name = review_element.find_element(By.CLASS_NAME, 'a-profile-name').text.strip()

            # EXTRAIR TÍTULO AVALIAÇÃO
            review_title = review_element.find_element(By.CLASS_NAME, 'review-title-content').text.strip()

            # EXTRAINDO TEXTO AVALIAÇÃO
            review_text = review_element.find_element(By.CLASS_NAME, 'review-text').text.strip()

            # EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
            review_star = locale.atof(review_element.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent").split()[0])

            # EXTRAINDO DATA AVALIAÇÃO (E PAÍS)
            review_date = review_element.find_element(By.CLASS_NAME, 'review-date').text.strip()

            # product_site.append(site)
            # product_asin.append(asin)
            # product_review_title.append(review_title)
            # product_review_text.append(review_text)
            # product_review_star.append(review_star)
            # product_review_user.append(author_name)
            # product_review_date.append(review_date)

            product_review.append((site, asin, review_title, review_text ,review_star, author_name, review_date))

            # print("ASIN: ", asin)
            # print("Title: ", review_title)
            # print("Review: ", review_text)
            # print("Stars: ", review_star)
            # print("Author: ", author_name)
            # print("Review Date: ", review_date)
            # print("\n")

        # PASSAR PRA PRÓXIMA PAG
        try:
            driver.find_element(By.CLASS_NAME, 'a-pagination').find_element(By.CLASS_NAME, "a-last").click()
        except NoSuchElementException:
            break

        try:
            driver.find_element(By.CLASS_NAME, "a-disabled a-last")
        except NoSuchElementException:
            break

    driver.close()

    # ENVIANDO PARA O BANCO DE DADOS
    try:
        sql = 'insert into teste.tbl_avaliacoes (site, asin, titulo, texto, nota, autor, date) values (%s, %s, %s, %s, %s, %s, %s)'
        cursor.executemany(sql, product_review)
    except pymysql.Error as e:
        mydb.rollback()
        print(e)
    finally:
        # cursor.close()
        # mydb.close()
        print(f"Avaliações do produto {asin} inseridas")

    # SALVANDO AS LISTAS EM DF
    return pd.DataFrame(data=product_review,
                        columns=['site', 'asin', 'title', 'text', 'star', 'user', 'data'])

def coletaDetalhes(asin, site):
    driver = webdriver.Firefox()
    url = "https://www.amazon"+site+"/dp/"+asin
    driver.get(url)

    pag = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'dp')))
    try:
        driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    except NoSuchElementException:
        pass

    try:
        marca = pag.find_element(By.ID, 'bylineInfo').text.strip()
    except NoSuchElementException:
        marca = pag.find_element(By.ID, 'bylineInfo_feature_div').text.strip()

    nome = pag.find_element(By.ID, 'productTitle').text.strip()

    try:
        overview = pag.find_element(By.ID, 'productOverview_feature_div').text.strip()
    except NoSuchElementException:
        overview = ""

    try:
        features = pag.find_element(By.ID, 'featurebullets_feature_div').text.strip()
    except NoSuchElementException:
        try:
            features = pag.find_element(By.ID, 'productFactsDesktop_feature_div').text.strip()
        except NoSuchElementException:
            features = ""

    try:
        details = pag.find_element(By.ID, 'productDetails_feature_div').text.strip()
    except NoSuchElementException:
        try:
            details = pag.find_element(By.ID, 'detailBulletsWrapper_feature_div').text.strip()
        except NoSuchElementException:
            details = ""
    try:
        description = pag.find_element(By.ID, 'productDescription_feature_div').text.strip()
    except NoSuchElementException:
        try:
            description = pag.find_element(By.ID, 'bookDescription_feature_div').text.strip()
        except NoSuchElementException:
            description = ""

    try:
        information = pag.find_element(By.ID, 'importantInformation_feature_div').text.strip()
    except NoSuchElementException:
        information = ""

    try:
        documents = pag.find_element(By.ID, 'productDocuments_feature_div').text.strip()
    except NoSuchElementException:
        documents = ""

    try:
        tag = driver.find_element(By.XPATH, './/a[@class="nav-a nav-b"]').text.strip()
    except NoSuchElementException:
        try:
            tag = driver.find_element(By.XPATH, './/ul/li[1]/span/a').text.strip()
        except NoSuchElementException:
            tag = ""
    # detalhes = pd.DataFrame(data=[[asin, overview, features, details]],
    #                     columns=['asin', 'overview', 'features', 'details'])

    # print(detalhes)
    driver.close()

    try:
        sql = 'insert into teste.tbl_detalhes (site, asin, nome, marca, tag, overview, features, details, description, information, documents) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (site, asin, nome, marca, tag, overview, features, details, description, information, documents))
    except pymysql.Error as e:
        mydb.rollback()
        print(e)
    # finally:
    #     # cursor.close()
    #     # mydb.close()
    #     print(f"Detalhes do produto {asin} inseridos")

    return pd.DataFrame(data=[[site, asin, nome, marca, tag, overview, features, details, description, information, documents]],
                       columns=['site', 'asin', 'nome', 'marca', 'tag', 'overview', 'features', 'details', 'description', 'information', 'documents'])

def coletaElemento(palavra_chave, site):
    today = date.today().strftime("%Y%m%d")

    # INICIALIZE O DRIVER DO SELENIUM
    # driver = webdriver.Firefox()
    fp = webdriver.FirefoxOptions()
    fp.set_preference("network.cookie.cookieBehavior", 2)
    driver = webdriver.Firefox(options = fp)

    url = 'https://www.amazon'+site+'/s?k=' + palavra_chave + "&dc="
    # url = 'https://www.amazon.com.br/'

    driver.get(url)
    try:
        driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    except NoSuchElementException:
        pass

    #
    # # create WebElement for a search box
    # search_box = driver.find_element(By.ID, 'twotabsearchtextbox')  # type the keyword in searchbox
    # search_box.send_keys(palavra_chave)
    #
    # # create WebElement for a search button
    # search_button = driver.find_element(By.ID, 'nav-search-submit-button')  # click search_button
    # search_button.click()

    # INICIANDO DATAFRAMES
    product = pd.DataFrame()
    product_descr = pd.DataFrame()
    avaliacoes = pd.DataFrame()

    while True:
        # CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
        items = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))

        for item in items:

            name = item.find_element('xpath', './/span[@class="a-size-base-plus a-color-base a-text-normal"]').text

            try:
                auxpatrocinio = item.find_element(by.class_name, "puis-label-popover-default")
            except nosuchelementexception:
                auxpatrocinio = false

            if auxpatrocinio:
                name = name + " (propaganda)"

            data_asin = item.get_attribute("data-asin")

            # DESMEMBRANDO PREÇO (INCLUIR SÍMBOLO TBM?)
            whole_price = item.find_elements(by.xpath, './/span[@class="a-price-whole"]')
            fraction_price = item.find_elements(by.xpath,'.//span[@class="a-price-fraction"]')
            if whole_price and fraction_price:
                price = ','.join([whole_price[0].text, fraction_price[0].text])
            else:
                price = 0
            price = locale.atof(price)

            # DESMEMBRANDO A AVALIAÇÃO
            ratings_box = item.find_elements('xpath', './/div[@class="a-row a-size-small"]/span')
            if ratings_box:
                ratings = locale.atof(ratings_box[0].get_attribute('aria-label').split()[0])
                ratings_num = ratings_box[1].get_attribute('aria-label')
            else:
                ratings, ratings_num = 0.0, 0

            # LINK DE CADA PRODUTO
            link = item.find_element('xpath', './/a[@class="a-link-normal s-no-outline"]').get_attribute("href")

            # LINK DA IMAGEM -> DEPOIS BAIXAR O ARQUIVO
            img = item.find_element(by.class_name, "s-image").get_attribute("src")

            # print the extracted information
            # print("nome produto: ", name.text)
            # print("asin: ", data_asin)
            # print("preço: ", price)
            # print("nota: ", ratings)
            # print("num de avaliações: ", ratings_num)
            # print("link: ", link)
            # print("imagem: ", img)
            # print("\n")

            try:
                auxmusica = "mp3" in item.find_element(by.xpath, ".//a[@class='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-bold']").text.strip()
            except nosuchelementexception:
                auxmusica = false
            if auxmusica:
                name = name + " (amazon music)"
            else:
                product_descr = pd.concat([product_descr, coletadetalhes(data_asin, site)], ignore_index=true)

            # pegando avaliações dos produtos que possuem avaliação
            if ratings_num != 0 and ratings_num != "none": #### trocar pra pegar avalições com análise (como checar?) , esse aqui verifica só a qtde notas
                avaliacoes = pd.concat([avaliacoes, coletareview(data_asin, site)], ignore_index=true)
                # print("ok")
            # else:
            #     print("sem avaliações\n")

            # salvando as listas em df -> depois otimizar pra já salvar direto em df
            product = pd.concat(
                [product, pd.dataframe(data=[[site, data_asin, name, price, ratings, ratings_num, img, link]],
                                       columns=['site', 'asin', 'name', 'price', 'ratings', 'ratings_num', 'img', 'link'])],
                ignore_index=true)
        # for i in product_asin:
        #    coletaReview(i)

        try:
            sql = 'insert into teste.tbl_produtos (site, asin, nome, preco, nota, num_avaliacoes, img, link) values (%s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (site, data_asin, name, price, ratings, ratings_num, img, link))
            # sql = 'insert into teste.tbl_detalhes (site, asin, nome, marca, tag, overview, features, details, description, information, documents) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            # cursor.executemany(sql, tuple(product_descr.iloc))
            # sql = 'insert into teste.tbl_avaliacoes (site, asin, titulo, texto, nota, autor) values (%s, %s, %s, %s, %s, %s)'
            # cursor.execute(sql, tuple(avaliacoes.iloc[item]))
        except pymysql.Error as e:
            mydb.rollback()
            print(e)
        finally:
            # cursor.close()
            # mydb.close()
            print("Dados inseridos")

        # IR PRA PRÓXIMA PÁGINA (SE HOUVER)
        try:
            driver.find_element('xpath', ".//a[contains(@class, 's-pagination-next')]").click()
        except NoSuchElementException:
            break
        # paginacao.find_element(By.CLASS_NAME, "s-pagination-next").click()
    # SALVANDO TUDO NO BANCO DE DADOS
    mydb.commit()
    driver.close()

    # final = product.merge(product_descr, on='asin', how='left')

    # print(product)
    # print(final)
    # print(avaliacoes)


    # Salvando os dataframes em arquivos csv -> 'amazon' + pais + palavra_chave
    product.to_excel('results/amazon'+site+'_'+palavra_chave+'_(produtos)_'+today+'.xlsx', index=False)
    product_descr.to_excel('results/amazon'+site+'_'+palavra_chave+'_(detalhes)_'+today+'.xlsx', index=False)
    # final.to_csv('results/amazon'+site+'_'+palavra_chave+'_(produtos)_'+today+'.csv', index=False)
    avaliacoes.to_excel('results/amazon'+site+'_'+palavra_chave+'_(avaliacoes)_'+today+'.xlsx', index=False)

palavra_chave = "buttermilk"

#### .com.br, .com, .co.uk, .ca, .de (buttermilch), .fr (lait ribot), .com.mx, .it, .es (mazada, suero de mantequilla), .co.jp, .sg, .ae, .com.au, .in, .nl, .sa, .com.tu, .se, .pl, .com.be, .eg, .at,
site = ".fr"
coletaElemento(palavra_chave, site)

# coletaReview("B07HM62FL3")

# coletaDetalhes('B09ZMTBTSV')