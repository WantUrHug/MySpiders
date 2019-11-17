import requests
from bs4 import BeautifulSoup

import re

host = "https://m.77nt.com/"
page = "117563/38339847.html"
#page = "117563/38817857.html"
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50'}

cnt = 0

while True:
	r = requests.get(host + page, headers = headers)
#print(r.encoding)
	text = r.text
#print(dir(text))

	r.encoding = "utf-8"
#print(r.content.decode(r.encoding))
	t = text.encode("ISO-8859-1")
	ss = t.decode("utf-8")
	soup = BeautifulSoup(ss, "html.parser")

	chapter = soup.find_all("h1")
	chaptername = chapter[0].string
#print(chaptername)
	nr = soup.find("div", id = "nr1")
	
	with open("test.txt", "a", encoding = "utf-8") as file:

		file.write(chaptername + "\n\n")
		for i in list(nr.children)[::2]:
			file.write(re.sub(" |\n|\r", "", i) + "\n")
		file.write("\n")

	page = soup.find("a", id = "pb_next")["href"]
	cnt += 1
	if cnt%100 == 0:
		print("已经下载%d章."%cnt)
	#print(next_pg["href"])
	
#for i in list(nr.children)[::2]:
	#print(type(i))
#	print(i.string)#[1:].encode("ISO-8859-1").decode("utf8"))
	#	file.write(i)
	#print(type(text))
#	file.write(text)	
#print(text)
#ss = "è¿å"
#ss = ""
#sss = ss.encode('ISO-8859-1')
#ssss = sss.decode('utf8')
#print(ssss)
