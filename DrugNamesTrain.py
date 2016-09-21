import fileinput
import re

def chunkWord(word):
	#pattern = re.compile("\w[^aeiouy]+[aeiouy]+[^aeiouy]|[^aeiouy]*[aeiouy]+[^aeiouy]*")	
	middle = re.compile("[^aeiouy]+[aeiouy]+[^aeiouy]")

	#\w: match the beginning of word
	#[^aeiouy]+ : start with non-vovel, more than one
	#[aeiouy]+ : continued by one or more vovels
	#(?ifthen|else): if else startement
	# (?=[^aeiouy]{2,}): if followed by two non-vovels, only capture 	
	#beginning = re.compile("\w[^aeiouy]+[aeiouy]+(?(?=[^aeiouy]{2,}))")	
	#print(re.split(r"[^aeiouy]+",word))	

	#begins with non-vovel and end with single non-vovel
	#beginNonVovel = re.compile("\w[^aeiouy]+[aeiouy]+[^aeiouy]{2,}")	

	if len(word)<5:
		return word
	else:
		
		word = word.replace(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "")
		return " ".join(re.findall(middle, word))

def main():

	for line in fileinput.input("DrugNamesFromDrugPortal.csv"):
		lst = []
		lst = [item.lower() for item in line.strip().rsplit(',')]
		#print(lst[0])
		#print(chunkWord(lst[0]))
		

if __name__=="__main__":
	main()




