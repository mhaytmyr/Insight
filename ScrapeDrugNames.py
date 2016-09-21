import urllib,re
from bs4 import BeautifulSoup
import string,time

def getDrugNames(soup,filename):
	#this part will get drug names
	result = soup.findAll("table", {"border":1})
	result2 = result[0].find_all('td')
	
	#this part will get synonims
	for item in result2:
		time.sleep(2)
		originalName, names = item.text.lower(), str()
		print("Drug name...{}".format(originalName))
		#<a href="/drugportal/name/exelon">
		#https://druginfo.nlm.nih.gov/drugportal/name/abacavir%20sulfate

		drugWeb = re.findall(r'href="(.+?)">',str(item))
		#drugs.append(item.text.lower())
		drugWeb = "https://druginfo.nlm.nih.gov"+drugWeb[0]
		soup2 = BeautifulSoup(urllib.urlopen(drugWeb).read(),"lxml")

		synonym = re.findall(r'&lt;li&gt;([a-zA-Z0-9-\s]+?)&lt;br&gt;',str(soup2.find("button",{"onmouseout":"return nd();"})))
		
		names = ",".join(synonym)
		print(originalName+","+names)

		filename.write(originalName+","+names)
                filename.write("\n")      
        	#filename.close()		

	#return names

def main():

	address  = 'https://druginfo.nlm.nih.gov/drugportal/drug/names/'
	drugs = open("DrugNamesFromDrugPortal.csv","w")

	for letter in string.ascii_lowercase:
		print("Drugs starting with name....{}".format(letter))
		html = urllib.urlopen(address+letter)
		soup = BeautifulSoup(html,"lxml")
		getDrugNames(soup,drugs)
		#drugs.write(synonym)
		#drugs.write("\n")	

	drugs.close()

if __name__=="__main__":
	main()

