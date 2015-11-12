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

PREFIX = "/usr/local/RootZoneCollector"
PRINT = "yes"

server 		= 	"dummy"
zonedir		=	"dummy"
sigdir 		=	"dunmy"
storepathB	=	"dummy"
storepathT	=	"dummy"
period		=	"dummy"
Logpath		=	"dummy"
KeyPath		=	"dummy"


def pull():
	
	filesigname = time.strftime("%F-%H:%M-")+sigdir.split('/')[-1]	
	temp = "%s/tempfile/" % PREFIX
	cmd = "curl %s -o %s --retry-delay 10 --retry 10" % (sigdir,temp+filesigname)
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()

	filedataname = time.strftime("%F-%H:%M-")+zonedir.split('/')[-1]
	temp = "%s/tempfile/" % PREFIX
	cmd = "curl %s -o %s --retry-delay 10 --retry 10" % (zonedir,temp+filedataname)
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()


	return filesigname,filedataname



def check_move(signame,dataname):
#	print dataname
#	print signame
	
	cmd = "sudo gpg --verify %s/tempfile/%s %s/tempfile/%s" % (PREFIX,signame,PREFIX,dataname)
	logging.debug(cmd)
	sub = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	sub.wait()
	linelist = sub.stderr.readlines()
	res1 = re.search("Good signature",linelist[1])
	res2 = re.search("完好的签名",linelist[1])
	if res1 != None or res2 != None:
		logging.warning("zone file %s verified" % dataname)
 
		runcmd1 = "mv %s/tempfile/%s %s/%s" % (PREFIX,dataname,storepathB,dataname)
		logging.debug(runcmd1)
		sub1 = subprocess.Popen(runcmd1,shell=True)
		sub1.wait()

		runcmd2 = "mv %s/tempfile/%s %s/%s" % (PREFIX,signame,storepathB,signame)
		logging.debug(runcmd2)
		sub2 = subprocess.Popen(runcmd2,shell=True)
		sub2.wait()
	
		runcmd3 = "rm -f %s/*.*" % storepathT
		logging.debug(runcmd3)
		sub3 = subprocess.Popen(runcmd3,shell=True)
		sub3.wait()
		
		runcmd4 = "cp %s/%s %s/%s" % (storepathB,dataname,storepathT,"root.zone.ori")
		logging.debug(runcmd4)
		sub4 = subprocess.Popen(runcmd4,shell=True)
		sub4.wait()

	else:
		logging.warning("zone file %s NOT verified" % dataname)

		runcmd1 = "rm -f %s/tempfile/%s" % (PREFIX,signame)
		subprocess.Popen(runcmd1,shell=True)
		logging.debug(runcmd1)

		runcmd2 = "rm -f %s/tempfile/%s" % (PREFIX,dataname)
		subprocess.Popen(runcmd2,shell=True)
		logging.debug(runcmd2)


def proc():
	dataname	= "dummy"
	signame		= "dummy"
	while True:
		try:
			signame,dataname = pull()
		except socket.timeout,reason:
			logging.debug("fetchfile failed reason:%s" % reason)
			logging.debug("clear tempfle & try again!")
			subprocess.Popen("rm -f %s/tempfile/*.sig" % PREFIX,shell=True)
			subprocess.Popen("rm -f %s/tempfile/*.zone" % PREFIX,shell=True)
			continue
		else:
			break
	check_move(signame,dataname)


def perform_command(schedule,delay_s):
	schedule.enter(delay_s,0,perform_command,(schedule,delay_s))
	proc()

def timing_exe(delay = 300):
	schedule = sched.scheduler(time.time,time.sleep)
	schedule.enter(0,0,perform_command,(schedule,delay))
	schedule.run()

def ImportKey():
	cmd = "sudo gpg --import %s" % KeyPath
	sub = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
	sub.wait()
	res = sub.stderr.readlines() 
	if "not changed" in res[0] and PRINT == "yes":
		print "key already imported!"
	elif "imported" in res[0] and PRINT == "yes":
		print "key import successful"
			
	match = re.search(r"key\s([0-9A-Z]*)",res[0])
	if match != None:
		keyID = match.group(1)
		if PRINT == "yes":
			print keyID
		return keyID

def PromoteTrustkey(keyID):
	child = pexpect.spawn("sudo gpg --edit-key %s" % keyID)
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





def init():
	#read parameter
	global period
	global server
	global zonedir
	global sigdir
	global storepathB
	global storepathT
	global Logpath
	global KeyPath	

	f = open("%s/Configuration.in" % PREFIX,'r')
	filelines = f.readlines()
	period = filelines[0].strip().split()[-1]
	zonedir = filelines[1].strip().split()[-1]
	sigdir = filelines[2].strip().split()[-1]
	storepathB = "%s/%s" % (filelines[3].strip().split()[-1], filelines[4].strip().split()[-1])
	storepathT = "%s/%s" % (filelines[3].strip().split()[-1], filelines[5].strip().split()[-1])
	Logpath = "%s/%s" % (filelines[3].strip().split()[-1], filelines[6].strip().split()[-1])
	KeyPath = filelines[7].strip().split()[-1]

	f.close()
	
	#import pgp publickey to key ring
#	cmd			= "sudo gpg --import PGPVarifyPublicKey"
#	sub			= subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
#	sub.wait()
	KeyID = ImportKey()
	PromoteTrustkey(KeyID)

	#init Folder
	if os.path.exists(storepathB)==False:
		os.makedirs(storepathB)
	if os.path.exists(storepathT)==False:
		os.makedirs(storepathT)
	if os.path.exists(Logpath)==False:
		os.makedirs(Logpath)

	if os.path.exists("%s/tempfile" % PREFIX)==True:
		subprocess.Popen("rm -f %s/tempfile/*.*" % PREFIX, shell=True)
	else:
		os.makedirs("%s/tempfile" % PREFIX)

	#init logging mode
	logging.basicConfig(level = logging.DEBUG,\
					format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
					datefmt = '%a, %d %m %Y %H:%M:%S',\
					filename = "%s/run.log" % Logpath,\
					filemode = 'a')
	logging.info("############################ A New restart ############################")




if __name__ == "__main__":
	init()
	print "start periodic task!\n"
	timing_exe(int(period))
#	proc()	
#	pull()


