import datetime
from datetime import datetime
import os

import parsedatetime
import pytz
from pytz import timezone

cal = parsedatetime.Calendar()



home_dir = os.path.expanduser('~')
home_dir = os.path.join(home_dir, 'PycharmProjects')
home_dir = os.path.join(home_dir, 'avec_google')
home_dir = os.path.join(home_dir, 'last_update.txt')


def to_date(str):
    str2 = str[0:19]
    answer = datetime.strptime(str2,"%Y-%m-%dT%H:%M:%S")
    return answer

if not os.path.exists(home_dir):
    fichier = open("last_update.txt", "w")
    fichier.write("2012-06-04T12:00:00-08:00")
    fichier.close()

def get():
    with open("last_update.txt","r") as fichier:
        #time_struct, parse_status = parsedatetime.Calendar().parse(fichier.read())
        #return datetime(*time_struct[:6])
        return "2012-06-04T12:00:00-08:00"

def update():
    fichier = open("last_update.txt", "w")
    fichier.write(str(datetime.utcnow()))
    fichier.close()