import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
import re, os
from time import time
from time import gmtime, strftime
import hashlib
import os
import re
import lxml.html
import requests
import re
import collections


try:
    # For python 2
    from urlparse import urlparse, parse_qs,urljoin
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs


logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set() 
    if not os.path.exists("successful_urls.txt") else 
    set([line.strip() for line in open("successful_urls.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 3000
hashes = dict()
urls_max=dict();


dict_subdomains = {}
@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):

    def __init__(self, frame):
        self.starttime = time()
        # Set app_id <student_id1>_<student_id2>...
        self.app_id = "18164476_74047877"
        # Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
        # If Graduate studetn, change the UnderGrad part to Grad.
        self.UserAgentString = "IR W17 Grad 18164476, 74047877"
        read_hash()
        read_visited_url()

        self.frame = frame
        assert(self.UserAgentString != None)
        assert(self.app_id != "")
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        for g in self.frame.get(OneUnProcessedGroup):
            print "Got a Group"
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
				if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
					urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            for l in outputLinks:
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
		print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
		analytics()
		write_hash()
		write_visited_url()
		pass

def save_count(urls):
    global url_count
    urls = set(urls).difference(url_count)
    url_count.update(urls)
    if len(urls):
        with open("successful_urls.txt", "a") as surls:
            surls.write(("\n".join(urls) + "\n").encode("utf-8"))

def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas
    
#######################################################################################
'''
STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.
'''
def extract_next_links(rawDatas):
	outputLinks = list()
	'''
    rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
    Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.

    Suggested library: lxml
	'''
	generated = open("generated_urls.txt", "a")	
	for rawData in rawDatas:
		try:
			parent_url = rawData.url
			generated.write("[" + strftime('%X %x %Z') +"]" + parent_url + "\n")
			page = rawData.content
			
			# if page is not found and similar other http response where page is blank
			if page != None  and rawData.http_code not in [204,400,401,402,403,405,406,408,409,410,411,412,413,414,415,416,417,451]:
				if (len(page) > 0):
					if compute_checksum((parent_url,page)) == False:
						rawData.bad_url = True
						continue
					html = lxml.html.fromstring(page)
				else:
					generated.write("[" + strftime('%X %x %Z') + "]" + " Encountered URL with no page" + "\n")
					rawData.bad_url = True
					continue
			else:
				generated.write("[" + strftime('%X %x %Z') + "]" + " Encountered URL with page issue - " + str(rawData.http_code) + "\n")
				rawData.bad_url = True
				continue
			temp_url_list = []
			for link in html.iterlinks():
				try:
					sub_url = (link[2])
					parent_url_parsed= urlparse(parent_url)
					sub_url_parsed = urlparse(sub_url)
					new_url = urljoin(parent_url_parsed.geturl(), sub_url_parsed.geturl())
					generated.write("   " + "original link" + "[" + strftime('%X %x %Z') + "]" + sub_url_parsed.geturl() + "\n")
					generated.write("   " + "[" + strftime('%X %x %Z') +"]" + new_url + "\n")
					temp_url_list.append(new_url)
				except Exception as c:
					generated.write("[" + strftime('%X %x %Z') + "]" + " Encountered exception in parsing link " + str(c) + "\n")
					rawData.bad_url = True
					continue
			outputLinks.extend(temp_url_list)
			log_url_count(parent_url, len(temp_url_list))
		except Exception as e:
			generated.write("[" + strftime('%X %x %Z') + "]" + " Encountered exception in parsing main url or error in page " + str(e) + "\n")
			continue 
	return outputLinks


def is_valid(url):

	update_subdomains_count(url)

	try:
		parsed = urlparse(url)
		# print "scheme check"
		if parsed.scheme not in set(["http", "https"]):
			return False
		# print "domain check"
		if "../" in url:
			return False

		if len(parsed.netloc) == 0:
			return False
		if " " in url:
			return False
		# print "javascript check"
		if "javascript:popUp(" in url:
			return False
		# print "hostname check"
		if ".ics.uci.edu" not in parsed.hostname:
			return False
		# print "invalid file check"
		invalid_end = [".war",".r",".c",".p",".txt",".py",".java",".m",".gif",".js",".pdf",".jpg",".jpeg",".css",".bmp",".ico",".png",".tiff",".mid",".mp2",".mp3",".mp4",".wav",".avi",".mov",".mpeg",".ram",".m4v",".mkv",".ogg",".ogv",".pdf",".text",".thmx",".mso",".arff",".rtf",".jar",".csv","rm",".smil",".wmv",".swf",".wma",".zip",".rar",".gz",".ps",".eps",".tex",".ppt",".pptx",".doc",".docx",".xls",".xlsx",".names",".data",".dat",".exe",".bz2",".tar",".msi",".bin",".7z",".psd",".dmg",".iso",".epub",".dll",".cnf",".tgz",".sha1",".ico"]
		if parsed.path.lower().endswith(tuple(invalid_end)):
			return False
			
	# Check if repeated words in the url - (path, fragment , query ): if word repeated more than 5 times, then the url is invalid
	# eg: http://www.ics.uci.edu/about/bren/bren_press.php/bren_vision.php/gallery/gallery/gallery/visit/gallery/gallery_06_jpg.php/community/news/articles/gallery/gallery/grad/about_safety.php/gallery/about_deanmsg.php/gallery/gallery/gallery/gallery_10_jpg.php/gallery/gallery_04_jpg.php/visit/gallery/gallery/gallery_04_jpg.php
	# http://www.ics.uci.edu/about/bren/bren_press.php/bren_vision.php/gallery/gallery/gallery/visit/gallery/gallery_06_jpg.php/community/news/articles/gallery/gallery/grad/about_safety.php/gallery/about_deanmsg.php/gallery/gallery/gallery/gallery_10_jpg.php/gallery/gallery_04_jpg.php/gallery/gallery_01_jpg.php/grad/gallery/visit/index.php/ICS/ics/about/
	# 	print " invalid word check"
		if len(parsed.path) > 0:
			data = str(parsed.path)+"\\"
			if len(parsed.query) > 0:
				data = str(data) + str(parsed.query)+"\\"
			if len(parsed.fragment) > 0:
				data =str(data) + str(parsed.fragment)
			list_words = re.sub(r"\W+"," ",data).split(" ")
			c= collections.Counter(list_words)
			for letter, count_words in c.most_common(1):
				if count_words > 8:
					return False
		if check_trap(url)==True:
			return False
		return True

	except Exception as e:
		return False
		
# LOG INVALID URL RECEIVED FROM FRONTIER
def log_invalid_url(url):
        with open("invalid_urls.txt", "a") as invalid_url:
            invalid_url.write("\n".join(url) + "\n")
            invalid_url.close()

# GET THE COUNT OF INVALID URL RECEIVED FROM FRONTIER
def count_invalid_url():
    if os.path.isfile("invalid_urls.txt"):
        with open("invalid_urls.txt", "r") as invalidurl:
            s= []
            for i in invalidurl:
                s.append(i)
        return len(s)
    else:
        return 0

# LOG URL, NUMBER OF LINKS EXTRACTED FOR VALID URL RECIEVED FORM FRONTIER	
def log_url_count(url, count):
	print "calling url count"
	try:
		if count == None:
			count=0
		with open("url_count.txt", "a") as url_count_file:
			a=str(str(url)+","+str(count)+'\n')
			url_count_file.write(a)
			url_count_file.close()
	except Exception as e:
		print e
		pass

# GET URL HAVING MAXIMUM OUTBOUND LINKS
def get_url_with_max_outbound():
	try:
		max_count =-1;
		max_url = None
		if os.path.isfile("url_count.txt"):
			with open("url_count.txt", "r") as url_count_file:
				for line in url_count_file:
					try: 
						url_list=line.split(',')
						url = url_list[0]
						count = int(url_list[-1])
						if count > max_count:
							max_count = count
							max_url = url
					except Exception as c:
						print c
		return max_url, max_count
	except Exception as e:
		print e
		pass

# ANALYTICS METHOD FOR CRAWLER WHICH LOGS URL WITH MAX LINKS, COUNT OF INVALID LINKS AND AVERAGE DOWNLOAD TIME				
def analytics():
	with open("analytics.txt", "w") as analytics_file:
		url_key, max_url_count = get_url_with_max_outbound()
		if(url_key is not None):
			analytics_file.write("\nURL with max outbound links: " + str(url_key) + "  	, Number of outbound links: " + str(max_url_count))
		else:
			analytics_file.write("\n No valid URL's recieved")
		invalid_url_count = count_invalid_url()
		analytics_file.write("\nCount of invalid links recieved: " + str(invalid_url_count))
		#analytics_file.write("\n Average download time: " + str(computer_average_download_time()) + " seconds")
		write_subdomain()
			
# METHOD TO UPDATE THE COUNT OF SUBDOMAINS VISITED
# DATA IS STORED IN A DICTIONARY WITH SUBDOMAIN AS KEY AND COUNT AS VALUE
# VALUE UPDATED ONCE URL WITH THAT SUBDOMAIN IS PROCESSED(RECIEVED AS WELL AS SENT TO FRONTIER)		
def update_subdomains_count(url):
	try:
		parsed = urlparse(url)
		if(len(parsed.netloc) > 0):
			if (".ics.uci.edu" in parsed.hostname):
				new_hostname = parsed.hostname[0:len(parsed.hostname) - 12]
				list_hostname = list(new_hostname)
				str=""
				if (len(list_hostname) >0):
					for k in range(len(list_hostname)-1,-1,-1):
						if list_hostname[k] == '.':
							break
						str= str+ list_hostname[k]
					if (len(str) > 0):
						str = str[::-1]
						if str =="www":
							str = "www.ics.uci.edu"
						else:
							str = str +".ics.uci.edu"
						if (str in dict_subdomains.keys()):
							dict_subdomains[str] = int(dict_subdomains[str]) +1
						else:
							dict_subdomains[str] = 1
	except Exception as e:
		print e
		pass
	
# WRITE THE SUBDOMAIN ON THE FILE - SUBDOMAIN.TXT
def write_subdomain():
    with open("subdomain.txt", "w") as myfile:
        for url,count in dict_subdomains.iteritems():
            myfile.write(url+","+ str(count)+"\n")
    myfile.close()	

# READ  THE DOWNLOAD TIME OF ALL THE DOWNLOADED URLS AND GIVE AVERAGE DOWNLOAD TIME
def computer_average_download_time():
	try:
		average_time = 0.0
		count_lines = 0
		if os.path.isfile("url_download_time.txt"):
			with open("url_download_time.txt", "r") as url_download_time_file:
				for line in url_download_time_file:
					url_list=line.split(',')
					time_download = float(url_list[-1])
					average_time = average_time + time_download
					count_lines = count_lines + 1
				if(count_lines > 0):
					average_dwnl_time = float(average_time/ count_lines)
					return average_dwnl_time
				return 0
	except Exception as e:
		return 0			

# READ THE HASH FILE TO FIND IF THE CORRESPONDING URL IS ALREADY EXPLORED
def read_hash():
    if os.path.isfile("hash.txt"):
        with open("hash.txt", 'r') as f:
            for line in f:
                # print "in"
                items = line.split(",")
                key, values = items[0], items[-1]
                # print "####",key,values
                hashes[key] = values.strip('\n')
                # print hashes
        f.close()

# WRITE THE HASH FILE WITH URL AND ITS CORRESPONDING HASH CODE
def write_hash():
    with open("hash.txt", "w") as myfile:
        for url,hashcode in hashes.iteritems():
            myfile.write(url+","+hashcode+"\n")
    myfile.close()

#CHECK HASH OF PAGE AND IF HASH ALREADY EXISTS (DIRECTED TO SAME PAGE) RETURN FALSE
def compute_checksum(data):
	try:
		hash=hashlib.sha224(data[1]).hexdigest()
		if os.path.isfile("hash.txt"):
			for url,hashcode in hashes.iteritems():
				if hashcode==hash:
					with open("failed_hash.txt","a") as ft:
						ft.write(data[0]+","+hashcode+"\n")
					return False
		hashes[data[0]]=hash
		return True
	except Exception as e:
		return False

# READ THE URL FILE CORRESPONDING TO VISITED URLS
def read_visited_url():
    print "reading_found_urls"
    if os.path.isfile("url.txt"):
        with open("url.txt", 'r') as f:
            for line in f:
                items = line.split(",")
                key, values = items[0], items[-1]
                urls_max[key] = values.strip('\n')
        f.close()

# WRITE THE URL FILE CORRESPONDING TO VISITED URLS
def write_visited_url():
    # print urls_max
    with open("url.txt", "w") as myfile:
        for url,count in urls_max.iteritems():
            myfile.write(url+","+str(count)+"\n")
    myfile.close()

# CHECK FOR THE CRAWLER TRAP-IF MORE THAN 10 PAGES WITH SAME NETLOC+PATH+QUERY_KEYS RETURN TRUE
def check_trap(new_url):
	try:
		parsed=urlparse(new_url)
		if len(parsed.query) > 0: 
			query1 = parse_qs(parsed.query)
			s =""
			for key in sorted(query1):
				s = s + key 
			x= parsed.netloc + parsed.path + s
			if x in urls_max.keys():
				if urls_max[x] > 10:
					with open("trap.txt","a") as f:
						f.write(str(x)+"\n")
					return True
				else:
					urls_max[x]=urls_max[x]+1
			else:
				urls_max[x]=1
			return False
		else:
			return False
	except Exception as e:
		print e
		return False

