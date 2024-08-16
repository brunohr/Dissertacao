import pandas as pd
from retinaface import RetinaFace as rf
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

def processamentoImgs():
    profiles_img = [f for f in listdir('results/profile_img') if isfile(join('results/profile_img', f))]
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
    # for i in range(len(profiles_img)):
    i = 0
    while len(profiles_img):
        i += 1
        profile_img = profiles_img.pop(0)
        start = datetime.now()

        auxId = ".".join(profile_img.split("_")[1].split(".")[:-1])

        try:
            cursor.execute("SELECT usuario_id FROM usuario WHERE codigo_perfil = %s;", auxId)
            auxId = cursor.fetchone()['usuario_id']
        except TypeError:
            continue

        if cursor.execute("SELECT * FROM resultadoimg WHERE usuario_id = %s", auxId):
            continue

        img = 'results/profile_img/'+profile_img
        aux = rf.detect_faces(img)
        if len(aux):
            try:
                aux = DeepFace.analyze(
                    img_path=img,
                    # actions=['gender', 'age', 'race', 'emotion'],
                    actions=['gender', 'age', 'race'],
                    enforce_detection=False,
                    detector_backend=backends[4],
                )
                if len(aux):
                    auxResults.append(aux)
                    try:
                        auxSql = [profile_img, aux[0]['dominant_gender'], aux[0]['age'], aux[0]['dominant_race'], auxId]
                        results.append(auxSql)
                        cursor.execute("INSERT INTO resultadoimg (img, sexo, idade, raca, usuario_id) VALUES (%s, %s, %s, %s, %s);", auxSql)
                        mydb.commit()
                        print(str(i-1) + ' ' + str(profile_img) + " ok " + str(datetime.now() - start))
                    except pymysql.Error as e:
                        print("ERRO", e)
                        mydb.rollback()
            except ValueError:
               print(str(i-1) + " " + str(profile_img) + ' VALUE ERROR ' + str(datetime.now() - start))
        else:
                try:
                    auxSql = [profile_img, auxId]
                    cursor.execute("INSERT INTO resultadoimg (img, usuario_id) VALUES (%s, %s);", auxSql)
                    mydb.commit()
                    print(str(i-1) + " " + str(profile_img) + ' FACE NÃO DETECTADA ' + str(datetime.now() - start))
                except pymysql.Error as e:
                    print("ERRO", e)
                    mydb.rollback()

processamentoImgs()

# cursor.execute("SELECT ")
