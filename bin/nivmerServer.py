#! /usr/bin/python3.7

## Programme de récupération de données de marégraphe de KERGUELEN. Mise en forme pour l'envoie d'un mail automatique à la Réunion et l'envoie par FTP en fin de journée aux chefs de programme
## Alerting via le serveur Zabbux
## @author: cc71

import yaml
import sys
import socket
import datetime
import re
import time
from sendByMail import *
import os

myYAML = sys.argv[1] ##Fichier de configuration du marégraphe en paramètre

with open(myYAML, 'r') as stream:
    try:
        myData = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

import logging
os.chdir(os.path.dirname(__file__))
logging.basicConfig(filename='os.getcwd() + 'log/nivmer' + myData['name'] + '.log', level=logging.INFO)

last15MinData=[] #Données des 15 dernières hauteur d'eau à envoyer à la réu
Store15MinForNextSend=[] #Données de 15 hauteur d'eau à renvoyer dans le mail à la réu. Egale aux valeurs de last15MinData mais du mail N-1
dateOfFirstData2=int(time.time()) #Initialisation de la valeur de temps à sauvegarder

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(("0.0.0.0", myData['port']))
logging.info("nivmer" + myData['name'] + " UDP Server now listening")

# Sous Fonction formatage des données pour préparer à l'envoie par mail à la Réunion 
def crex(acquiData):
    dataParsed = re.findall(r'([\w]+)',acquiData.decode())
    ## dataParsed est désormais un tableau avec chaque élément dans une case. Voir le fichier YML pour l'emplacement des données

    #Calcul de la hauteur d'eau en mm par rapport au zero hydro
    hauteurEauRef = (10 * (myData['fixed']['zh2f'] + myData['fixed']['f2zr']) - int(dataParsed[myData['data']['Tid']]))

    return str(int(hauteurEauRef))

while(True):

    now = datetime.datetime.now()
    dateForFile = now.strftime('%Y-%m-%d')
    fileNameOfDay = "NIV" + myData['name'] + "-" + dateForFile + ".txt"
    fileLoc = "../dataInProgress/" + fileNameOfDay

    bytesAddressPair = UDPServerSocket.recvfrom(myData['bufferSize'])

    message = bytesAddressPair[0]
    address = format(bytesAddressPair[1][0])

    if (str(address) != myData['ip']) :
            print("Attention l'ip " + str(address) + " usurpe le marégraphe!")
            break

    f = open(fileLoc, "a")
    f.write(message.decode('UTF-8'))
    f.close()

    hauteurEauRef = crex(message)
    logging.info("La hauteur d'eau est de : " + hauteurEauRef)

    if (len(last15MinData) == 0) :
        dateOfFirstData1 = now.strftime('%Y %m %d %H %M')
    else:
        if(int(time.time()) - dateOfLastData > 120): ##Si l'aquisition cesse d'envoyer des données, les valeurs précédentes n'ont plus lieux d'être envoyé à la Réu
            logging.info("ecart avec la dernière valeur supérieur à 2 minutes, suppression des tableaux")
            last15MinData.clear()
            Store15MinForNextSend.clear()

    last15MinData.append(hauteurEauRef)
    dateOfLastData = int(time.time())

    if len(last15MinData) == 15:
        logging.info("Sending Mail with : " + str(Store15MinForNextSend + last15MinData))
        sendMail(Store15MinForNextSend + last15MinData,dateOfFirstData2,myData)
        Store15MinForNextSend = last15MinData.copy() #On fait glisser les données des 15 dernières minutes pour les renvoyer au prochain mail
        dateOfFirstData2 = dateOfFirstData1 #On garde la date de la première valeur de last15MinData pour l'envoyer au prochain mail
        last15MinData.clear()
