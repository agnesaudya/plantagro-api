from email.message import EmailMessage
import json
from fastapi import FastAPI
from celery import Celery
import classes
import helper
import smtplib
app = FastAPI()


celery = Celery(
    __name__,
    broker="amqp://guest:guest@localhost:5672/", backend='rpc://',
)


@app.get("/province-info")
async def info(input: classes.InputData): 
    task = getProvinceInfoTask.delay(input.province_name, input.municipality, input.email)
    return {"status":"your result will be sent through the email"}

@app.get("/fruit-list")
async def fruit_list(email:str): 
    task =  getPlantTask.delay(email,"buah")
    return {"status":"your result will be sent through the email"}

@app.get("/vegetable-list")
async def vegetable_list(email:str):
    task = getPlantTask.delay(email, "sayuran")
    return {"status":"your result will be sent through the email"}

@app.get("/rempah-list")
async def vegetable_list(email:str):
    task = getPlantTask.delay(email, "rempah")
    return {"status":"your result will be sent through the email"}

@app.get("/recommended-plant")
async def recommend_plants(input: classes.InputData):
    task = analyzePlantTask.delay(input.province_name, input.municipality, input.email, input.type)
    return {"status":"your result will be sent through the email"}

@app.get("/recommended-town")
async def recommend_towns(plant_name:str, email:str):
    task = getRecommendedPlace.delay(plant_name, email)
    return {"status":"your result will be sent through the email"}

@celery.task
def getRecommendedPlace(plant_name:str, email:str):
    subject = f"Hasil analisis informasi mengenai {plant_name}"
    content = f"Halo kak, berikut adalah hasil analisis informasi mengenai daerah-daerah yang sekiranya cocok untuk {plant_name} kami ambil berdasarkan data BMKG:\n"
    listMunicipality=""
    counter=0
    res = helper.recommendPlace(plant_name=plant_name)


    for i in res:
        counter+=1
        listMunicipality+=f"{counter}. {i['municipality']} terletak di {i['province_name']}. Beberapa hari ini, {i['municipality']} memiliki temperatur dalam jangka "
        listMunicipality+=f"{i['min_temp']}-{i['max_temp']} derajat Celcius dan memiliki kelembapan udara sekitar {i['min_humid']}-{i['max_humid']}%. "
        listMunicipality+=f"Dalam beberapa hari ini, {i['municipality']}, sudah dihitung bahwa rata-rata suhu adalah {i['mean_temp']} dan rata-rata kelembapan adalah {i['mean_humid']}.\n\n"
        content+=listMunicipality
       

   
    sendEmail(email=email, content=content, subject=subject)

    return res

@celery.task
def getProvinceInfoTask(province_name:str, municipality:str, email:str):
    subject = "Hasil informasi setiap daerah"
    content = f"Halo kak, berikut adalah informasi mengenai daerah-daerah yang kami ambil berdasarkan data BMKG:\n"
    listMunicipality=""
    counter=0
    if(municipality is None):
        res = json.loads(helper.fetchAllBMKGDataByProvince(province_name=province_name))
        for i in res:
            counter+=1
            listMunicipality+=f"{counter}. {i['municipality']} terletak di {i['province_name']}. Beberapa hari ini, {i['municipality']} memiliki temperatur dalam jangka "
            listMunicipality+=f"{i['min_temp']}-{i['max_temp']} derajat Celcius dan memiliki kelembapan udara sekitar {i['min_humid']}-{i['max_humid']}%. "
            listMunicipality+=f"Dalam beberapa hari ini, {i['municipality']}, sudah dihitung bahwa rata-rata suhu adalah {i['mean_temp']} dan rata-rata kelembapan adalah {i['mean_humid']}.\n\n"
        content+=listMunicipality
       
    else:
        res = json.loads(helper.fetchBMKGDataByMuncipality(province_name=province_name,municipality=municipality))
        content+=f"{res['municipality']} terletak di {res['province_name']}. Beberapa hari ini, {res['municipality']} memiliki temperatur dalam jangka "
        content+=f"{res['min_temp']}-{res['max_temp']} derajat Celcius dan memiliki kelembapan udara sekitar {res['min_humid']}-{res['max_humid']}%. "
        content+=f"Dalam beberapa hari ini, {res['municipality']}, sudah dihitung bahwa rata-rata suhu adalah {res['mean_temp']} dan rata-rata kelembapan adalah {res['mean_humid']}.\n\n"
        
    
   
    sendEmail(email=email, content=content, subject=subject)

    return res

@celery.task
def getPlantTask(email:str, type:str):
    res = helper.getPlantsByType(type)
    subject = "Hasil Pencarian Tanaman-tanaman"
    content = f"Halo kak, berikut adalah hasil analisis {type} apa saja yang ada di data kami:\n"
    listPlant = ""

    counter = 0
    for i in res:
        counter+=1
        capitalize_name = i['plant_name'].capitalize()
        listPlant+=f"{counter}. {capitalize_name} merupakan {i['plant_type']} yang memiliki temperatur minimal sebesar {i['min_temp']} derajat Celcius dan temperatur maksimal sebesar {i['max_temp']} derajat Celcius. "
        listPlant+=f"Selain itu, {capitalize_name} butuh lingkungan dengan kelembapan udara sekitar {i['min_humid']}-{i['max_humid']}%. "
        listPlant+=f"{capitalize_name} juga dapat di {i['soil_type']} dengan keasaman {i['ph']} dan di curah hujan sekitar {i['curah_hujan']}.\n\n"

    content+=listPlant


    sendEmail(email=email, content=content, subject=subject)
    return res
        


@celery.task
def analyzePlantTask(province_name:str, municipality:str, email:str, type:str):

    res = helper.analyzePlants(province_name, municipality, type)

    subject = f"Hasil Analisis Tanaman-tanaman yang memang cocok untuk daerah {municipality}"
    content = f"Halo kak, berikut adalah hasil analisis apa saja yang ada di data kami:\n"
    listPlant = ""

    counter = 0
    for i in res:
        counter+=1
        capitalize_name = i['plant_name'].capitalize()
        listPlant+=f"{counter}. {capitalize_name} merupakan {i['plant_type']} yang memiliki temperatur minimal sebesar {i['min_temp']} derajat Celcius dan temperatur maksimal sebesar {i['max_temp']} derajat Celcius. "
        listPlant+=f"Selain itu, {capitalize_name} butuh lingkungan dengan kelembapan udara sekitar {i['min_humid']}-{i['max_humid']}%. "
        listPlant+=f"{capitalize_name} juga dapat di {i['soil_type']} dengan keasaman {i['ph']} dan di curah hujan sekitar {i['curah_hujan']}.\n\n"

    content+=listPlant
    sendEmail(email=email, content=content, subject=subject)
    return res
        
  



def sendEmail(email:str, content:str, subject:str):
    email_address = "brilliantaurisya@gmail.com"
    email_password = "izeeeiddribvpivw"
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = email

    
    msg.set_content(str(content))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
