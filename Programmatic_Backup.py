#!/usr/bin/env -S python3 -u
#from __future__ import print_function

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
   parser.add_argument("--TestMode", help="Put the receiver into TestMode to do the backup/restore. Value provided is the test mode password")
   parser.add_argument("-R","--Restore", type=argparse.FileType('r'), help="Restore backup from a file")
   parser.add_argument("-O","--Output", type=argparse.FileType('w'), default="-", help="Save backup to file")

   args=parser.parse_args()

   User = args.User
   Password = args.Password
   Host=args.Host
   Port=args.Port
   TLS=args.TLS
   Verbose=args.Verbose
   if Verbose==None:
       Verbose=0
   Restore=args.Restore!=None
   Output_File=args.Output
   Restore_File=args.Restore
   TestMode=args.TestMode!=None
   if TestMode:
      TestMode_Password=args.TestMode
   else:
      TestMode_Password=""

   if args.Explain:
       if Restore:
          sys.stderr.write("Restoring from: {}\n".format(
            Restore_File.name))
       else:
          sys.stderr.write("Backing Up to {}\n".format(Output_File.name))
       sys.stderr.write("GNSS Receiver: {}:{},  User: {}, Password: {} TLS: {} Verbose: {}\n".format(
           Host,
           Port,
           User,
           Password,
           TLS,
           Verbose))

       sys.stderr.write("Test Mode: {}:{}\n".format(
           TestMode,
           TestMode_Password))



   return (Host,Port,User,Password,TLS,Verbose,Output_File,Restore,Restore_File,TestMode,TestMode_Password)

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
      sys.stderr.write(get_url)
      sys.stderr.write("\n")
   return get_url


def get_prog_item (Base_URL, Output_File, item, info_only=False):
   r=requests.get(get_URL(Base_URL,item))
   if info_only:
      print ("# "+ r.text.rstrip(),file=Output_File)
   else:
      if r.text.startswith("ERROR"):
         print ("# "+ r.text.rstrip(),file=Output_File)
      else:
         print (r.text.rstrip(),file=Output_File)
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

def get_all_ports(Base_URL,Output_File):
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
      print (line,file=Output_File)
#      match = find_port.match(line)
#     if match:
#         get_prog_port(Base_URL,match.group(1))
#      else:
#         logging.error ("did not find port in line: "+ line)

#   print len(lines)
#   print(lines)

def get_all_sessions(Base_URL,Output_File):
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
      print (line.rstrip(),file=Output_File)




def Backup_Receiver_Standard(Host,Port,User,Password,TLS,Output_File):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)

   print ("# {}:{}".format(Host,Port),file=Output_File)
   print ("# "+str(datetime.datetime.now()),file=Output_File)
   get_prog_item(Base_URL,Output_File,"SerialNumber",True)
   get_prog_item(Base_URL,Output_File,"FirmwareVersion",True)
   get_prog_item(Base_URL,Output_File,"firmwareWarranty",True)
   get_prog_item(Base_URL,Output_File,"SystemName")

   get_prog_item(Base_URL,Output_File,"ElevationMask")
   get_prog_item(Base_URL,Output_File,"SystemName")

   get_prog_item(Base_URL,Output_File,"PowerControls")
   get_prog_item(Base_URL,Output_File,"ChargingControls")
   get_prog_item(Base_URL,Output_File,"UPS")

   get_prog_item(Base_URL,Output_File,"ReferenceFrequency")
   get_prog_item(Base_URL,Output_File,"PdopMask")
   get_prog_item(Base_URL,Output_File,"ClockSteering")

   get_prog_item(Base_URL,Output_File,"GpsSatControls")
   get_prog_item(Base_URL,Output_File,"SbasSatControls")
   get_prog_item(Base_URL,Output_File,"QzssSatControls")
   get_prog_item(Base_URL,Output_File,"GlonassSatControls")
   get_prog_item(Base_URL,Output_File,"galileoSatControls")
   get_prog_item(Base_URL,Output_File,"BeiDouSatControls")
   get_prog_item(Base_URL,Output_File,"IrnssSatControls")
   get_prog_item(Base_URL,Output_File,"Tracking")
   get_prog_item(Base_URL,Output_File,"Antenna")
   get_prog_item(Base_URL,Output_File,"MultipathReject")
   get_prog_item(Base_URL,Output_File,"RefStation")
   get_prog_item(Base_URL,Output_File,"RtkControls")
   get_prog_item(Base_URL,Output_File,"PPS")
   get_prog_item(Base_URL,Output_File,"AutoReboot")
#   get_prog_item(Base_URL,Output_File,"NtpServer") Set only today
#   get_prog_item(Base_URL,Output_File,"Autodelete")  Set only today
   get_all_sessions(Base_URL,Output_File)
   get_all_ports(Base_URL,Output_File)


def Backup_Receiver_TestMode_Only(Host,Port,User,Password,TLS):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)
   get_prog_item(Base_URL,"Security",True)

   get_prog_item(Base_URL,"FtpPush",True) #Need to fix the directory stuff.
   get_prog_item(Base_URL,"EmailAlerts")
   get_prog_item(Base_URL,"HttpPorts")
#   get_prog_item(Base_URL,"PPP")
   get_prog_item(Base_URL,"Ethernet",True) #Needs mac=00:60:35:10:33:84 removed
   get_prog_item(Base_URL,"NtripClient",True) # Needs port removed
# Note that NTRIP only supports 1 item, but it is better than nothing
   get_prog_item(Base_URL,"NtripServer")
   get_prog_item(Base_URL,"Omnistar")
   get_prog_item(Base_URL,"SystemMode")
   get_prog_item(Base_URL,"HeadingControls")
#   get_prog_item(Base_URL,"sessions")


def set_URL(Base_URL,item):
   global Verbose
   get_url=Base_URL+'set?'+item
   if Verbose >= 2:
      sys.stderr.write(get_url)
      sys.stderr.write("\n")
   return get_url


def set_prog_item (Base_URL,item):
   r=requests.get(set_URL(Base_URL,item))
   if Verbose >= 1:
      print (r.text.rstrip())
   return True


def Restore_Receiver(Host,Port,User,Password,TLS,Restore_File,TestMode,TestMode_Password):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)

   Need_to_Unset=False

   if In_Test_Mode (Host,Port,User,Password,TLS):
      Need_to_Unset=False
   else:
      if TestMode:
         if Verbose>=1:
            sys.stderr.write("Putting the unit in Test Mode\n")
         if Set_TestMode(Host,Port,User,Password,TLS):
            if Verbose>=1:
               sys.stderr.write("Unit put in Test Mode\n")
      #         if In_Test_Mode (Host,Port,User,Password,TLS):
            Need_to_Unset=True

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
         if not match:
           match=re.match("Antenna type=(\d+) name='.*' height=([0-9.]+) measMethod=(\w+) serial='(.*)'",line)
#
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
#         print (line)
         match=re.match("RefStation lat=([-0-9.]+) lon=([-0-9.]+) height=([-0-9.]+) Rtcm2Id=(\w+) Rtcm3Id=(\w+) CmrId=(\w+) RtxStnId=.* Name='(.*)' Code='(.*)'",line)

         if not match:
             match=re.match("RefStation lat=([-0-9.]+) lon=([-0-9.]+) height=([-0-9.]+) Rtcm2Id=(\w+) Rtcm3Id=(\w+) CmrId=(\w+) Name='(.*)' Code='(.*)'",line)

         if match:
#            print ("matched")
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
#            print set_Ref
            logging.debug("Special RefStation handling done: " + set_Ref)
            set_prog_item(Base_URL,set_Ref)
         else:
            logging.error("Special Refstation handling FAILED")

      else:
         line=line.replace(" ","&")
         set_prog_item(Base_URL,line)


   if Need_to_Unset:
      Unset_TestMode(Host,Port,User,Password,TLS)
      if Verbose>=1:
         sys.stderr.write("Taking the unit out of Test Mode\n")


def In_Test_Mode(Host,Port,User,Password,TLS):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)
   get_url=Base_URL+'show?TestMode'
   r=requests.get(get_url)
   return r.text.rstrip()=="testMode enable=yes"

def Set_TestMode(Host,Port,User,Password,TLS):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)
   get_url=Base_URL+'set?testMode&enable=yes&password='+TestMode_Password
   r=requests.get(get_url)
   return r.text.rstrip()=="OK: testMode enable=yes"

def Unset_TestMode(Host,Port,User,Password,TLS):
   Base_URL=create_base_programmatic_URL (Host,Port,User,Password,TLS)
   set_url=Base_URL+'set?testMode&enable=no'
#   if Verbose >= 2:
#      print get_url
   r=requests.get(set_url)
#   print r.text.rstrip()


(Host,Port,User,Password,TLS,Verbose,Output_File,Restore,Restore_File,TestMode,TestMode_Password) = process_args()

if Restore:
   Restore_Receiver(Host,Port,User,Password,TLS,Restore_File,TestMode,TestMode_Password)
else:
   Backup_Receiver_Standard(Host,Port,User,Password,TLS,Output_File)
   if In_Test_Mode (Host,Port,User,Password,TLS):
      Backup_Receiver_TestMode_Only(Host,Port,User,Password,TLS)
   else:
      if TestMode:
         if Verbose>=1:
            sys.stderr.write("Putting the unit in Test Mode\n")
         if Set_TestMode(Host,Port,User,Password,TLS):
            if Verbose>=1:
               sys.stderr.write("Unit put in Test Mode\n")
#         if In_Test_Mode (Host,Port,User,Password,TLS):
            Backup_Receiver_TestMode_Only(Host,Port,User,Password,TLS)
            Unset_TestMode(Host,Port,User,Password,TLS)
            if Verbose>=1:
               sys.stderr.write("Taking the unit out of Test Mode\n")



