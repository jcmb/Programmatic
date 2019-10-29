#!/usr/bin/env python

import sys
import argparse
from pprint import pprint

import requests
import logging
import re
import datetime


Verbose=0

def process_args():

   parser = argparse.ArgumentParser(
               description='Trimble GNSS Receiver Backup',
               fromfile_prefix_chars='@',
               epilog="(c) JCMBsoft 2019")

   parser.add_argument("-U", "--User", default="admin", help="User Name, default:admin")
   parser.add_argument("-P", "--Password", default="password", help="User Name, default:password")
   parser.add_argument("--Host", required=True, help="GNSS Receiver IP")
   parser.add_argument("--Port", default=80, type=int, help="GNSS Receiver Port")
   parser.add_argument("-V", "--Verbose", action='count', help="Verbose level")
   parser.add_argument("-S", "--TLS", action="store_true", help="Connect using HTTPS/TLS")
   parser.add_argument("-E", "--Explain", action="store_true", help="System Should Explain what is is doing, AKA Verbose")
   parser.add_argument("--Restore", type=argparse.FileType('r'), help="Restore backup from a file")

   args=parser.parse_args()

   User = args.User
   Password = args.Password
   Host=args.Host
   Port=args.Port
   TLS=args.TLS
   Verbose=args.Verbose
   Restore=args.Restore!=None
   Restore_File=args.Restore

   if args.Explain:
       if Restore:
          sys.stderr.write("Restoring from: {}\n".format(
            Restore_File.name))
       else:
          sys.stderr.write("Backing Up\n")
       sys.stderr.write("GNSS Receiver: {}:{},  User: {}, Password: {} TLS: {} Verbose: {}\n".format(
           Host,
           Port,
           User,
           Password,
           TLS,
           Verbose))

   return (Host,Port,User,Password,TLS,Verbose,Restore,Restore_File)

def create_base_programmatic_URL (Host,Port,User,Password,TLS):

   if TLS :
      URL="https://"
   else:
      URL="http://"

   URL+=User
   URL+=":"
   URL+=Password
   URL+="@"
   URL+=Host
   URL+=":"
   URL+=str(Port)
   URL+="/prog/"
   return (URL)


def get_URL(Base_URL,item):
   global Verbose
   get_url=Base_URL+'show?'+item
   if Verbose >= 2:
      print get_url
   return get_url


def get_prog_item (Base_URL,item, info_only=False):
   r=requests.get(get_URL(Base_URL,item))
   if info_only:
      print "# "+ r.text.rstrip()
   else:
      print r.text.rstrip()
   return True

#def get_URL_port(Base_URL,port):
#   global Verbose
#   get_url=Base_URL+'show?ioPort&port='+port
#   if Verbose >= 2:
#      print get_url
#   return get_url

#def get_prog_port(Base_URL,port):
#   r=requests.get(get_URL_port(Base_URL,port))
#   print r.text
#   return True

def get_all_ports(Base_URL):
#   find_port = re.compile("IoPort port=(\w*)")
   r=requests.get(get_URL(Base_URL,"IoPorts"))
   lines=r.text.splitlines()

   if len(lines) == 0 :
      logging.error("Blank Reply to IoPorts")
      return (False)

   if lines[0] != "<Show IoPorts>" :
      logging.error("Reply to IoPorts doesn't start with <Show IoPorts>")
      return (False)
   else:
      del (lines[0])

   if lines[len(lines)-1] != "<end of Show IoPorts>" :
      logging.error("Reply to IoPorts doesn't end with <end of show IoPorts>")
      return (False)
   else:
      del(lines[len(lines)-1])


   for line in lines:
      print line
#      match = find_port.match(line)
#     if match:
#         get_prog_port(Base_URL,match.group(1))
#      else:
#         logging.error ("did not find port in line: "+ line)

#   print len(lines)
#   print(lines)

def get_all_sessions(Base_URL):
   r=requests.get(get_URL(Base_URL,"Sessions"))
   lines=r.text.splitlines()

   if len(lines) == 0 :
      logging.error("Blank Reply to IoPorts")
      return (False)

   if lines[0] != "<Show Sessions>" :
      logging.error("Reply to IoPorts doesn't start with <Show Sessions>")
      return (False)
   else:
      del (lines[0])

   if lines[len(lines)-1] != "<end of Show Sessions>" :
      logging.error("Reply to IoPorts doesn't end with <end of Show Sessions>")
      return (False)
   else:
      del(lines[len(lines)-1])

   for line in lines:
      print line.rstrip()




def Backup_Receiver(Host,Port,User,Password,TLS):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)

   print "# {}:{}".format(Host,Port)
   print "# "+str(datetime.datetime.now())
   get_prog_item(Base_URL,"SerialNumber",True)
   get_prog_item(Base_URL,"FirmwareVersion",True)

   get_prog_item(Base_URL,"ElevationMask")
   get_prog_item(Base_URL,"SystemName")
   get_prog_item(Base_URL,"PowerControls")
   get_prog_item(Base_URL,"UPS")
   get_prog_item(Base_URL,"RtkControls")
   get_prog_item(Base_URL,"ReferenceFrequency")
   get_prog_item(Base_URL,"PdopMask")
   get_prog_item(Base_URL,"ClockSteering")
   get_prog_item(Base_URL,"GpsSatControls")
   get_prog_item(Base_URL,"SbasSatControls")
   get_prog_item(Base_URL,"QzssSatControls")
#   get_prog_item(Base_URL,"IrnssSatControls")
#   get_prog_item(Base_URL,"PPS")
   get_prog_item(Base_URL,"Tracking")
   get_prog_item(Base_URL,"Antenna")
   get_prog_item(Base_URL,"MultipathReject")
   get_prog_item(Base_URL,"RefStation")
   get_prog_item(Base_URL,"RtkControls")
   get_prog_item(Base_URL,"GlonassSatControls")
#   get_prog_item(Base_URL,"Sessions")
#   get_prog_item(Base_URL,"Autodelete")
   get_all_sessions(Base_URL)
   get_all_ports(Base_URL)


def set_URL(Base_URL,item):
   global Verbose
   get_url=Base_URL+'set?'+item
   if Verbose >= 2:
      print get_url
   return get_url


def set_prog_item (Base_URL,item):
   r=requests.get(set_URL(Base_URL,item))
   if Verbose >= 1:
      print r.text.rstrip()
   return True


def Restore_Receiver(Host,Port,User,Password,TLS,Restore_File):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)

   for line in Restore_File:
      line=line.rstrip()
#      print line
      if len (line) == 0:
         continue
      if line[0] == "#":
         continue
      words=line.split()
      if Verbose >0 :
         if words[0]=="IoPort":
            sys.stderr.write(words[0]+" " + words[1] +"\n")
         else:
            sys.stderr.write(words[0]+"\n")
#      if len(words)==0: Can't happen since we checked for zero length above
      if words[0]=="Antenna":
#         print line
#         match=re.match('Antenna type=(\d+) name=".+" height=([0-9.]+) measMethod=(\w+) serial="(\w+)"',line)
         match=re.match('Antenna type=(\d+) name=".*" height=([0-9.]+) measMethod=(\w+) serial="(.*)"',line)
         if match:
#            print "matched"
            set_antenna="Antenna&type={}&height={}&measMethod={}&serial={}".format(
               match.group(1),
               match.group(2),
               match.group(3),
               match.group(4)
               )
#            print set_antenna
            logging.debug("Special antenna handling done: " + set_antenna)
            set_prog_item(Base_URL,set_antenna)
         else:
            logging.error("Special antenna handling FAILED")

      elif words[0]=="RefStation":
         print line
         match=re.match("RefStation lat=([-0-9.]+) lon=([-0-9.]+) height=([-0-9.]+) Rtcm2Id=(\w+) Rtcm3Id=(\w+) CmrId=(\w+) Name='(.*)' Code='(.*)'",line)
         if match:
#            print "matched"
            set_Ref="RefStation&lat={}&lon={}&height={}&Rtcm2Id={}&Rtcm3Id={}&CmrId={}&Name={}&Code={}".format(
               match.group(1),
               match.group(2),
               match.group(3),
               match.group(4),
               match.group(5),
               match.group(6),
               match.group(7),
               match.group(8)
               )
            print set_Ref
            logging.debug("Special RefStation handling done: " + set_Ref)
            set_prog_item(Base_URL,set_Ref)
         else:
            logging.error("Special Refstation handling FAILED")

      else:
         line=line.replace(" ","&")
         set_prog_item(Base_URL,line)


(Host,Port,User,Password,TLS,Verbose,Restore,Restore_File) = process_args()

if Restore:
   Restore_Receiver(Host,Port,User,Password,TLS,Restore_File)
else:
   Backup_Receiver(Host,Port,User,Password,TLS)


