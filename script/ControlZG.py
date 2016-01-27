from __future__ import print_function
import getopt
import sys
import re
import getopt
import subprocess
import time
import os

#ControlPREFIX = "/opt/TLDCollect/RootZoneCollector/"

def startService(ControlPREFIX):
	#start ZoneCollect.py process
	#f = open("/tmp/loglog.txt","w")
	cmd = 'ps -ef | grep ZoneCollect.py'
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	judge_ifrun = 0
	for lines in reslines:
		if lines.split()[7].startswith("grep"):
			continue
		if lines.split()[7].startswith("python") or lines.split()[7].startswith("ZoneCollect"):
			print ("program already start")
			print ("pid=%s" % lines.split()[1], end="\n")
			judge_ifrun = 1
			break

	#if process not start, then start
	if judge_ifrun == 1:
		return None
	elif judge_ifrun == 0:
		cmd_run = "python %s/ZoneCollect.py -c /opt/TLDCollect/TLDCollector/Configuration.in -p 0" % ControlPREFIX
		#cmd_run = "python %s/ZoneCollect.py -c /opt/TLDCollect/TLDCollector/Configuration.in &" % ControlPREFIX
		#f.write("1231231232\n")
		#f.close()
		#print ("123123123")
		#cmd_run = "ls &"
		#print (cmd_run)
		#os.system(cmd_run)
		sub_run = subprocess.Popen(cmd_run, shell=True)
		sub_run.wait()
		#f = open("/tmp/loglog.txt","a")
		#f.write("456456456\n")
		#f.close()
#		time.sleep(2)

		sub_check = subprocess.Popen('ps -ef | grep ZoneCollect.py', stdout=subprocess.PIPE, shell=True)
		sub_check.wait()
		reslines = sub_check.stdout.readlines()
		for lines in reslines:
			if lines.split()[7].startswith("grep"):
				continue
			if lines.split()[7].startswith("python") or lines.split()[7].startswith("ZoneCollect"):
				print ("pid=%s," % lines.split()[1], end="\n")
				break

		return None

		
def stopService(ControlPREFIX):
	cmd = "ps -ef | grep ZoneCollect.py"
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	pid = "dummy"

	for lines in reslines:
		if lines.split()[7].startswith("grep"):
			continue
		if lines.split()[7].startswith("python") or lines.split()[7].startswith("ZoneCollect"):
			pid = lines.split()[1]
			print ("pid=%s," % lines.split()[1], end="\n")

 	if pid == "dummy":
 		print ("No progress running")
 	else:
		sub = subprocess.Popen("kill -9 %s" % pid, shell=True)
		sub.wait()



def updateConfiguration(ControlPREFIX,value):
	items = value.strip().split(',')
	f = open(ControlPREFIX+"Configuration.in",'r')
#	print (ControlPREFIX+"Configuration.in")
	filelines = f.readlines()
#	print (filelines)
	for i in range(len((filelines))):
		if filelines[i].strip().split()[0] == "period":
				filelines[i] = "%s\t%s\t%s\n" % ("period","=",items[2])
		if filelines[i].strip().split()[0] == "ZoneDir":
				filelines[i] = "%s\t%s\t%s\n" % ("ZoneDir","=",items[0][7:])
		if filelines[i].strip().split()[0] == "SigDir":
				filelines[i] = "%s\t%s\t%s\n" % ("SigDir","=",items[1][7:])		
	f.close()
#	print (filelines)
	f = open(ControlPREFIX+"Configuration.in",'w')
	f.writelines(filelines)
	f.close()

	stopService(ControlPREFIX)
	startService(ControlPREFIX)



def runServiceOnce(ControlPREFIX):

	cmd_run = "python %s/ZoneCollect.py -b &" % ControlPREFIX
	sub_run = subprocess.Popen(cmd_run, shell=True)



def main(argv):

	ProgramPath = "/opt/TLDCollect/TLDCollector"

	try:
		opts,args = getopt.getopt(argv[1:], "h", ["stop","start","restart","runonce","update="])
	except getopt.GetoptError,info:
		print (info.msg)
		PrintUsage()
		sys.exit()
	for option,value in opts:
		if option in ("--start"):
			startService(ProgramPath)
		elif option in ('--stop'):
			stopService(ProgramPath)
		elif option in ('--restart'):
			stopService(ProgramPath)
			startService(ProgramPath)
		elif option in ('--runonce'):
			runServiceOnce(ProgramPath)
		elif option in ('--update'):
			updateConfiguration(ProgramPath,value)
		elif option in ('-h'):
			PrintUsage()
		else:
			PrintUsage()
			sys.exit()

if __name__ == "__main__":
	main(sys.argv)
