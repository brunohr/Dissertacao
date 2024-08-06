import pandas as pd
from deepface import DeepFace
from os import listdir
from os.path import isfile, join
from datetime import datetime

import pymysql

### INICIANDO CONEXÃO COM O BANCO DE DADOS
global mydb, cursor
mydb = pymysql.connect(host="localhost", database='scraping2', user="root", passwd="", port = 3307,
                       cursorclass=pymysql.cursors.DictCursor)
cursor = mydb.cursor()



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

def processamentoImgs(url):
    count = 0
    backends = [
        'opencv',
        'ssd',
        'dlib',
        'mtcnn',
        'fastmtcnn',
        'retinaface',
        'mediapipe',
        'yolov8',
        'yunet',
        'centerface',
    ]
    auxResults = []
    results = []
    for i in range(0, len(profiles_img)):
        start = datetime.now()
        # print(count)

        if 'amazon' in profiles_img[i]:
            auxId = "amzn1.account." + profiles_img[i].split("_")[1].split(".")[0]
        elif 'iherb' in profiles_img[i]:
            auxId = profiles_img[i].split("_")[1]
        try:
            cursor.execute("SELECT usuario_id FROM usuario WHERE codigo_perfil = %s;",
                           (auxId.replace(".png", "").replace(".jpg", "").replace(".jpeg", "")))
            auxId = cursor.fetchone()['usuario_id']
        except TypeError:
            continue

        if cursor.execute("SELECT * FROM resultadoimg WHERE usuario_id = %s", (auxId)):
            continue

        img = 'results/profile_img/'+profiles_img[i]
        try:
            aux = DeepFace.analyze(
                img_path=img,
                # actions=['gender', 'age', 'race', 'emotion'],
                actions=['gender', 'age', 'race'],
                enforce_detection=False,
                detector_backend=backends[4],
            )
            auxResults.append(aux)
            if len(aux):
                try:
                    results.append([profiles_img[i], aux[0]['dominant_gender'], aux[0]['age'], aux[0]['dominant_race'], auxId])
                    cursor.execute("INSERT INTO resultadoimg (sexo, idade, raca, usuario_id) VALUES (%s, %s, %s, %s);", results[i][1:])
                    mydb.commit()
                except pymysql.Error as e:
                    print(e)
                    mydb.rollback()
        except ValueError:
            print(print(str(count) + ' VALUE ERROR ' + str(datetime.now() - start)))
        #
        print(str(count) + ' ' + str(datetime.now() - start))

        count+=1

profiles_img = [f for f in listdir('results/profile_img') if isfile(join('results/profile_img', f))]
resultadosImg = processamentoImgs(profiles_img)


