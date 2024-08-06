import pandas as pd
from deepface import DeepFace
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
    results = []
    for i in url:
        print(count)
        img = 'results/profile_img/'+i
        if img == "VERIFICAR":
            results.append("VERIFICAR")
        elif "amazon-avatars-global/default._" not in img:
            results.append(DeepFace.analyze(
                img_path=img,
                actions=['gender', 'age', 'race', 'emotion'],
                enforce_detection=False,
                detector_backend=backends[7],
            ))
        else:
            results.append("SEM IMAGEM")
        count+=1

from os import listdir
from os.path import isfile, join
profiles_img = [f for f in listdir('results/profile_img') if isfile(join('results/profile_img', f))]

resultadosImg = processamentoImgs(profiles_img)
