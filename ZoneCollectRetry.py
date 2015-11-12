import pycurl

def download():
	f = open("./res",'w')
	curl = pycurl.Curl()
	curl.setopt(pycurl.URL, 'http://www.internic.net/domain/root.zone')
	curl.setopt(pycurl.WRITEDATA, f)
	curl.perform()
	curl.close()
	f.close()




if __name__ == "__main__":
	download()
