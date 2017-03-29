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



sys.setdefaultencoding("UTF-8")

count_parser_words=0
# create a subclass and override the handler methods
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
				self.list_of_words.append(stem(word))
				self.tags.append(self.tag)
	
	def getWords(self):
		# print self.list_of_words
		global count_parser_words
		mywords = self.list_of_words
		self.list_of_words =[]
		count_parser_words=count_parser_words+len(mywords)
		# print count_parser_words," ","\n";
		# print len(self.tags)
		# print len(mywords)
		return mywords, self.tags
		
# instantiate the parser and fed it some HTML

class AllFilesParser():

	term_dictionary = {}

	def __init__(self): pass

	def create_term_dictionary(self,list_of_words, list_tags):
		# print list_of_words
		self.term_dictionary={}
		for i in range(0,len(list_of_words)):
			word=list_of_words[i]
			# word not in stopwords.words('english')
			if (word) in self.term_dictionary:
				tup = (i, list_tags[i])
				self.term_dictionary[(word)].append(tup)
				# self.term_dictionary[stem(word)]=sorted(self.term_dictionary[stem(word)])
			else:
				self.term_dictionary[(word)] = list()
				tup = (i, list_tags[i])
				self.term_dictionary[(word)].append(tup)
		# print self.term_dictionary
		# f1=open("term_dict.txt",'a')
		# for key,value in self.term_dictionary.iteritems():
		# 	f1.write(key+" "+str(value)+"\n")		
		# print self.term_dictionary
		return self.term_dictionary

	def parse_files(self, filename):
		try:
			parser = MyHTMLParser()
			parser.list_of_words=[]
			parser.tags =[]
			file1 = open(filename,"r")
			text = file1.read()
			parser.feed(text)
		except Exception as e:
			print e
		list_words, list_tags = parser.getWords()
		return self.create_term_dictionary(list_words, list_tags)
		

class parser_main:
	term_document=dict()
	count_documents=0
	cnt={} #count of the documents
	final_index_dic={}
	final_term_dic={} #word:term_frequency mapping
	final_document_dic={} #word:term_document frequency mapping
	tf_idf={} #tf-idf for term document pair
	bookkeeping = {}
	document_vector = {}
	document_vector_length = {}

	def tagWeight(self):
		tag_weight={}
		tag_weight["title"] = 0.085
		tag_weight["h1"] = 0.078
		tag_weight["h2"]= 0.076
		tag_weight["h3"]= 0.074
		tag_weight["h4"]= 0.072
		tag_weight["h5"]= 0.070
		tag_weight["h6"]= 0.068
		tag_weight["a"]= 0.07
		tag_weight["b"]= 0.05
		tag_weight["p"]= 0.077
		tag_weight["em"]= 0.078
		tag_weight["strong"]= 0.077
		tag_weight["i"]= 0.06
		tag_weight["meta"]= 0.09
		return tag_weight



	def readbookkeeping(self):
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
				data[0] = data[0].replace("\"","")
				if len (data) > 1:
					data[1] = data[1][2:-1]
					data[0]=data[0].strip()
					# print data[0],"***"
					bookkeeping[data[0]] = data[1]
		self.bookkeeping = bookkeeping



	def compute_tf_idf(self):
		# print self.final_term_dic;
		N=self.count_documents
		# print len(self.final_term_dic),"****"
		# cnt=1
		# for word in self.final_term_dic:
		# 	print cnt,word
		# 	cnt=cnt+1

		for word in self.final_term_dic:
			# print word,self.final_term_dic[word]
			for i in range(0,len(self.final_term_dic[word])):
				for key,value in self.final_term_dic[word][i].iteritems():
					# print word,key,value
					if word not in self.tf_idf:
						self.tf_idf[word]=[]
						f=(float( math.log10(1+value)) * float(math.log10(float(self.count_documents)/ float(self.final_document_dic[word])) ) )
						# print word,key,value,self.count_documents,f 
						# print f
						self.tf_idf[word].append({key:f})	
						# self.tf_idf[word].append({key: ( math.log10(1+value)* math.log10(self.count_documents/ self.final_document_dic[word] )) })
					else:
		
						f=(float( math.log10(1+value)) * float(math.log10(float(self.count_documents)/ float(self.final_document_dic[word])) ) )
						# print word,key,value,self.final_document_dic[word],f 
						self.tf_idf[word].append({key:f})	

						# self.tf_idf[word].append({key: ( math.log10(1+value)* math.log10(self.count_documents/ self.final_document_dic[word] ) )	})

	def addTagWeight(self):
		tag_weight=self.tagWeight()
		# print document_score
		for word in self.term_document:
			print word	
			# if word in self.term_document:
			document_list = self.term_document[word]
				# print document_list
			i =0
			for document in document_list:
				keys = document.iterkeys()
				for key in keys:
					value_list=document[key][1]
					for j in range(0,len(value_list)):
						tuple_data = value_list[j]
						for tag in tag_weight:
							if tuple_data[1] == tag:
								keys2 = self.tf_idf[word][i].iterkeys()
								for key2 in keys2:
									self.tf_idf[word][i][key2] = self.tf_idf[word][i][key2] + tag_weight[tag]
								break
				i = i+1
			

	def computeDocumentVector(self):
		for word in self.tf_idf.iterkeys():
			document_list = self.tf_idf[word]
			# print document_list
			for document in document_list:
				keys = document.iterkeys()
				for key in keys:
					# print key
					if key in self.document_vector:
						self.document_vector[key].append((word, document[key]))
					else:
						self.document_vector[key] = []
						self.document_vector[key].append((word, document[key]))
		# return self.document_vector

	def computeDocumentVectorLength(self):
		for document in self.document_vector.iterkeys():
			self.document_vector_length[document]=0
			# print document 
			for word in self.document_vector[document]:
				# print type(word)
				self.document_vector_length[document]=self.document_vector_length[document] + (word[1]*word[1]) 
			self.document_vector_length[document]=math.sqrt(self.document_vector_length[document])	

		

					
	def writefile(self):
		for word in self.term_document:
			self.final_document_dic[word]=self.cnt[word]

		for word in self.term_document:
			self.final_index_dic[word]={self.cnt[word]:self.term_document[word]}

		# compute tidf index
		parser_ob.compute_tf_idf()
		parser_ob.addTagWeight()
		parser_ob.computeDocumentVector()
		parser_ob.computeDocumentVectorLength()

		# WRITE INDEX
		
		# WITH TERM FREQUENCY,POSITIONS AND TAGS
		f=open("dictionary_index.txt","w")
		for key in sorted(self.term_document.iterkeys()):
			f.write(str(key)+": "+str(self.term_document[key])+'\n');
		f.close()	
			
		# TF-IDF
		f=open("tf-idf.txt","w")
		for key in sorted(self.tf_idf.iterkeys()):
			f.write(str(key)+"-"+str(self.tf_idf[key])+"\n")			
		f.close()	

		# DOCUMENT VECTOR
		f=open("dv.txt","w")
		for key in sorted(self.document_vector.iterkeys()):
			f.write(str(key)+"-"+str(self.document_vector[key])+"\n")			
		f.close()	

		# DOCUMENT VECTOR LENGTH
		f=open("dvl.txt","w")
		for key in sorted(self.document_vector_length.iterkeys()):
			f.write(str(key)+"-"+str(self.document_vector_length[key])+"\n")			
		f.close()	



	def readfiles(self,path):
		list_file_names = []
		for (dirpath, dirnames, filenames) in walk(path):
			filenames.sort(key=int)
			for file in filenames:
				list_file_names.append(path+"\\"+file)

		for file_name in list_file_names:
			self.count_documents = self.count_documents + 1

			first_index = file_name.rfind("\\", 0,len(file_name) )
			name1 = file_name[first_index +1:]
			second_index = file_name.rfind("\\", 0,first_index  )
			name2 = file_name[second_index +1:]	
			new_file_name = name2	
			# print new_file_name
			new_file_name2 = new_file_name.replace("\\", "-")
			print new_file_name2
			# print (self.bookkeeping)
			if new_file_name2 in self.bookkeeping:
				# print new_file_name2
				if self.bookkeeping[new_file_name2].endswith(".txt") or self.bookkeeping[new_file_name2].endswith(".r") or self.bookkeeping[new_file_name2].endswith(".m") or self.bookkeeping[new_file_name2].endswith(".java") or self.bookkeeping[new_file_name2].endswith(".jpg") or self.bookkeeping[new_file_name2].endswith(".py") or self.bookkeeping[new_file_name2].endswith(".cc") or self.bookkeeping[new_file_name2].endswith(".h") or self.bookkeeping[new_file_name2].endswith(".cpp") or self.bookkeeping[new_file_name2].endswith(".r") or self.bookkeeping[new_file_name2].endswith(".m"):
					continue			
						
			list_of_words=dict()
			list_of_words=AllFilesParser().parse_files(file_name);
		
			for word in list_of_words:
				x=0
				if word in self.term_document:
					document_freq_pos = {new_file_name:(len(list_of_words[word]),list_of_words[word])}
					self.term_document[word].append(document_freq_pos)
					self.cnt[word]=len(self.term_document[word])	

					if word not in self.final_term_dic:
						x=x+len(list_of_words[word])
						self.final_term_dic[word]=[]
						self.final_term_dic[word].append({new_file_name:x})
					else:
						x=x+len(list_of_words[word])
						self.final_term_dic[word].append({new_file_name:x})

				else:
					self.term_document[word] = []
					document_freq_pos = {new_file_name:(len(list_of_words[word]),list_of_words[word])}
					self.term_document[word].append(document_freq_pos)
					self.cnt[word]=len(self.term_document[word])	

					if word not in self.final_term_dic:
						x=x+len(list_of_words[word])
						self.final_term_dic[word]=[]
						self.final_term_dic[word].append({new_file_name:x})
					else:
						x=x+len(list_of_words[word])
						self.final_term_dic[word].append({new_file_name:x})
			print len(self.term_document)	


# path=r'E:\search_engine_indexer\parser\try';	
path=r'E:\search_engine_indexer\parser copy\webpages_raw\WEBPAGES_RAW';	

count_files=0

parser_ob=parser_main()
parser_ob.readbookkeeping()
directory_names=[]
for (dirpath, dirnames, filenames) in walk(path):
	break
for directory in dirnames:
	directory_names.append(directory)
	directory_names.sort(key=int)
	
# print directory_names
for directory in directory_names:
	count_files=count_files+1
	parser_ob.readfiles(path+"\\"+directory);
	#print "folder count", count_files

parser_ob.writefile()		
print "The total number of document/files processed are",parser_ob.count_documents
print "The number of unique words are",len(parser_ob.term_document)