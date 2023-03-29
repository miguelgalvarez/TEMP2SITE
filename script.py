import os
import glob
import time
import MySQLdb
import datetime
import threading
import urllib
import requests
import mysql.connector
from mysql.connector import Error


db = MySQLdb.connect(host = "enter mySQL database ip", user = "enter username", passwd = "enter password", db = "enter database name")
cur = db.cursor()

try:
    connection = mysql.connector.connect(host='enter database ip',
                             database='enter database name',
                             user='enter database username',
                             password='enter database password')

    if connection.is_connected():
       db_Info = connection.get_server_info()
       print("Connected to MySQL database... MySQL Server version on ",db_Info)
       cursor = connection.cursor()
       cursor.execute("select database();")
       record = cursor.fetchone()
       print ("Your connected to - ", record)
    
except Error as e :
    print ("Error while connecting to MySQL", e)
           
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
     
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
     
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c  

def sendDataToServer():
    global temperature

    threading.Timer(600,sendDataToServer).start()
    print("Mesuring...")
    read_temp()
    temperature = read_temp()
    print(temperature)
    temp= read_temp()
    urllib.request.urlopen("domain"+str(read_temp())).read()

while True:
        print("putting temperature data into temp_pi database")
        i = datetime.datetime.now()
        year = str(i.year)
        month = str(i.month)
        day = str(i.day)
        date = day + "-" + month + "-" + year

        hour = str(i.hour)
        minute = str(i.minute)
        second = str(i.second)
        timestr = hour + ":" + minute + ":" + second
        
        valT = str(read_temp())
              
        try:
            cur.execute("""INSERT INTO TAB_CLASSROOM(temp_c,T_Date,T_Time) VALUES(%s,%s,%s)""",(valT,i,timestr))
            db.commit()
        except:
            db.rollback()

        time.sleep(1)


        sendDataToServer()

cur.close()  
db.close()
