import urllib.request

baseURL = 'https://api.thingspeak.com/update?api_key=DO68GWETIHR6E10S'
params = '&field1=%s' % (12.5)
f = urllib.request.urlopen(baseURL + params)
f.read()
f.close()
