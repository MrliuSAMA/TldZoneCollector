#!/usr/bin/python

from __future__ import print_function
import re
import subprocess

ControlPREFIX = "/usr/local/RootZoneCollector/"
DataPREFIX = "/var/ZoneCollect/Data/ZoneGetBak/"

def ReturnConfig(ControlPREFIX,DataPREFIX,FileName = "Configuration.in"):

	#print configures
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

	match = re.search(r"ZoneDir\s*=\s*[a-zA-Z/\.:]*",fileContent)
	print ("ZoneDir="+"http://"+match.group().split()[-1]+',',end="\n")

	match = re.search(r"SigDir\s*=\s*[a-zA-Z/\.:]*",fileContent)
	print ("SigDir="+"http://"+match.group().split()[-1]+',',end="\n")

	match = re.search(r"Prefix\s*=\s*[a-zA-Z/\.]*",fileContent)
	prefix = match.group().split()[-1]
	match = re.search(r"LogPath\s*=\s*[a-zA-Z/\.]*",fileContent)
	logpath = match.group().split()[-1]
	print ("Logpath="+prefix+logpath+'/run.log'+',',end="\n")
	f.close()


	#print files
	sub0 = subprocess.Popen("ls -lt -d %s*.zone | head -n 10 " % DataPREFIX, stdout=subprocess.PIPE, shell=True)
	sub0.wait()
	reslines = sub0.stdout.readlines()
	if len(reslines) > 0 and len(reslines) < 2:
		print (reslines[0].split()[-1].split('/')[-1]+',',end="\n")
	elif len(reslines) > 0 and len(reslines) < 3:
		print (reslines[0].split()[-1].split('/')[-1]+',',end="\n")		
		print (reslines[1].split()[-1].split('/')[-1]+',',end="\n")
	elif len(reslines) > 3:
		print (reslines[0].split()[-1].split('/')[-1]+',',end="\n")		
		print (reslines[1].split()[-1].split('/')[-1]+',',end="\n")
		print (reslines[3].split()[-1].split('/')[-1]+',',end="\n")
	else:
		pass
	sub1 = subprocess.Popen("ls -lt -d %s*.zone | wc -l" % DataPREFIX, stdout=subprocess.PIPE, shell=True)
	print (sub1.stdout.readlines()[0].strip()+',',end="\n")

	#print pid
	cmd = 'ps -ef | grep "python %sZoneCollect"'%ControlPREFIX
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	judgeifrun = 0
	for lines in reslines:
		if lines.split()[2] == '1':
			print ("pid=%s," % lines.split()[1])
			judgeifrun = 1
			break
	if judgeifrun == 0:
		print ("pid=0,")



	#print keys
	f = open(ControlPREFIX+"PGPVarifyPublicKey.pub")
	lines = f.readlines()
	print ("PGPKEY="+lines[4]+',',end="\n")	

	sub1 = subprocess.Popen("gpg --list-keys", stdout=subprocess.PIPE, shell=True)
	sub1.wait()	
	reslines = sub1.stdout.readlines()
	
	print (reslines[2].split()[1].split('/')[-1]+',',end="\n")
	url = "http://pgp.mit.edu/pks/lookup?search=0x%s&op=index" % reslines[2].split()[1].split('/')[-1]
	print (url+',',end="\n")
	print (reslines[3].split()[-1]+'$',end="\n")









if __name__ == "__main__":
	ReturnConfig(ControlPREFIX,DataPREFIX)
