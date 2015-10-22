#!/usr/bin/python

from __future__ import print_function
import re
import subprocess

ControlPREFIX = "/root/ZoneProject/RootZoneCollector/"
DataPREFIX = "/var/ZoneCollect/Data/ZoneGetBak/"

def ReturnConfig(ControlPREFIX,DataPREFIX,FileName = "Configuration.in"):
	f = open(ControlPREFIX+FileName, 'r')
	fileContent = f.read()
#	print (fileContent)
#	match = re.search(r"""(period\s*=\s*[0-9]*).		
#						  (ZoneDir\s*=\s*[a-zA-Z/\.\"]*).
#						  (SigDir\s*=\s*[a-zA-Z/\.\"]*).
#						  (Prefix\s*=\s*[a-zA-Z/\"]*).	
#						  (CurFilePath\s*=\s*[a-zA-Z/\"]*).
#						  (LogPath\s*=\s*[a-zA-Z/\"]*)""", 	
#						  fileContent,re.S|re.X)

	match = re.search(r"period\s*=\s*[0-9]*",fileContent)
	print ("period="+match.group().split()[-1]+',',end="\n")

	match = re.search(r"ZoneDir\s*=\s*[a-zA-Z/\.]*",fileContent)
	print ("ZoneDir="+match.group().split()[-1]+',',end="\n")

	match = re.search(r"SigDir\s*=\s*[a-zA-Z/\.]*",fileContent)
	print ("SigDir="+match.group().split()[-1]+',',end="\n")

#	print (match.group(2)+',',end="")
#	print (match.group(3)+',',end="")
#	print (match.group(4)+',',end="")
#	print (match.group(5)+',',end="")
#	print (match.group(6)+'$',end="")
	f.close()

	sub0 = subprocess.Popen("ls -lt -d %s*.zone" % DataPREFIX, stdout=subprocess.PIPE, shell=True)
	sub0.wait()
	reslines = sub0.stdout.readlines()
	print (reslines[1].split()[-1].split('/')[-1]+',',end="\n")
	print (reslines[2].split()[-1].split('/')[-1]+',',end="\n")
	print (reslines[3].split()[-1].split('/')[-1]+',',end="\n")
	sub1 = subprocess.Popen("ls -lt -d %s*.zone | wc -l" % DataPREFIX, stdout=subprocess.PIPE, shell=True)
	print (sub1.stdout.readlines()[0].strip()+',',end="\n")

	#print keys
	sub1 = subprocess.Popen("gpg --list-keys", stdout=subprocess.PIPE, shell=True)
	sub1.wait()	
	reslines = sub1.stdout.readlines()
	
	print (reslines[2].split()[1].split('/')[-1]+',',end="\n")
	url = "http://pgp.mit.edu/pks/lookup?search=0x%s&op=index" % reslines[2].split()[1].split('/')[-1]
	print (url+',',end="\n")
	print (reslines[3].split()[-1]+'$',end="\n")









if __name__ == "__main__":
	ReturnConfig(ControlPREFIX,DataPREFIX)
