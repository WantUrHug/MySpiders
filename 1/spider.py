import requests
from bs4 import BeautifulSoup as bs
import re, json, os
import argparse
import collections
import xlwt 

def build_env(dir_name = "spider_result"):
	cwd = os.getcwd()
	filedir =os.path.join(cwd, dir_name)
	if os.path.exists(filedir):
		#shutil.rmtree(filedir)
		print("此目录下存在同名文件夹")#，已删除它以及其中的所有文件.")
	else:
		os.mkdir(filedir)
		print("已在此目录下创建文件夹 %s 以存放数据."%dir_name)
	return filedir

#def download_info(pageindex, pagesize, jgid, download_csv):
#	
#	main_url = "http://218.14.150.123:8085/"
#	#SPFYSXM=商品房预售项目
#	SPFYSXM = "api/TradeInfoJMApi/GetSPFYSXM?jgid=%s&&type=ysxmmc&value=&pageindex=%d&pagesize=%d"%(jgid, pageindex, pagesize)
#	
#	r = requests.get(main_url + SPFYSXM)#发起 GET 请求并取出其中的 text 数据
#	#print(r.url)
#	r = r.text
#	jsondata = json.loads(r)#对 json 数据进行处理，得到字典对象
#	rows = jsondata["Data"]["rows"]
#
#	#如果是要预许号文件，那么索引号选择5
#	index = 2
#	pattern = re.compile(r'href=".*" target')
#	#[6:-8}是为了略去正则表达式的前面的 href=" 和后面的 target"，注意是有空格的
#	href_ls = [pattern.search(item["data"][index]).group()[7:-8] for item in rows]
#
#	global header_flag
#	for href in href_ls:
#		response = requests.get(main_url + href)
#		html = response.content
#		html_doc = str(html, "utf-8")
#
#		item_soup = bs(html_doc, "html.parser")
#		table = item_soup.find("table")
#		tds = table.find_all("td")
#
#		info = parse_from_table(table)
#		save2csv(info, download_csv, header_flag)
#		if header_flag:
#			header_flag = False
#
#	print("成功写入第%s页."%pageindex)



def parse_from_table(table):
	'''
	tds 是一个网页中将会被解析成表格的信息，依次提取成字典然后再交给另一个函数保存到本地的 excel 中
	'''
	dic = collections.OrderedDict()
	#dic["areaname"] = tds[0].find("span").string + tds[0].find("strong").string
	tds = table.find_all("td")

	dic["areaname"] = tds[0].span.string + tds[0].strong.contents[2]
	dic["bookid"] = tds[1].font.contents[0].string + ":" + tds[1].font.contents[1][1:]

	dic["开发企业名称"] = table.find(id = "kfsmc").string
	dic["开发资质证书号"] = table.find(id = "kfszh").string
	dic["备注"] = table.find(id = "Reg_Remark").string
	if dic["备注"]:
		dic["备注"] = re.sub("( |\n|\r)", "", dic["备注"])
	dic["项目名称"] = table.find(id = "PresellName").string
	dic["项目坐落"] = table.find(id = "ItemRepose").string
	dic["预售房屋建筑面积"] = re.sub("( |\n|\r)", "", table.find(id = "PresellArea").string)
	dic["土地使用权证号及用途"] = table.find(id = "landinfo").string
	dic["住宅"] = re.sub(" ", "", table.find(id = "zhuzhai").string)
	dic["预售房屋栋号及层数"] = re.sub("( |\n|\r)", "", table.find(id = "donginfo").string)
	dic["商业用房"] = re.sub(" ", "", table.find(id = "businesshouse").string)
	dic["发证时各栋已建层数"] = table.find(id = "buildedcount").string
	dic["办公用房统计"] = re.sub(" ", "", table.find(id = "Officestatistics").string)
	dic["预售房屋占用土地是否抵押"] = re.sub("( |\n|\r)", "", table.find(id = "isdiya").string)
	dic["其它"] = re.sub(" ", "", table.find(id = "others").string)
	dic["预售款专用账户"] = re.sub("( |\n|\r)", "", table.find(id = "bank").string)
	dic["发证机关查询、投诉电话"] = re.sub("( |\n|\r)", "", table.find(id = "fztel").string)
	dic["发证机关（盖章）"] = table.find(id = "fzorg").string[10:]
	dic["有效期"] = re.sub(" ", "", table.find(id = "FZDatebegin").string[4:-1])
	dic["发证日期"] = re.sub(" ", "", table.find(id = "FZDate").string[5:])
	
	return dic

def save2csv(dic, csv_path, add_header = False):
	if add_header:
		string = ", ".join(dic.keys())
		#print(string)
		with open(csv_path ,"w") as f:
			f.write(string + "\n")
	value_ls = []
	#pprint(dic)
	for value in dic.values():
		if value is None:
			value = ""
		value_ls.append(value)
	string = ", ".join(value_ls)
	with open(csv_path, "a") as f:
		f.write(string + "\n")

class MySpider():

	def __init__(self, jgid_ls, name_ls):
		self.jgid_ls = jgid_ls
		self.name_ls = name_ls
		#self.pagenum_ls = pagenum_ls
		self.header_flag = True
		self.main_url = "http://218.14.150.123:8085/"
		self.pagesize = 10
		self._parse_based_task()
		
		self.workbook = xlwt.Workbook(encoding = "utf-8")

	def __len__(self):

		return len(self.name_ls)

	def _parse_based_task(self):
		'''
		查询每个区需要下载的文件数，因为随着时间推移会发生变化.
		'''
		print("")
		print("开始查询每个区需要下载的文件总数...")
		self.total_cnt = []

		for i in range(len(self)):

			SPFYSXM = "api/TradeInfoJMApi/GetSPFYSXM?jgid=%s&&type=ysxmmc&value=&pageindex=%d&pagesize=%d"%(self.jgid_ls[i], 1, self.pagesize)
			r = requests.get(self.main_url + SPFYSXM)
			r = r.text
			jsondata = json.loads(r)
			total_count = jsondata["Data"]["total_count"]
			self.total_cnt.append(total_count)
			print(self.name_ls[i], total_count)

	def _parse_from_table(self, table):
		'''
		tds 是一个网页中将会被解析成表格的信息，依次提取成字典然后再交给另一个函数保存到本地的 excel 中
		'''
		dic = collections.OrderedDict()
		#dic["areaname"] = tds[0].find("span").string + tds[0].find("strong").string
		tds = table.find_all("td")

		dic["areaname"] = tds[0].span.string + tds[0].strong.contents[2]
		dic["bookid"] = tds[1].font.contents[0].string + ":" + tds[1].font.contents[1][1:]

		dic["开发企业名称"] = table.find(id = "kfsmc").string
		dic["开发资质证书号"] = table.find(id = "kfszh").string
		dic["备注"] = table.find(id = "Reg_Remark").string
		if dic["备注"]:
			dic["备注"] = re.sub("( |\n|\r)", "", dic["备注"])
		dic["项目名称"] = table.find(id = "PresellName").string
		dic["项目坐落"] = table.find(id = "ItemRepose").string
		dic["预售房屋建筑面积"] = re.sub("( |\n|\r)", "", table.find(id = "PresellArea").string)
		dic["土地使用权证号及用途"] = table.find(id = "landinfo").string
		dic["住宅"] = re.sub(" ", "", table.find(id = "zhuzhai").string)
		dic["预售房屋栋号及层数"] = re.sub("( |\n|\r)", "", table.find(id = "donginfo").string)
		dic["商业用房"] = re.sub(" ", "", table.find(id = "businesshouse").string)
		dic["发证时各栋已建层数"] = table.find(id = "buildedcount").string
		dic["办公用房统计"] = re.sub(" ", "", table.find(id = "Officestatistics").string)
		dic["预售房屋占用土地是否抵押"] = re.sub("( |\n|\r)", "", table.find(id = "isdiya").string)
		dic["其它"] = re.sub(" ", "", table.find(id = "others").string)
		dic["预售款专用账户"] = re.sub("( |\n|\r)", "", table.find(id = "bank").string)
		dic["发证机关查询、投诉电话"] = re.sub("( |\n|\r)", "", table.find(id = "fztel").string)
		dic["发证机关（盖章）"] = table.find(id = "fzorg").string[10:]
		dic["有效期"] = re.sub(" ", "", table.find(id = "FZDatebegin").string[4:-1])
		dic["发证日期"] = re.sub(" ", "", table.find(id = "FZDate").string[5:])
		
		return dic
	
	def _get_infos(self, pageindex, pagesize, jgid):
	
		infos = []

		#main_url = "http://218.14.150.123:8085/"
		#SPFYSXM=商品房预售项目
		SPFYSXM = "api/TradeInfoJMApi/GetSPFYSXM?jgid=%s&&type=ysxmmc&value=&pageindex=%d&pagesize=%d"%(jgid, pageindex, pagesize)
		
		r = requests.get(self.main_url + SPFYSXM)#发起 GET 请求并取出其中的 text 数据
		#print(r.url)
		r = r.text
		jsondata = json.loads(r)#对 json 数据进行处理，得到字典对象
		rows = jsondata["Data"]["rows"]
	
		#如果是要预许号文件，那么索引号选择5
		index = 2
		pattern = re.compile(r'href=".*" target')
		#[6:-8}是为了略去正则表达式的前面的 href=" 和后面的 target"，注意是有空格的
		href_ls = [pattern.search(item["data"][index]).group()[7:-8] for item in rows]
	
		for href in href_ls:
			response = requests.get(self.main_url + href)
			html = response.content
			html_doc = str(html, "utf-8")
	
			item_soup = bs(html_doc, "html.parser")
			table = item_soup.find("table")
			tds = table.find_all("td")
	
			info = self._parse_from_table(table)
			infos.append(info)
	
		return infos


	def run(self):


		for i in range(1):#len(self)):

			worksheet = self.workbook.add_sheet(self.name_ls[i])
			#每张表的表头，只需要执行一次添加表头的操作
			header_flag = True
			pag = self.total_cnt[i]//self.pagesize if self.total_cnt[i]%self.pagesize == 0 else self.total_cnt[i]//self.pagesize+1

			for pageindex in range(pag):
				infos = self._get_infos(pageindex, self.pagesize, self.jgid_ls[i])
				#print(infos)
				for j in range(self.pagesize):
					print("1")


		self.workbook.save("test.xls")
	

if __name__ == "__main__":
	#assert 1 == 0
	#parser = argparse.ArgumentParser()
	#parser.add_argument("--pagenum", help = "从网页上查看一共有多少页，以每页10条计", type = int, default = 139)
	#args = parser.parse_args()
	#pagenum = args.pagenum
	#print("一共计划抓取%s页"%pagenum)
	
	download_dir = build_env()

	jgid_ls = [ "91679226-6e6c-4b90-b60f-6f4b87291133", 
				"f85c93f4-9520-4e8b-8dde-3c89ceb95883",
				"d111693f-6943-4f13-858a-cd61ff9184fd",
				"a28d3522-f93f-46b7-9446-1ccbfd3b5146",
				"819cee29-0920-49f1-9b3d-d777eb846f56", 
				"03f8d5d6-c504-4836-b0ea-7c2df55b3024", 
				"5be1d44b-34d8-4ec9-9756-13e2260b52aa"]
	name_ls = ["蓬江", "江海", "新会", "台山", "开平", "鹤山", "恩平"]
	#pagenum_ls = [61, 35, 139, 102, 79, 521, 43]
	#for i in range(len(pagenum_ls)):
	#	csv = os.path.join(download_dir, "%s区.csv"%name_ls[i])
	#	header_flag = True
	#	for pageindex in range(1, pagenum_ls[i] + 1):
	#		download_info(pageindex, 10, jgid_ls[i], csv)
	spider = MySpider(jgid_ls, name_ls)
	spider.run()
