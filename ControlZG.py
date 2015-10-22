from __future__ import print_function
import getopt
import sys
import re
import getopt
import subprocess

ControlPREFIX = "/root/ZoneProject/RootZoneCollector/"

def startService(ControlPREFIX):
	cmd = "(python ZoneCollect.py &)"
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()	
	
def stopService(ControlPREFIX):
	cmd = r'ps -ef | grep "python ZoneCollect"'
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	pid = "dummy"
	for lines in reslines:
		if lines.split()[2] == '1':
			pid = lines.split()[1]
			print (pid)
 
	sub1 = subprocess.Popen("kill -9 %s" % pid, stdout=subprocess.PIPE, shell=True)
	sub1.wait()

def runServiceOnce(ControlPREFIX):
	cmd = "(python ZoneCollectBasic.py &)"
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()


def main(argv):
	try:
		opts,args = getopt.getopt(argv[1:], "h", ["stop","start","restart","runonce"])
	except getopt.GetoptError,info:
		print (info.msg)
		PrintUsage()
		sys.exit()
	for option,value in opts:
		if option in ("--start"):
			startService(ControlPREFIX)
		elif option in ('--stop'):
			stopService(ControlPREFIX)
		elif option in ('--restart'):
			stopService(ControlPREFIX)
			startService(ControlPREFIX)
		elif option in ('--runonce'):
			runServiceOnce(ControlPREFIX)
		elif option in ('-h'):
			PrintUsage()
		else:
			PrintUsage()
			sys.exit()

if __name__ == "__main__":
	main(sys.argv)	
