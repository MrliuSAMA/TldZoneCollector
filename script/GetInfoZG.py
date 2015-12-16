#!/usr/bin/python

from __future__ import print_function
import re
import subprocess
import os
import sys
import pprint





def ReturnInfo_parameter(ConfigureFile):
	#get configure file parameter
	f = open(ConfigureFile, 'r')
	fileContent = f.read()

	match = re.search(r"Period\s*=\s*[0-9]*", fileContent)
	print ("period="+match.group(0).split()[-1]+',', end="\n")
	match = re.search(r"ZoneDir\s*=\s*[a-zA-Z/\.:]*", fileContent)
	print ("ZoneDir="+"http://"+match.group(0).split()[-1]+',', end="\n")
	match = re.search(r"SigDir\s*=\s*[a-zA-Z/\.:]*", fileContent)
	print ("SigDir="+"http://"+match.group(0).split()[-1]+',', end="\n")
	match = re.search(r"Prefix\s*=\s*[a-zA-Z/\.]*", fileContent)
	prefix = match.group(0).split()[-1]
	match = re.search(r"LogPath\s*=\s*[a-zA-Z/\.]*", fileContent)
	logpath = match.group().split()[-1]
	print ("Logpath="+prefix+'/'+logpath+'/run.log'+',', end="\n")
	match = re.search(r"BackupFilePath\s*=\s*[a-zA-Z/\.]*", fileContent)
	datapath = match.group().split()[-1]
	print ("DataPath="+prefix+'/'+datapath+',', end="\n")

	f.close()
	DataPath = "%s/%s" % (prefix, datapath)


	return  DataPath



def ReturnInfo_files(DataPath):
	#get information of downloaded file
	cur_path = os.getcwd()
	compare_path = DataPath
	os.chdir(compare_path)

	files= os.listdir(DataPath)
	zone_files = [x for x in files if x.endswith("zone")]
	zone_files.sort(cmp = compare_time, reverse = True)

	num_counter = 0
	while(num_counter < min(3,len(zone_files))):
		print (zone_files[num_counter]+',', end="\n")
		num_counter = num_counter + 1



def ReturnInfo_pid():
	#get information of running process
	cmd = "ps -ef | grep ZoneCollect.py"
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
#	pprint.pprint(reslines)
	judge_ifrun = 0
	for lines in reslines:
		if lines.split()[7].startswith("grep"):
			continue
		if lines.split()[7].startswith("python") or lines.split()[7].startswith("ZoneCollect"):
			print ("pid=%s," % lines.split()[1], end="\n")
			judgeifrun = 1
			break
	if judge_ifrun == 0:
		print ("pid=0,", end="\n")	



def ReturnInfo_key(ConfigureFile):
	#get information of imported public key
	key_dir = os.path.dirname(ConfigureFile)
	f = open("%s/%s" %(key_dir, "PGPVarifyPublicKey.pub"))
	lines = f.readlines()
	print ("PGPKEY="+lines[4]+',',end="\n")
	f.close()

	sub = subprocess.Popen("gpg --list-keys", stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()	
	print (reslines[2].split()[1].split('/')[-1]+',', end="\n")
	url = "http://pgp.mit.edu/pks/lookup?search=0x%s&op=index" % reslines[2].split()[1].split('/')[-1]
	print (url+',', end="\n")
	print (reslines[3].split()[-1]+'$',end="\n")	



def compare_time(file_x, file_y):
	#internal called function
	stat_x = os.stat(file_x)
	stat_y = os.stat(file_y)
	if stat_x.st_mtime < stat_y.st_mtime:
		return -1
	elif stat_x.st_mtime > stat_y.st_mtime:
		return 1
	else:
		return 0



def ReturnInfo(ConfigureFile):

	DataFolder = ReturnInfo_parameter(ConfigureFile)

	ReturnInfo_files(DataFolder)

	ReturnInfo_pid()

	ReturnInfo_key(ConfigureFile)



if __name__ == "__main__":
	#enter point
	ConfigureFile = "/usr/local/RootZoneCollector/Configuration.in"

	ReturnInfo(ConfigureFile)
