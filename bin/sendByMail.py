#!/usr/bin/python3.7

## Programme d'envoie des données du  marégraphe KER3 a la Réunion toutes les 15 et/ou 30 minutes. 
## Executé par une cron toutes les 15min. voir crontab -l
## Lève une erreur si l'envoie du fichier n'a pas pu se faire, cette erreur est envoyé à la boite mail instrum@kerguelen.ipev.fr
## @author cc71 07/2021

#Envoie de mails officiels à la Réunion
import smtplib 
sender = 't2i@kerguelen.ipev.fr'
receivers = ['instrum@kerguelen.ipev.fr']
smtpSrvAddr = "smtp.kerguelen.ipev.fr"
smtpSrvPort = 25

import logging
import datetime

def sendMail(last30MinData,DateOfFirstData,myData) :
    now = datetime.datetime.now()
    dateForMail = now.strftime('%d%H%M')
    last30MinDataString = ' '.join(last30MinData)

    try:
        messageTemplate = """From: root <root@kerguelen.ipev.fr>
To: clement.crt@protonmail.com
Subject: {subject}

{entete} {crexHeaderDate}
CREX++
T000103 A001 D01021 D06019 R010{Rtag} B22038++
-4935250 07021850 FR023 {crexDataDate} //// 11 07 00 01
{dataLast30min}++
7777
"""
        messageMail = messageTemplate.format(subject=myData['template_mail_auto']['subject'],entete=myData['template_mail_auto']['header'],crexHeaderDate=dateForMail,Rtag=len(last30MinData),crexDataDate=DateOfFirstData,dataLast30min=last30MinDataString)
        smtpObj = smtplib.SMTP(smtpSrvAddr,smtpSrvPort)
        smtpObj.sendmail(sender, receivers, messageMail)         
        logging.info(str(now) + "Successfully sent email 30 CREX : ")
    except Exception as e: logging.exception('Unhandled Exception')
    return 1
