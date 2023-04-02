from email.message import EmailMessage
from fastapi import FastAPI
from celery import Celery
import classes
import helper
from kombu import Queue
import smtplib
app = FastAPI()


celery = Celery(
    __name__,
    broker="amqp://guest:guest@localhost:5672/", backend='rpc://',
)


@app.get("/province-info")
async def info(input: classes.InputData): 
    task = getProvinceInfoTask.delay(input.province_name, input.municipality, input.email)
    print(task.state, task.result)
    return {"status":"your result will be sent through the email"}

@app.get("/fruit-list")
async def fruit_list(): 
    task =  getPlantTask.delay(input.province_name, input.municipality, input.email,"buah")
    return {"status":"your result will be sent through the email"}

@app.get("/vegetable-list")
async def vegetable_list(input: classes.InputData):
    task = getPlantTask.delay(input.province_name, input.municipality, input.email, "sayuran")
    return {"status":"your result will be sent through the email"}

@app.get("/rempah-list")
async def vegetable_list(input: classes.InputData):
    task = getPlantTask.delay(input.province_name, input.municipality, input.email, "rempah")
    return {"status":"your result will be sent through the email"}

@app.get("/analyze")
async def plan_plants(input: classes.InputData):
    task = analyzePlantTask.delay(input.province_name, input.municipality, input.email, input.type)
    return {"status":"your result will be sent through the email"}




@celery.task
def getProvinceInfoTask(province_name:str, municipality:str, email:str):
 
    res = {"status":"failed"}
    if(municipality is None):
        res = helper.fetchAllBMKGDataByProvince(province_name=province_name)
    else:
        res = helper.fetchBMKGDataByMuncipality(province_name=province_name,municipality=municipality)
        
    # sendEmail(email=email, content=res)

    return res

@celery.task
def getPlantTask(province_name:str, municipality:str, email:str, type:str):

    res = helper.getPlantsByType(province_name, municipality, type)
    subject = "Hasil Pencarian Tanaman-tanaman"
    content = "Halo kak, berikut adalah hasil analisis dari kami:\n"
    return res
        
    # sendEmail(email=email, content=res)

@celery.task
def analyzePlantTask(province_name:str, municipality:str, email:str, type:str):

    res = helper.analyzePlants(province_name, municipality, type)
    return res
        
    # sendEmail(email=email, content=res)



def sendEmail(email:str, content:str):
    email_address = "brilliantaurisya@gmail.com"
    email_password = "izeeeiddribvpivw"
    msg = EmailMessage()
    msg['Subject'] = "Email subject"
    msg['From'] = email_address
    msg['To'] = email

    
    msg.set_content(str(content))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
