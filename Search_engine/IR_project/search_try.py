from Tkinter import *
from operator import itemgetter
import webbrowser
from stemming.porter2 import stem
# -*- coding: utf-8 -*-
# encoding:utf-8
import nltk
from HTMLParser import HTMLParser
import re
import os
import glob
from os import walk
from nltk.corpus import stopwords 
import collections
import sys
reload(sys)
import site
import math
from stemming.porter2 import stem
from collections import Counter

class MyHTMLParser(HTMLParser):
    
	tag =""
	list_of_words=[]	
	tags =[]

	# list_of_words=[]	
	script = False
	def handle_starttag(self, tag, attrs):
		# print "Encountered a start tag:", tag
		
		self.tag = tag;
		if (tag == "script"):
			self.script = True
		
	def handle_endtag(self, tag):
		# print "Encountered an end tag :", tag	
			if self.script:
				self.script = False
				self.tag=""

	def handle_data(self, data):
		if self.script == False:
			words = re.sub(r'[^A-Za-z0-9]'," ",data).lower().split()
			for i in range(0,len(words)):
				word=words[i]
				self.list_of_words.append((word))
				# self.tags.append(self.tag)
	
	def getWords(self):
		# print self.list_of_words
		# global count_parser_words
		mywords = self.list_of_words
		self.list_of_words =[]
		# count_parser_words=count_parser_words+len(mywords)
		# print count_parser_words," ","\n";
		# print len(self.tags)
		# print len(mywords)
		return mywords

def parse_files(filename):
	try:
		parser = MyHTMLParser()
		parser.list_of_words=[]
		parser.tags =[]
		file1 = open(filename,"r")
		text = file1.read()
		parser.feed(text)
	except Exception as e:
		print e
	list_words = parser.getWords()
	return list_words


def snippets(query,result):
	snip=""
	snip_list=[]
	try:
		for i in range(0,len(result)):
			# print result[i]
			# print bookkeeping[result[i][0]]
			path="E:\search_engine_indexer\parser copy\webpages_raw\WEBPAGES_RAW"
			# print type(result[i][0])
			file=result[i][0].replace('-','\\')	
			path=str(path)+"\\"+str(file)
			print path
			# f=open(path,"r")
			content=parse_files(path)
			# print content[0]
			# print (content)
			snip=""
			index=-1;
			for q_word in query:
				# print q_word
				for i in range(0,len(content)):
					# print content[i]
					if stem(content[i])==stem(q_word):
						index=i
						# print i,content[i]
						break
				if index!=-1:
					break		
			snip="";
			# print index
			a=index-15
			b=index+15
			while a<0 and a!=index:
				a=a+1
			while b>len(content) and b!=index:
				b=b-1	
			for i in range(a,b):
				snip = snip +" "+ content[i]
			# print content	
			# print snip
			x="..."+snip+"..."
			snip_list.append(x)
	except Exception as e:
		print e		
	return snip_list



def readbookkeeping():
	file = open("bookkeeping.json", "r")
	bookkeeping = {}
	lines  = file.read().split(",")
	for line in lines:
		if line == "{" or line == "}":
			continue
		else:
			line = line.strip()
			data = line.split(":")
			data[0] = data[0][1:-1]
			data[0] = data[0].replace("/","-")
			if len (data) > 1:
				data[1] = data[1][2:-1]
				bookkeeping[data[0]] = data[1]
	return bookkeeping


def addTagWeight(query_list,document_score):
	tag_weight=tagWeight()
	# print document_score
	for word in query_list:
		word=stem(word.lower())
		# print word
		if word in document_index:
			document_list = document_index[word]
			# print document_list
			for document in document_list:
				keys = document.iterkeys()
				for key in keys:
					# print key
					if key in document_score:
						value_list=document[key]
						# print value_list
						for tag in tag_weight:
							if tag in value_list[1]:
								document_score[key] = document_score[key] + tag_weight[tag]
	# print document_score
	return sorted(document_score.items(), key=itemgetter(1),reverse = True)	

def readDocumentVectorLength():
 	file=open("dvl.txt","r")
 	document_vector_length={}
 	for line in file:
 		data=line.split('-')
 		document_vector_length[str(data[0].replace("\\","-"))] = float(data[1])
 	# print document_vector_length	
 	return document_vector_length



def readDictionaryIndex():
	file = open("dictionary_index.txt")
	main_dictionary = {}
	for line in file:
		data =  line.split(":")
		key = data[0]
		values = []
		while (line.find('{') != -1):
			a = line.find('{')
			b = line.find('}')
			# print a 
			# print b
			# print line [a+1:b]
			new_data = line[a+1:b]
			new_key = new_data.split(":")[0][1:-1]
			new_value = new_data.split(":")[1]
			new_key = new_key.replace("\\\\","-")
			# print new_key
			# print new_value
			new_dict = {}
			lenght= new_value.split(",")[0]
			m = new_value.find(',')
			new_value_iter = new_value[m+1:]
			# print lenght
			length = lenght[2:]
			# print length
			new_value_list =[]
			new_value_list.append(int(length))
			tag_list = []
			pos_list =[]
			while (new_value_iter.find('(') !=-1):
				c = new_value_iter.find('(')
				d = new_value_iter.find(')')
				new_value_iter_data =  new_value_iter[c+1:d]
				new_tuple = new_value_iter_data.split(',')
				tag_list.append(new_tuple[1][2:-1])
				pos_list.append(int (new_tuple[0]))
				new_value_iter = new_value_iter[d+1:]
			new_value_list.append(tag_list)
			new_value_list.append(pos_list)
			new_dict[new_key] = new_value_list
			values.append(new_dict)
			line = line [b+1:]
		main_dictionary[key] = values
	return main_dictionary



def tagWeight():
	tag_weight={}
	tag_weight["title"] = 0.85
	tag_weight["h1"] = 0.78
	tag_weight["h2"]= 0.76
	tag_weight["h3"]= 0.74
	tag_weight["h4"]= 0.72
	tag_weight["h5"]= 0.70
	tag_weight["h6"]= 0.68
	tag_weight["a"]= 0.7
	tag_weight["b"]= 0.5
	tag_weight["p"]= 0.77
	tag_weight["em"]= 0.78
	tag_weight["strong"]= 0.77
	tag_weight["i"]= 0.6
	tag_weight["meta"]= 0.9
	return tag_weight


def readTFIDF():
	tfidf = {}
	file = open("tf-idf.txt", "r")
	for line in file:
		new_list = []
		data = line.split('-')
		content = data[1][1:-2].split(",")
		for value in content:
			main_content = value.split(":")
			dict_key = str(main_content[0][0:].replace("{","").strip())
			dict_key = dict_key.replace("\\\\","-")
			dict_key = dict_key[1:-1]
			# print dict_key
			dict_value = main_content[1][:-1].strip()
			dict_value = dict_value.replace("}","")
			# print dict_value
			dict_map ={}
			dict_map[dict_key] = float(dict_value)
			new_list.append(dict_map)
		tfidf[data[0]] = new_list
		
	return tfidf


def getSearchResultsByCosineScore(query_list):
	document_score = {}
	query_vector_score = []
	word_counter = Counter(query_list)
	length_document= {}
	
	#calculate the numerator part of cosine formula
	for word in word_counter:
		# print word
		word1=word
		word=stem(word.lower())
		if word in tfidf_index:
			document_list = tfidf_index[word]
			# print document_list
			print "tf","no of docs","doc list"
			print word_counter[word1] , number_of_documents, len(document_list)
			weight_query_word = (float( math.log10(1+word_counter[word1])) * float(math.log10(number_of_documents)/ float(len(document_list))) )
			print "in "
			print weight_query_word
			for document in document_list:
				keys = document.iterkeys()
				for key in keys:
					# print key
					if key in document_score:
						document_score[key] = document_score[key] + (float(document[key]) * float(weight_query_word))
					else:
						document_score[key] = ( float(document[key]) * float(weight_query_word) )
	# print document_score
	# calculate the denominator part of cosine formula and divide it by numerator
	for document in document_score:
		length_document[document] = 0
		if document in document_vector_index:
			document_score[document] = float(document_score[document] / float(document_vector_index[document]))
	# sort score by value and return
	return sorted(document_score.items(), key=itemgetter(1),reverse = True)


def getSearchResultsByTFIDF(query_list):
	document_score = {}
	for word in query_list:
		# print word
		word=stem(word.lower())
		# print word
		if word in tfidf_index:
			document_list = tfidf_index[word]
			# print document_list
			for document in document_list:
				keys = document.iterkeys()
				for key in keys:
					# print key
					if key in document_score:
						document_score[key] = document_score[key] + document[key]
					else:
						document_score[key] = document[key]
	# print document_score
	return sorted(document_score.items(), key=itemgetter(1),reverse = True)	

def url_score(query_list,result):
	if len(result)<=100:
		result=result
	else:
		result=result[0:100]
	print "in url score"
	print result		
	score=float(1/float(len(query_list)))
	print "score",score
	document_score={}	
	for document_id in result:
		document_score[document_id[0]]=document_id[1]
		print "document score ",document_score[document_id[0]]
		url=bookkeeping[document_id[0]]
		for word in query_list:
			word=word.lower()
			url=url.lower()
			if word in url:
				print word,url
				document_score[document_id[0]] = document_score[document_id[0]] + score 
	# print document_score	
	return sorted(document_score.items(), key=itemgetter(1),reverse = True)	




def callback():
	for widget in result_frame.winfo_children():
		widget.destroy()
	# print text1.get()
	query_list = []
	query = text1.get()
	query_list = query.split()
	var = StringVar()

	label = Label(result_frame, textvariable = var)
	label.pack(side= TOP)
	
	scrollbar = Scrollbar(result_frame)
	scrollbar.pack( side = RIGHT, fill=Y )

	mylist = Listbox(result_frame, yscrollcommand = scrollbar.set,height =30, width = 800 )

	# result = getSearchResultsByTFIDF(query_list)
	result= getSearchResultsByCosineScore(query_list)
	
	# print type(result)
	print result

	result=url_score(query_list, result)
	var.set("Result count: " + str(len(result)))

	snippet_list=snippets(query_list,result)	
	if len(result)<10:
		result=result
	else:
		result=result[0:10]	

	for i in range(0,len(result)):
		mylist.insert(END, bookkeeping[result[i][0]])
		mylist.itemconfig(i*3, {'fg': 'blue'})
		mylist.insert(END, snippet_list[i])
		mylist.insert(END,"")

		# print bookkeeping[result[i][0]]
	# q=["week"]
	mylist.pack( side = LEFT, fill = BOTH )
	scrollbar.config( command = mylist.yview )
	mylist.bind( "<Double-Button-1>" , internet)


def internet(event):
	# print "here"
	widget = event.widget
	selection=widget.curselection()
	value = widget.get(selection[0])
	# print "selection:", selection, ": '%s'" % value
	webbrowser.open_new(value)

print "reading bookkeeping"
bookkeeping = readbookkeeping()	
# print len(bookkeeping)	
print "reading tfidf"
tfidf_index = readTFIDF()
print "read tfidf"

print "reading document vector length"
document_vector_index=readDocumentVectorLength()

print "read document vector length"
number_of_documents=len(document_vector_index)

# document_index = readDictionaryIndex()
# print "read dict"
# print len(tfidf_index)
master = Tk()
master.title("ICS Search")
master.geometry("1500x900")
frame = Frame(master)
frame.pack(side = TOP)
input_frame = Frame(frame)
input_frame.pack(side = TOP)
result_frame = Frame(frame)
result_frame.pack(side = BOTTOM)

text1 = Entry(input_frame, width =100)
text1.pack(side=LEFT)
b = Button(input_frame, text="Search", command= callback)
b.pack(side = RIGHT)

mainloop()
