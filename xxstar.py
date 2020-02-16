#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

# Copyright (C) 2020 nbenm <nb@dagami.org>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; see the file COPYING. If not, write to the
#    Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Copyright (C) 2020 nbenm <nb@dagami.org>
#     Ce programme est un logiciel libre: vous pouvez le redistribuer
#     et/ou le modifier selon les termes de la "GNU General Public
#     License", tels que publiés par la "Free Software Foundation"; soit
#     la version 2 de cette licence ou (à votre choix) toute version
#     ultérieure.
# 
#     Ce programme est distribué dans l'espoir qu'il sera utile, mais
#     SANS AUCUNE GARANTIE, ni explicite ni implicite; sans même les
#     garanties de commercialisation ou d'adaptation dans un but spécifique.
# 
#     Se référer à la "GNU General Public License" pour plus de détails.
# 
#     Vous devriez avoir reçu une copie de la "GNU General Public License"
#     en même temps que ce programme; sinon, écrivez a la "Free Software
#     Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA".

import serial
import sys
import getopt
import datetime

usage="""
usage:
%s [-d] [-s] [-u] [-a] [-h]
-d: Debug mode. Permet d'afficher les requêtes et tout le contenu du lecteur avec les secondes
    Ne tient pas compte du fichier xxstar.last, et ne le modifie pas
-s: Simulation. Affiche toutes les mesures nouvelles, mais ne modifie pas xxstar.last
-u: Update. Affiche toutes les mesures nouvelles, et modifie xxstar.last
-a: All. Affiche toutes les mesures mais ne modifie pas xxstar.last
-h: help

-d et -s sont exclusifs l'un de l'autre
""" % sys.argv[0]

debug=False
simul=False
update=False
all=False
updlast=False

try:
    opts, args = getopt.getopt(sys.argv[1:],"dsuah")
except getopt.GetoptError as err:
    sys.stderr.write(usage)
    sys.exit(1)

for opt,arg in opts:
  if opt == '-d':
    debug = True
  if opt == '-s':
    simul = True
  if opt == '-u':
    update = True
  if opt == '-a':
    all = True
  if opt == '-h':
    sys.stderr.write(usage)
    sys.exit(2)
if debug and simul:
    sys.stderr.write(usage)
    sys.exit(3)

def requestDevice(req, rep_partielle):
  ser.write(req)
  response=ser.readline()
  if not response.startswith(rep_partielle) or not response.endswith(b'\r\n'):
    print ('Le dispositif ne répond pas à la requête: %s' % (req.decode('utf-8')))
    sys.exit(4)
  response=response.strip()
  return response

try:
  ser = serial.Serial(port='/dev/cu.SLAB_USBtoUART', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5, rtscts=False, dsrdtr=False)
except serial.serialutil.SerialException as err:
  print ('Le Port série /dev/cu.SLAB_USBtoUART ne répond pas, on essaye /dev/ttyUSB0')
  try:
    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5, rtscts=False, dsrdtr=False)
  except serial.serialutil.SerialException as err:
    print ('Le Port série /dev/ttyUSB0 ne répond pas non plus, on sort')
    sys.exit(5)


last = None
f = open("xxstar.last","rb")
last = f.readline().strip()

req=b'hello\r'
rep_partielle=b'200 hello '
response=requestDevice(req, rep_partielle)

#req=b'get serial\r'
#rep_partielle=b'200 serial '
#response=requestDevice(req, rep_partielle)
#serial=response.split()[2]
#if serial != b'XXXXXXXXXXXXXX':
#  print ("Le dispositif n'est pas le BG*STAR attendu")
#  sys.exit(6)

# On met à jour la date et l'heure sur le lecteur de glycémie
req='set datetime '
now='{dt.year} {dt.month} {dt.day} {dt.hour} {dt.minute} {dt.second}'.format(dt = datetime.datetime.now()) + '\r'
req = req.encode('utf-8') + now.encode('utf-8')
rep_partielle=b'200 datetime '
print("Mise à jour de l'horloge: {!s}\n".format(now))
response=requestDevice(req, rep_partielle)

req=b'get glucount\r'
rep_partielle=b'200 glucount '
response=requestDevice(req, rep_partielle)
nombre=int(response.split()[2])

d={}
for i in range(0, nombre-1):
  req=b'get glurec %d\r' % (i)
  rep_partielle=b'200 glurec %d ' % (i)
  response=requestDevice(req, rep_partielle)
  xpl=response.split()
  date_heure=b'%s-%02d-%02d %02d:%02d:%02d' % \
    (xpl[6],int(xpl[7]),int(xpl[8]),int(xpl[9]),int(xpl[10]),int(xpl[11]))
  glyc=xpl[4]
  if glyc.startswith(b'E'):
    print ('erreur le %s, valeur:%s. On ignore cette mesure'
          % (date_heure.decode('utf-8'), glyc.decode('utf-8')))
    continue
  else:
    glyc=int(xpl[4])
  type_glyc=int(xpl[5])
  if date_heure[0:16] <= last:
    if debug or all:
      d[date_heure[0:16].decode('utf-8')] = [glyc,type_glyc,req,response]
    else:
      break
  else:
    updlast = True
    d[date_heure[0:16].decode('utf-8')] = [glyc,type_glyc,req,response]

for dt in sorted(d.keys()):
  if debug:
    # print req and response
    print ('\n' + d[dt][2].decode('utf-8'))
    print (d[dt][3].decode('utf-8'))
  print (dt, d[dt][0], d[dt][1], '\"\"')

if update and updlast:
  f = open("xxstar.last","w")
  f.write(dt + '\n')
