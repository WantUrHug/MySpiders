#encoding = utf-8
import requests
from bs4 import BeautifulSoup
import re

host = "https://m.77nt.com/"
page = "117563/38817857.html"

r = requests.get(host + page)
#print(r.encoding)
text = r.text
#print(dir(text))
soup = BeautifulSoup(text, "html.parser")
chapter = soup.find_all("h1")
chaptername = chapter[0].string
nr = soup.find("div", id = "nr1")

t = text.encode("ISO-8859-1")
#print(t.decode("utf-8"))
for i in list(nr.children)[::2]:
	#s = i.string
	#print(list(i.next))
	print(i)
	#print(i.encode("ISO-8859-1").decode("utf-8"))