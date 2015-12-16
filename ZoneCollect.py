#coding=utf-8
import httplib
import time
import subprocess
import re
import socket
import os
import sched
import logging
import pexpect
import pprint
import sys
import getpass
import getopt
import json



def init_pgpkey(KeyPath):
	logging.debug("enter function init_pgpkey()")
	#init and promote pgp keys , to possess pub-key an ultimate
	keyID = ImportKey(KeyPath)
	PromoteTrustkey(keyID)
	return None



def init_directory(Prefix, BackupFolder, FinalFolder, LogPath):
	#init_directory must not use logging , because logging module install in init_logging()
	#init necessary directory


	#init data directory
	currentUser = getpass.getuser()
	if os.path.exists(BackupFolder)==False:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
				 % (BackupFolder, currentUser, Prefix, currentUser, Prefix, Prefix)  
		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()

	if os.path.exists(FinalFolder)==False:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
				 % (FinalFolder, currentUser, Prefix, currentUser, Prefix, Prefix)  
		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()

	if os.path.exists(LogPath)==False:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
				 % (LogPath, currentUser, Prefix, currentUser, Prefix, Prefix)  
		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()

	#init tempfile directory
	if os.path.exists("/tmp/root-zone-collector")==True:
		cmdstring = "rm -f /tmp/root-zone-collector/*.*"
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()
	else:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
			% ("/tmp/root-zone-collector", currentUser, "/tmp/root-zone-collector", \
				currentUser,"/tmp/root-zone-collector", "/tmp/root-zone-collector")
		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)	
		sub.wait()


	return  None



def init_logging(LogPath):
	#logging.debug("enter function init_logging")
	#install logging module
	logging.basicConfig(
			level = logging.DEBUG, \
			format = '%(asctime)s %(filename)s[line:%(lineno)4d] %(levelname)-8s %(message)s', \
			datefmt = '%Y-%m-%d %H:%M:%S', \
			filename = "%s/run.log" % LogPath, \
			filemode = 'a')
	logging.info('#'*30 + "A New restart:")	




def init(Prefix, BackupFolder, FinalFolder, LogPath, KeyPath):
	#total initial work
	#logging mudole initialize must done before use
	init_directory(Prefix, BackupFolder, FinalFolder,LogPath)

	init_logging(LogPath)

	init_pgpkey(KeyPath)



def pull(ZoneFileServerpath, SigFileServerpath):
	logging.debug("enter function pull()")
	#download zonedata and zonesig from remote server
	timeString = time.strftime("%F_%T_")

	sigFile = timeString+SigFileServerpath.split('/')[-1]	
	tempdir = "/tmp/root-zone-collector"
	cmdstring = "curl %s -s -o %s/%s --retry-delay 60 --retry 3" % (SigFileServerpath, tempdir, sigFile)
	sub = subprocess.Popen(cmdstring, shell=True)
	sub.wait()
	sigReturnCode = sub.returncode

	zoneFile = timeString+ZoneFileServerpath.split('/')[-1]
	tempdir = "/tmp/root-zone-collector"
	cmdstring = "curl %s  -s -o %s/%s --retry-delay 60 --retry 3" % (ZoneFileServerpath, tempdir, zoneFile)
	sub = subprocess.Popen(cmdstring, shell=True)
	sub.wait()
	dataReturnCode = sub.returncode


	logDict = {};
	logDict["DataSource"] = ZoneFileServerpath
	logDict["FetchTime"] = time.strftime("%F_%T")
	logFile = timeString+"root.zone.log"
	fp= open("%s/%s" % (tempdir,logFile) ,"w")
	json.dump(logDict, fp, indent=4, sort_keys=True)
	fp.close() 



	
	
	# f.write("DataSource = %s\n" % ZoneFileServerpath)
	# f.write("FetchTime = %s\n" % time.strftime("%F_%T"))
	# f.close()

	return sigFile,zoneFile,logFile,sigReturnCode,dataReturnCode




def check_move(SigFile, DataFile, LogFile, BackupFolder, FinalFolder):
	logging.debug("enter function check_move()")
	#use gpg varify downloaded file
	tempdir = "/tmp/root-zone-collector"
	cmd = "gpg --verify /tmp/root-zone-collector/%s /tmp/root-zone-collector/%s" % (SigFile,DataFile)
	logging.info(cmd)
	sub = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	sub.wait()
	linelist = sub.stderr.readlines()
	res1 = re.search("Good signature",linelist[1])
	res2 = re.search("完好的签名",linelist[1])
	if res1 != None or res2 != None:
		logging.info("zone file %s verified" % DataFile)
 		
 		#move downloaded file to backup folder
		runcmd = "mv -t %s %s/%s %s/%s %s/%s"  \
				% (BackupFolder, tempdir, DataFile, tempdir, SigFile, tempdir, LogFile)
		logging.info(runcmd)
		sub = subprocess.Popen(runcmd, shell=True)
		sub.wait()
		if sub.returncode != 0:
			logging.warning("move downloaded file to backup folder failed")
	
		#clear final folder
		runcmd = "rm -f %s/root.zone.ori" % FinalFolder
		logging.info(runcmd)
		sub = subprocess.Popen(runcmd, shell=True)
		sub.wait()
		if sub.returncode != 0:
			logging.warning("clear final folder failed")

		#move files from backupfolder to finalfolder
		runcmd = "cp %s/%s %s/%s" % (BackupFolder, DataFile, FinalFolder, "root.zone.ori")
		logging.info(runcmd)
		sub = subprocess.Popen(runcmd, shell=True)
		sub.wait()
		if sub.returncode != 0:
			logging.warning("move data_files from backupfolder to finalfolder failed")

		runcmd = "cp %s/%s %s/%s" % (BackupFolder, LogFile, FinalFolder, "root.zone.log")
		logging.info(runcmd)
		sub = subprocess.Popen(runcmd, shell=True)
		sub.wait()
		if sub.returncode != 0:
			logging.warning("move log_files from backupfolder to finalfolder failed")

	else:
		logging.warning("zone file %s NOT verified" % DataFile)

		#varify failed so clear tempfile folder 
		runcmd = "rm -f %s/%s ; rm -f %s/%s" % (tempdir, SigFile, tempdir, DataFile)
		logging.info(runcmd)
		sub = subprocess.Popen(runcmd1,shell=True)
		sub.wait()
		if sub.returncode != 0:
			logging.warning("clear tempfile folder failed")



def proc(ZoneFileServerpath, SigFileServerpath, BackupFolder, FinalFolder):
	logging.debug("enter function proc()")
	#program's entry point	
	sigFile,dataFile,logFile,code0,code1 = pull(ZoneFileServerpath, SigFileServerpath)
	if code0 == 0 and code1 == 0:
		logging.info("file download and write to file successful")

	elif code0 == 23 or code1 == 23:
		logging.warning("write downloaded file failed")
		logging.info("rm -f /tmp/root-zone-collector/*.*")
		subprocess.Popen("rm -f /tmp/root-zone-collector/*.*", shell=True)
		sys.exit(1)
	elif code0 ==6 or code1 == 6:
		logging.warning("unable to resolve the host")
		sys.exit(1)
	else:
		logging.warning("unexpected error occured")
		sys.exit(1)

	check_move(sigFile, dataFile, logFile, BackupFolder, FinalFolder)



def ImportKey(Keypath):
#	print Keypath
	logging.debug("enter function ImportKey()")
	#inport public-pgp-key from file to key-ring(in memory)
	cmd = "gpg --import %s" % Keypath
	sub = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
	sub.wait()
	res = sub.stderr.readlines() 
#	pprint.pprint(res)
	if "not changed" in res[0] or "未改变" in res[0]:
		logging.info("key already exist[repeated import]")
#		print "key already imported!"

	elif "imported" in res[0] or "已导入" in res[0]:
		logging.info("key import successful")
#		print "key import successful"
			
	match = re.search(r"key\s([0-9A-Z]*)",res[0])
	if match != None:
		keyID = match.group(1)
		logging.info("key id : %s" % keyID)
#		print keyID
		return keyID
	else:
		logging.warning("can't find key file")
		sys.exit(1)



def PromoteTrustkey(KeyID):
	logging.debug("enter function PromoteTrustkey()")
	#To possess pub-key an ultimate
	child = pexpect.spawn("gpg --edit-key %s" % KeyID)
	except_list = ["Command> ","Your decision\? ","\(y/N\) "]

	index = child.expect(except_list)
	if index == 0:
		child.sendline("trust")	
	index = child.expect(except_list)
	if index == 1:
		child.sendline("5")
	index = child.expect(except_list)
	if index == 2:
		child.sendline("y")
	index = child.expect(except_list)
	if index == 0:
		child.sendline("quit")

	return None



def extractParameter(ConfigurationFile):
	#logging.debug("enter function extractParameter()")
	#read file configuration and return parameters to program
	if ConfigurationFile == "dummy":
		ConfigurationFile = "./Configuration.in"

	#f = open("%s/Configuration.in" % PREFIX,'r')
	f = open(ConfigurationFile, 'r')
	fileContent = f.read()
	f.close()

	period = re.search("Period\s*=\s*([0-9]*)", fileContent, re.M).group(1)
	zonedir = re.search("ZoneDir\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)
	sigdir = re.search("SigDir\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)
	prefix = re.search("Prefix\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)
	backupfilepath = re.search("BackupFilePath\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)
	truefilepath = re.search("CurFilePath\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)
	logpath = re.search("LogPath\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)
	keypath = re.search("KeyPath\s*=\s*([a-zA-Z0-9\./]*)", fileContent, re.M).group(1)


	return (period, zonedir, sigdir, prefix,prefix+'/'+backupfilepath, prefix+'/'+truefilepath,	\
		prefix+'/'+logpath, keypath)



def perform_command(schedule,delay,ZoneFileDir,SigFileDir,BackupFolder,FinalFolder):
	logging.debug("enter function perform_command()")
	schedule.enter(delay,0,perform_command,(schedule,delay,ZoneFileDir,SigFileDir,BackupFolder,FinalFolder))
	proc(ZoneFileDir,SigFileDir,BackupFolder,FinalFolder)



def timing_exe(delay,ZoneFileDir,SigFileDir,BackupFolder,FinalFolder):
	logging.debug("enter function timing_exe()")
	schedule = sched.scheduler(time.time,time.sleep)
	schedule.enter(0,0,perform_command,(schedule,delay,ZoneFileDir,SigFileDir,BackupFolder,FinalFolder))
	schedule.run()



def usage():
	logging.debug("enter function usage()")
	print "\t\tUsage:%s [-c|-p|-b]" % sys.argv[0]
	print "\t-c  assign configuration file path[default path : ./configuration]"
	print "\t-p  execute program with period"
	print "\t-b  execute program once[default choice]"



if __name__ == "__main__":
	#deal with parameter 

	configurationFilePath = "dummy"
	periodTime = "dummy"
	ifOnce = "yes"

	try:
		opts,args = getopt.getopt(sys.argv[1:], "hbp:c:")
	except getopt.GetoptError,info:
		print info.msg
		usage()
		sys.exit()

#	pprint.pprint(opts)
	for option,value in opts:
		if option in ("-b"):
			ifOnce = "yes"
		elif option in ("-h"):
			usage()
			sys.exit()
		elif option in ("-p"):
			ifOnce = "no"
			periodTime = value
		elif option in ("-c"):
			configurationFilePath = value
		else:
			usage()
			sys.exit()

	res = extractParameter(configurationFilePath)

	period = res[0]
	zoneFileDir = res[1]
	sigFileDir = res[2]
	prefix = res[3]
	backupFolder = res[4]
	finalFolder = res[5]
	logPath = res[6]
	keyPath = res[7]
	init(prefix, backupFolder, finalFolder, logPath, keyPath)


	if ifOnce == "yes":
		proc(zoneFileDir, sigFileDir, backupFolder, finalFolder)
	else:
		if periodTime == "dummy":
			periodTime = period
		timing_exe(int(periodTime), zoneFileDir,sigFileDir,backupFolder, finalFolder )	



