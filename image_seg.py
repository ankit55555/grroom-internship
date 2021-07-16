import json
import urllib.request

file = open("C:/Users/chaud/OneDrive/Desktop/groom/file1.txt", )
text = json.load(file)

urls=[]
for x in text:
  urls.append(str(x["image"]))

url = urls[15000:16000]  ###Change the number according to what is assigned!!

count = 15000

while count != len(url):
	f = open('C:/Users/chaud/OneDrive/Desktop/groom/image_seg/{}.jpg'.format(count), 'wb')
	f.write(urllib.request.urlopen(url[count-15000]).read())
	count += 1

f.close()
