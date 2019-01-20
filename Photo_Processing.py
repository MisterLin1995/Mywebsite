import pandas as pd
import exifread
import os
import re
import datetime
import requests
from sqlalchemy import create_engine

def positioncal(positionstring,flag):
    positionstring=positionstring.replace('[','').replace(']','').replace(' ','')
    positionlist=[float(x) for x in re.split(',|/',positionstring)]
    position=positionlist[0]+positionlist[1]/60+positionlist[2]/positionlist[3]/3600
    if flag in ['W','S']:
        position=-position
    return position

def imgInfo(filename):
    #Geo Info
    rawInfo = exifread.process_file(open(filename,'rb'))
    try:
        latitude = positioncal(str(rawInfo['GPS GPSLatitude']), str(rawInfo['GPS GPSLatitudeRef']))
        longitude = positioncal(str(rawInfo['GPS GPSLongitude']), str(rawInfo['GPS GPSLongitudeRef']))
        locationResponse = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&key=AIzaSyCPUZdupskWClYp93VXVl0NDlfOkgokZf4".format(latitude,longitude))
        location = locationResponse.json()['results'][2]['formatted_address']
    except:
        latitude = ''
        longitude = ''
        location = ''  
    #Time Info
    try:
        takenTimeStr = str(rawInfo['EXIF DateTimeOriginal']).replace(':','/',2)
        takenTime = datetime.datetime.strptime(takenTimeStr,format('%Y/%m/%d %H:%M:%S'))
    except:
        takenTime = ''
    
    #Size Info
    try:
        width = int(str(rawInfo['EXIF ExifImageWidth']))
        length = int(str(rawInfo['EXIF ExifImageLength']))
    except:
        width = ''
        length = ''
    

    return [latitude,longitude,location,takenTime,width,length]

if __name__ == '__main__':
    photoInfo=pd.DataFrame(columns=['fileroute','latitude','longitude','location','takenTime','width','length','description'])
    count=0

    for file in os.listdir('./static/album/'):
        if file.endswith('.jpg'):
            fileroute=os.path.join('./static/album',file)
            photoInfo.loc[count]=[fileroute]+imgInfo(fileroute)+[file]
            count+=1
    
    engine = create_engine('mysql+pymysql://mrlin:Zhang-01234@127.0.0.1/web?charset=utf8',encoding = 'utf-8')
    mysqlconn = engine.connect()
    try:
        photoInfo.to_sql('photoInfo',con=mysqlconn,if_exists='replace')
    except Exception as e:
        print(e)
        photoInfo.to_excel('photoInfo.xlsx')