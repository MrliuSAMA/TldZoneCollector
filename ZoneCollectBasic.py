#coding=utf-8
import httplib
import time
import subprocess
import re
import socket
import os
import sched
import logging

server 		= 	"dummy"
zonedir		=	"dummy"
sigdir 		=	"dunmy"
storepathB	=	"dummy"
storepathT	=	"dummy"
period		=	"dummy"
Logpath		=	"dummy"

def pull():
	
#	print period
#	print server
#	print zonedir
#	print sigdir
#	print storepathB
#	print storepathT
#	print Logpath	
	
	HttpConn = httplib.HTTPConnection(server,80,timeout=60)
	HttpConn.request("GET",sigdir)
	Response = HttpConn.getresponse()
	RD = Response.read()
	filesigname = time.strftime("%F-%H:%M-")+sigdir.split('/')[-1]
	logging.info("fetch %s status:%s,%s"  % (filesigname, Response.status, Response.reason))
	HttpConn.close()

	FP = open("./tempfile/"+filesigname, "wb")
	FP.write(RD)
	FP.close()


	HttpConn = httplib.HTTPConnection(server,80,timeout=60)
	HttpConn.request("GET",zonedir)
	Response = HttpConn.getresponse()
	RD = Response.read()
	HttpConn.close()
	filedataname = time.strftime("%F-%H:%M-")+zonedir.split('/')[-1]

	logging.info("fetch %s status:%s,%s" % (filedataname, Response.status, Response.reason))
	FP = open("./tempfile/"+filedataname, "wb")
	FP.write(RD)
	FP.close()



	return filesigname,filedataname



def check_move(signame,dataname):
	print dataname
	print signame
	cmd = "gpg --verify ./tempfile/%s ./tempfile/%s" % (signame,dataname)
	logging.debug(cmd)
	sub = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	sub.wait()
	linelist = sub.stderr.readlines()
	res1 = re.search("Good signature",linelist[1])
	res2 = re.search("完好的签名",linelist[1])
	if res1 != None or res2 != None:
		logging.warning("zone file %s verified" % dataname)
 
		runcmd1 = "mv ./tempfile/%s %s%s" % (dataname,storepathB,dataname)
		logging.debug(runcmd1)
		sub1 = subprocess.Popen(runcmd1,shell=True)
		sub1.wait()

		runcmd2 = "mv ./tempfile/%s %s%s" % (signame,storepathB,signame)
		logging.debug(runcmd2)
		sub2 = subprocess.Popen(runcmd2,shell=True)
		sub2.wait()
	
		runcmd3 = "rm -f %s*.*" % storepathT
		logging.debug(runcmd3)
		sub3 = subprocess.Popen(runcmd3,shell=True)
		sub3.wait()
		
		runcmd4 = "cp %s%s %s%s" % (storepathB,dataname,storepathT,"root.zone.ori")
		logging.debug(runcmd4)
		sub4 = subprocess.Popen(runcmd4,shell=True)
		sub4.wait()

	else:
		logging.warning("zone file %s NOT verified" % dataname)

		runcmd1 = "rm -f ./tempfile/%s" % signame
		subprocess.Popen(runcmd1,shell=True)
		logging.debug(runcmd1)

		runcmd2 = "rm -f ./tempfile/%s" % dataname
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
			subprocess.Popen("rm -f ./tempfile/*.sig",shell=True)
			subprocess.Popen("rm -f ./tempfile/*.zone",shell=True)
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


def init():
	#read parameter
	global period
	global server
	global zonedir
	global sigdir
	global storepathB
	global storepathT
	global Logpath
	
	f = open("./Configuration.in",'r')
	filelines = f.readlines()
	period = filelines[0].strip().split()[-1]
	server = filelines[1].strip().split()[-1].split('/')[0]
	zonedir = filelines[1].strip().split()[-1][len(server):]
	sigdir = filelines[2].strip().split()[-1][len(server):]
	storepathB = filelines[3].strip().split()[-1]+filelines[4].strip().split()[-1]
	storepathT = filelines[3].strip().split()[-1]+filelines[5].strip().split()[-1]
	Logpath = filelines[3].strip().split()[-1]+filelines[6].strip().split()[-1]
	f.close()
	
	#import pgp publickey to key ring
	cmd			= "gpg --import PGPVarifyPublicKey"
	sub			= subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	sub.wait()

	#init Folder
	if os.path.exists(storepathB)==False:
		os.makedirs(storepathB)
	if os.path.exists(storepathT)==False:
		os.makedirs(storepathT)
	if os.path.exists(Logpath)==False:
		os.makedirs(Logpath)

	if os.path.exists("./tempfile")==True:
		subprocess.Popen("rm -f ./tempfile/*.*", shell=True)
	else:
		os.makedirs("./tempfile")

	#init logging mode
	logging.basicConfig(level = logging.DEBUG,\
					format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
					datefmt = '%a, %d %m %Y %H:%M:%S',\
					filename = "%s/run.log" % Logpath,\
					filemode = 'a')
	logging.info("############################ A New restart ############################")




if __name__ == "__main__":
	init()
	proc()	



