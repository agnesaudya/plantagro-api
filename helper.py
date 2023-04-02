import requests
import xmltodict
import classes
import json
import utils
import province


def fetchBMKGDataByMuncipality(province_name:str, municipality:str):
    split_res = province_name.split(' ')
    url_query = ""
    if(len(split_res)>1):  
        url_query = (split_res[0]+split_res[1])
    else:
        url_query = (split_res[0])

    
    
    url = f'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-{url_query}.xml'
    response = requests.get(url)
    data = xmltodict.parse(response.content)
    fetchRes = classes.State()
    fetchRes.province_name=province_name
    for dat in data['data']['forecast']['area']:
        if(dat['@description']==municipality):
            fetchRes.municipality=dat['@description']
            for par in dat['parameter']:
                if(par['@id']=="hu"):
                    total = 0
                    counter = 0 
                    mean = 0
                    for h in par['timerange']:
                        counter +=1 
                        total+=int(h['value']['#text'])
                    mean = total/counter
                    fetchRes.mean_humid=mean  
                elif(par['@id']=="humax"):
                    fetchRes.max_humid = par['timerange'][0]['value']['#text']
                elif(par['@id']=="tmax"):
                    fetchRes.max_temp = par['timerange'][0]['value'][0]['#text']
                elif(par['@id']=="humin"):
                    fetchRes.min_humid = par['timerange'][0]['value']['#text']
                elif(par['@id']=="tmin"):
                    fetchRes.min_temp = par['timerange'][0]['value'][0]['#text']
                elif(par['@id']=="t"):
                    total = 0
                    counter = 0 
                    mean = 0
                    for h in par['timerange']:
                        counter +=1 
                        total+=int(h['value'][0]['#text'])
                    mean = total/counter

                    fetchRes.mean_temp=mean
                    break
            break
    return json.dumps(fetchRes.__dict__)

def fetchAllBMKGDataByProvince(province_name:str):
    split_res = province_name.split(' ')
    url_query = ""
    if(len(split_res)>1):  
        url_query = (split_res[0]+split_res[1])
    else:
        url_query = (split_res[0])
    
    url = f'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-{url_query}.xml'
    response = requests.get(url)
    data = xmltodict.parse(response.content)
    arr = []

  
    for dat in data['data']['forecast']['area']:
        fetchRes = classes.State()
        fetchRes.province_name = province_name
        fetchRes.municipality=dat['@description']
        if(dat['@tags']=="Pelabuhan" or dat['@type']=="sea"):
            continue
        else:
            for par in dat['parameter']:
                if(par['@id']=="hu"):
                    total = 0
                    counter = 0 
                    mean = 0
                    for h in par['timerange']:
                        counter +=1 
                        total+=int(h['value']['#text'])
                    mean = total/counter
                    fetchRes.mean_humid=mean  
                elif(par['@id']=="humax"):
                    fetchRes.max_humid = par['timerange'][0]['value']['#text']
                elif(par['@id']=="tmax"):
                    fetchRes.max_temp = par['timerange'][0]['value'][0]['#text']
                elif(par['@id']=="humin"):
                    fetchRes.min_humid = par['timerange'][0]['value']['#text']
                elif(par['@id']=="tmin"):
                    fetchRes.min_temp = par['timerange'][0]['value'][0]['#text']
                elif(par['@id']=="t"):
                    total = 0
                    counter = 0 
                    mean = 0
                    for h in par['timerange']:
                        counter +=1 
                        total+=int(h['value'][0]['#text'])
                    mean = total/counter
                    fetchRes.mean_temp=mean
                    break    
            
            arr.append(fetchRes)

 
    return json.dumps([obj.__dict__ for obj in arr])

def getPlantsByType(type:str):
    getAllPlants()
    arr = []
    f = open('plants.json')
    plants = json.loads(f.read())
    for p in plants:
        if(p['plant_type']==type):
            arr.append(p)
    f.close()

 
    return arr

def recommendPlace(plant_name:str):
    plant = {}
    for i in getAllPlants():
        if(i['plant_name']==plant_name):
            plant=i
    list_recommended = []
    for p in province.list_kota:
        listMuncipal = json.loads(fetchAllBMKGDataByProvince(p))
        for m in listMuncipal:
            flag = True
            if(int(m['mean_temp'])<int(plant['min_temp'])):
                flag=False
            elif(int(m['mean_temp'])>int(plant['max_temp'])):
                flag=False
            elif(int(m['mean_humid'])<int(plant['min_humid'])):
                flag=False
            elif(int(m['mean_humid'])>int(plant['max_humid'])):
                flag=False
            
            if(flag):
                list_recommended.append(m)
    return list_recommended
    
    


def getAllPlants():
    csvFilePath = r'plants.csv'
    jsonFilePath = r'plants.json'
    utils.csv_to_json(csvFilePath, jsonFilePath)
    
    f = open('plants.json')
    plants = json.loads(f.read())
    f.close()

    return plants

def analyzePlants(province_name:str, municipality:str, type:str):    
    municipality_data = json.loads(fetchBMKGDataByMuncipality(province_name=province_name, municipality=municipality))
    plants = []
    res_plants = []
    print(type)
    if(type is not None):
        plants = getPlantsByType(province_name=province_name, municipality=municipality, type=type)
    else:
        plants = getAllPlants()
    for p in plants:
        flag = True

        if(int(municipality_data['mean_temp'])<int(p['min_temp'])):
            flag=False
        elif(int(municipality_data['mean_temp'])>int(p['max_temp'])):
            flag=False
        elif(int(municipality_data['mean_humid'])<int(p['min_humid'])):
            flag=False
        elif(int(municipality_data['mean_humid'])>int(p['max_humid'])):
            flag=False
        
        if(flag):
            res_plants.append(p)

    return res_plants
            

        
        







