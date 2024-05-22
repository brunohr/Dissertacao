
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

import re

locale.setlocale(locale.LC_ALL, 'pt_BR')

# # INICIANDO CONEXÃO COM O BANCO DE DADOS
# global mydb, cursor
# mydb = pymysql.connect(host="localhost", database='teste', user="root", passwd="@Bruno123",
#                        cursorclass=pymysql.cursors.DictCursor)
# cursor = mydb.cursor()

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
    numPag = 1

    # PÁGINA DAS AVALIAÇÕES DO PRODUTO
    link_reviews = 'https://www.amazon'+site+'/product-reviews/' + asin + '?pageNumber='
    driver.get(link_reviews+str(numPag))
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
    profiles = pd.DataFrame()

    # PEGANDO CADA CARD DE AVALIAÇÃO
    while True:
        # time.sleep(3)
        #
        # # PEGANDO CADA CARD DE AVALIAÇÃO
        # review_elements = driver.find_elements(By.CSS_SELECTOR, '[id*=review-card]')
        try:
            review_elements = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[id*=review-card]')))
        except:
            break
        # if not review_elements:
        #     break
        for review_element in review_elements:
            # EXTRAINDO NOME DO AUTOR
            author_name = review_element.find_element(By.CLASS_NAME, 'a-profile-name').text.strip()

            # EXTRAIR TÍTULO AVALIAÇÃO
            review_title = review_element.find_element(By.CLASS_NAME, 'review-title-content').text.strip()

            # EXTRAINDO TEXTO AVALIAÇÃO
            review_text = review_element.find_element(By.CLASS_NAME, 'review-text').text.strip()

            # EXTRAINDO NOTA E JÁ CONVERTENDO O DECIMAL
            review_star = locale.atof(review_element.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent").split()[0])

            # EXTRAINDO DATA AVALIAÇÃO
            # review_date = ' '.join(review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[-5:])
            # review_date = datetime.strptime(review_date, "%d de %B de %Y").strftime("%Y/%m/%d")
            review_date = review_element.find_element(By.CLASS_NAME, 'review-date').text.strip()

            # EXTRAINDO PAÍS AVALIAÇÃO
            review_country = review_element.find_element(By.CLASS_NAME, 'review-date').text.split()[2:-6]

            # EXTRAINDO LINK DA POSTAGEM
            review_link = review_element.find_element(By.CLASS_NAME, 'review-title-content').get_attribute("href")

            # INCLUIR QUANTAS PESSOAS ACHARAM COMENTÁRIO ÚTIL?
            # try:
            #     helpful_votes = int(review_element.find_element(By.CLASS_NAME, 'cr-vote-text').text.split()[0])
            # except NoSuchElementException:
            #     helpful_votes = 0
            helpful_votes = 0

            # EXTRAINDO LINK DO PERFIL PARA COLETA SEGUINTE
            try:
                profile_link = review_element.find_element(By.CLASS_NAME, 'a-profile').get_attribute("href")
                # profiles = pd.concat([profiles, coletaPerfil(profile_link, review_country)], ignore_index=True)
            except NoSuchElementException:
                profile_link = None

            # if profile_link:
            #     coletaPerfil(profile_link, review_country)

            if profile_link:
                profile_id = profile_link.split('.')[-1] # REDUNDANTE?
            else:
                profile_id = None

            product_review.append((site, asin, review_title, review_text, review_star, author_name, review_date, review_country, helpful_votes, review_link, profile_link, profile_id))
        numPag+=1
        driver.get(link_reviews+str(numPag))

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
    #     sql = 'insert into teste.tbl_avaliacoes (site, asin, titulo, texto, nota, autor, date, pais, helpful_votes, link_avaliacao, link_perfil, id_perfil) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #     cursor.executemany(sql, product_review)
    #     print(f"Avaliações do produto {asin} inseridas")
    #     mydb.commit()
    # except pymysql.Error as e:
    #     mydb.rollback()
    #     print(e)

    # SALVANDO AS LISTAS EM DF
    review = pd.DataFrame(data=product_review,
                        columns=['site', 'asin', 'title', 'text', 'star', 'user', 'data', 'country', 'helpful_votes', 'link_avaliacao', 'link_perfil', 'id_perfil'])

    return review #, profiles
def coletaDetalhes(asin, url, review = False):
    driver = webdriver.Firefox()
    driver.get(url)

    pag = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, './/div[@class="product-grouping-wrapper defer-block"]')))
    # try:
    #     driver.find_element(By.ID, "sp-cc-all-link").click()
    # except NoSuchElementException:
    #     pass

    nome = pag.find_element(By.ID, 'name').get_attribute("textContent").strip()
    marca = pag.find_element(By.XPATH, './/div/div/a[@class="last"][1]').text.strip()
    # tag = pag.find_element(By.XPATH, './/a[contains(@href, "categories")]/a').text.strip()
    tag = pag.find_element(By.XPATH, './/div/div/a[4]').text.strip()

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

    aux = pag.find_elements(By.XPATH, './/div[@class="row"]/div[contains(@class, "col-xs-24")]/div[@class="row item-row"]')

    for bloco in aux:
        if "Descrição\n" in bloco.text.strip():
            descricao = bloco.text.strip()
        elif "Uso Sugerido\n" in bloco.text.strip():
            uso = bloco.text.strip()
        elif "Outros Ingredientes\n" in bloco.text.strip():
            ingredientes = bloco.text.strip()
        elif "Advertências\n" in bloco.text.strip():
            advertencia = bloco.text.strip()
        elif "Aviso Legal\n" in bloco.text.strip():
            aviso = bloco.text.strip()

    driver.close()

    # try:
    #     if not review:
    #         sql = 'insert into teste.tbl_detalhes (site, asin, nome, marca, moeda, price, tag, overview, features, details, description, information, documents) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #         cursor.execute(sql, (site, asin, nome, marca, moeda, price, tag, overview, features, details, description, information, documents))
    #     else:
    #         sql = 'insert into teste.tbl_detalhes_review (site, asin, nome, marca, price, tag, overview, features, details, description, information, documents, review) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #         cursor.execute(sql, (site, asin, nome, marca, moeda, price, tag, overview, features, details, description, information, documents, review))
    #     print(f"Detalhes do produto {asin} inseridos")
    #     mydb.commit()
    # except pymysql.Error as e:
    #     mydb.rollback()
    #     print(e)

    return pd.DataFrame(data=[[site, asin, nome, marca, tag, moeda, price, descricao, uso, ingredientes, advertencia, aviso]],
                       columns=['site', 'asin', 'nome', tag, 'marca', 'moeda', 'price', 'descricao', 'uso', 'ingredientes', 'advertencia', 'aviso'])

def coletaPerfil(link, site):
    driver = webdriver.Firefox()
    driver.get(link)
    try:
        driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    except NoSuchElementException:
        pass

    profile_review = []
    aux = pd.DataFrame()

    nome = driver.find_element(By.ID, "customer-profile-name-header").text.strip()
    img = driver.find_element(By.ID, "avatar-image").get_attribute("src")

    # sql = "insert into profile values (%s, %s, %s, %s)"
    # cursor.execute(sql, (link, nome, img, profile_country))

    reviews = driver.find_elements(By.CLASS_NAME, 'your-content-card-wrapper')
    for review in reviews:
        title = review.find_element(By.CLASS_NAME, 'your-content-text-1').text.strip()
        stars = int(review.find_element(By.CLASS_NAME, 'a-icon-star').get_attribute("textContent").split()[0])
        text = review.find_element(By.CLASS_NAME, 'your-content-text-3').text.strip()
        link_avaliacao = review.find_element(By.CSS_SELECTOR, '[class*="a-link-normal your-content-card"]').get_attribute("href")
        id_profile = link.split('.')[-1]
        profile_review.append((link, title, stars, text, link_avaliacao, id_profile))

        driver2 = webdriver.Firefox()
        driver2.get(link_avaliacao)
        link_produto = driver2.find_element(By.CSS_SELECTOR, "a[data-hook='product-link']").get_attribute("href")
        asin = re.split('/dp/|/ref', link_produto)[1]
        driver2.close()
        aux = pd.concat([aux, coletaDetalhes(asin, site, id_profile)], ignore_index=True)

    driver.close()
    return pd.DataFrame(data=profile_review,
                        columns=['link', 'title', 'stars', 'text', 'link_avaliacao', 'link_produto', 'nome', 'img', 'id_profile'])

def coletaElemento(palavra_chave, site):
    today = date.today().strftime("%Y%m%d")

    # INICIALIZE O DRIVER DO SELENIUM
    # driver = webdriver.Firefox()

    fp = webdriver.FirefoxOptions()
    fp.set_preference("network.cookie.cookieBehavior", 2)
    driver = webdriver.Firefox(options = fp)

    # LOGANDO PARA PODER ACESSAR PÁGINA DE QUEM AVALIOU O PRODUTO
    # login = input("Login")
    # senha = input("Senha")
    # driver.get('https://www.amazon'+site+'/login')
    # driver.find_element(By.ID, 'ap_email').send_keys(login)
    # driver.find_element(By.ID, 'continue').click()
    # driver.find_element(By.ID, 'ap_email').send_keys(senha)
    # driver.find_element(By.NAME, 'rememberMe').click()
    # driver.find_element(By.ID, 'signInSubmit').click()

    # try:
    #     driver.find_element(By.ID, "sp-cc-rejectall-link").click()
    # except NoSuchElementException:
    #     pass

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

    pag = 1
    while True:
        url = 'https://www.br.iherb.com/search?kw=' + palavra_chave + "&p=" + str(pag)
        # url = 'https://www.amazon.com.br/'
        driver.get(url)

        # CONFIGURAÇÃO PRA AGUARDAR A PAG CARREGAR ANTES DE TENTAR PEGAR OS RESULTS
        if driver.find_elements(By.ID, "NoResultsProductsPage"):
            break

        items = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, './/div[@class="product-inner product-inner-wide"]')))

        for item in items:
            name = item.find_element(By.XPATH, './/a[@class="absolute-link product-link"]').get_attribute('aria-label')

            ######  AMAZON
            # try:
            #     item.find_element('class name', "puis-label-popover-default")
            #     name = name + " (PROPAGANDA)"
            # except NoSuchElementException:
            #     pass

            ##### AMAZON
            # data_asin = item.get_attribute("data-asin")
            data_asin = item.find_element(By.XPATH, ".//a[@class='absolute-link product-link']").get_attribute("data-ga-product-id") ###asin é o códgo na amazon, aqui repeti só pra tentar manter um padrão - trocar no código da amazon futuramente
            # ###### AMAZON
            # # DESMEMBRANDO PREÇO (INCLUIR MOEDA TBM?)
            # whole_price = item.find_elements('xpath', './/span[@class="price"]')
            # fraction_price = item.find_elements('xpath', './/span[@class="a-price-fraction"]')
            # if whole_price and fraction_price:
            #     price = float('.'.join([whole_price[0].text.replace('.', '').replace(',', ''), fraction_price[0].text]))
            # else:
            #     price = None
            # # price = None
            try:
                price = item.find_element('xpath', ".//span[contains(@class, 'price')]").text #### TEM QUE RETIRAR A MOEDA
            except NoSuchElementException:
                price = None

            # DESMEMBRANDO A AVALIAÇÃO - MANTENDO NA PÁG DE RESULTS PRA EVITAR UM LOOP COM A COLETA DE DETALHES VINDA DA PÁGINA DO USUÁRIO
            ############## AMAZON
            # ratings_box = item.find_elements('xpath', './/div[@class="a-row a-size-small"]/span')
            # if ratings_box:
            #     # ADAPTA OS PONTOS E VIRGULAS NOS NÚMEROS
            #     ratings = locale.atof(ratings_box[0].get_attribute('aria-label').split()[0])
            #     ratings_num = locale.atoi(ratings_box[1].text.replace(',','').replace('.',''))
            # else:
            #     ratings, ratings_num = 0.0, 0
            #
            # if(ratings >= 10): ##CORRIGINDO POSSÍEVIS PROBLEMSA DE CONVERSÃO DE DECIMAIS
            #     ratings = ratings/10

            try:
                ratings_num = int(item.find_element(By.XPATH, './/a[@class="rating-count scroll-to"]').text.replace(',','').replace('.',''))
                ratings = float(re.split('/', item.find_element(By.XPATH, './/a[@class="stars scroll-to"]').get_attribute("title"))[0])
            except NoSuchElementException:
                ratings_num, ratings = 0, None

            # LINK DE CADA PRODUTO
            ##### AMAZON
            # link = item.find_element('xpath', './/a[@class="a-link-normal s-no-outline"]').get_attribute("href")
            # LINK DA IMAGEM -> DEPOIS BAIXAR O ARQUIVO
            # img = item.find_element('class name', "s-image").get_attribute("src")

            link = item.find_element('xpath',".//a[@class='absolute-link product-link']") .get_attribute("href")
            img = item.find_element(By.XPATH, './/span[@class="product-image"]/img').get_attribute("src")

            # # INSERÇÃO NO BANCO DE DADOS
            # try:
            #     # VERIFICAR SE JÁ EXISTE??
            #     sql = 'insert into teste.tbl_produtos (site, asin, nome, preco, nota, num_avaliacoes, img, link) values (%s, %s, %s, %s, %s, %s, %s, %s)'
            #     cursor.execute(sql, (site, data_asin, name, price, ratings, ratings_num, img, link))
            #     print(f"Produto {data_asin} inserido")
            # except pymysql.Error as e:
            #     mydb.rollback()
            #     print(e)

            #ACESSANDO PÁGINA DO PRODUTO, EXCETO SE FOR AMAZON MUSIC (E OS ANÚNCIOS?)
            #DENTRO DA FUNÇÃO FAZ A INSERÇÃO NO BANCO
            # try:
            #     "mp3" in item.find_element('xpath', ".//a[@class='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-bold']").text.strip()
            #     name = name + " (AMAZON MUSIC)"
            # except NoSuchElementException:
            #     product_descr = pd.concat([product_descr, coletaDetalhes(data_asin, site)], ignore_index=True)

            #ACESSANDO PÁGINA DE AVALIAÇÃO DO PRODUTO (SE HOUVER - SE FOR O CASO DE TER AVALIAÇÃO MAS SEM COMENTÁRIO, VAI SÓ ABRIR E FECHAR)
            #DENTRO DA FUNÇÃO FAZ A INSERÇÃO NO BANCO
            if ratings > 0: #### trocar pra pegar avalições com análise (como checar?) , esse aqui verifica só a qtde notas
                # avaliacoes = pd.concat([avaliacoes, coletaReview(data_asin, site)], ignore_index=True)
                # tempAvaliacoes, tempProfiles = coletaReview(data_asin, site)
                tempAvaliacoes = coletaReview(data_asin, site)
                avaliacoes = pd.concat([avaliacoes, tempAvaliacoes], ignore_index=True)
                # profiles = pd.concat([profiles, tempProfiles], ignore_index=True)
                # print("ok")
            # else:
            #     print("sem avaliações\n")

            # SALVANDO NO DATAFRAME
            product = pd.concat(
                [product, pd.DataFrame(data=[[site, data_asin, name, price, ratings, ratings_num, img, link]],
                                       columns=['site', 'asin', 'name', 'price', 'ratings', 'ratings_num', 'img', 'link'])],
                ignore_index=True)

            # INSERÇÃO NO BANCO DE DADOS
            # try:
            #     # VERIFICAR SE JÁ EXISTE??
            #     sql = 'insert into teste.tbl_produtos (site, asin, nome, preco, nota, num_avaliacoes, img, link) values (%s, %s, %s, %s, %s, %s, %s, %s)'
            #     cursor.execute(sql, (site, data_asin, name, price, ratings, ratings_num, img, link))
            #     print(f"Produto {data_asin} inserido")
            #     mydb.commit()
            # except pymysql.Error as e:
            #     print(e)
            #     mydb.rollback()

        # for i in product_asin:
        #    coletaReview(i)

        # IR PRA PRÓXIMA PÁGINA (SE HOUVER)
        ##### AMAZON
        # try:
        #     driver.find_element('xpath', ".//a[contains(@class, 's-pagination-next')]").click()
        # except NoSuchElementException:
        #     break
        # paginacao.find_element(By.CLASS_NAME, "s-pagination-next").click()
        pag = pag+1

    # profiles = pd.DataFrame()
    # for link in avaliacoes['link_perfil']:
    #     if link:
    #         profiles = pd.concat([profiles, coletaPerfil(link, site)], ignore_index=True)


    # SALVANDO TUDO NO BANCO DE DADOS
    # cursor.close()
    # mydb.close()
    # driver.close()

    # final = product.merge(product_descr, on='asin', how='left')

    # print(product)
    # print(final)
    # print(avaliacoes)

    # Salvando os dataframes em arquivos csv -> 'amazon' + pais + palavra_chave
    product.to_excel('results/amazon'+site+'_'+palavra_chave+'_(produtos)_'+today+'.xlsx', index=False)
    product_descr.to_excel('results/amazon'+site+'_'+palavra_chave+'_(detalhes)_'+today+'.xlsx', index=False)
    # final.to_csv('results/amazon'+site+'_'+palavra_chave+'_(produtos)_'+today+'.csv', index=False)
    avaliacoes.to_excel('results/amazon'+site+'_'+palavra_chave+'_(avaliacoes)_'+today+'.xlsx', index=False)
    # profiles.to_excel('results/amazon'+site+'_'+palavra_chave+'_(perfis)_'+today+'.xlsx', index=False)

palavra_chave = "buttermilk"

#### .com.br, .com, .co.uk, .ca, .de (buttermilch), .fr (lait ribot), .com.mx, .it, .es (mazada, suero de mantequilla), .co.jp, .sg, .ae, .com.au, .in, .nl, .sa, .com.tu, .se, .pl, .com.be, .eg, .at,
site = ".co.uk"

coletaElemento(palavra_chave, site)

# coletaReview("B07HM62FL3")

# coletaDetalhes('B09ZMTBTSV')
