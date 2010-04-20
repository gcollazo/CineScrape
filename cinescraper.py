#!/usr/bin/env python
# encoding: utf-8
"""
cinescraper.py

This app scrapes the showtime info from
http://www.caribbeancinemas.com

Copyright 2010-01-24 Giovanni Collazo

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import urllib2
import re
import sys
import getopt
from BeautifulSoup import BeautifulSoup
import MySQLdb

baseUrl = "http://www.caribbeancinemas.com"
db_user = ''
db_passwd = ''
db_name = ''
db_host = ''
db_socket = ''

def main():
	print updateDb(getAllData())


def updateDb(data):
	conn = MySQLdb.connect(user = db_user, passwd = db_passwd, db = db_name, unix_socket = db_socket)
	cursor = conn.cursor()
	
	# Truncate tables
	cursor.execute("TRUNCATE TABLE `movies`")
	cursor.execute("TRUNCATE TABLE `theaters`")
	
	for x in data:
		cursor.execute("INSERT INTO `theaters` (`name`) VALUES (%s)", x['theaterName'])
		theater_id = conn.insert_id()
		for m in x['data']:
			cursor.execute("INSERT INTO `movies` (`name`, `theater_id`) VALUES (%s, %s)", (m['movieName'], theater_id))
			movie_id = conn.insert_id()
			
			if(len(m['showtimes']) == 4):
				cursor.execute("UPDATE `movies` SET `period1` = %s, `period2` = %s, `period3` = %s, `period4` = %s WHERE `id` = %s",
				(m['showtimes'][0], m['showtimes'][1], m['showtimes'][2], m['showtimes'][3], movie_id))
			else:
				cursor.execute("UPDATE `movies` SET `period1` = %s, `period2` = %s, `period3` = %s WHERE `id` = %s",
				(m['showtimes'][0], m['showtimes'][1], m['showtimes'][2], movie_id))
	
	cursor.close()
	conn.commit()
	conn.close()
	
	return 'Done!'


def getAllData(max_theaters=0):
	theaters = getTheaterList(max_theaters)
	result = []

	i = 1

	for t in theaters:
		result.append({'theaterName': t['name'], 'data':getTheaterData(t['url'])})

	return result


def getTheaterData(url):
	
	page = getPage(url)
	
	soup = BeautifulSoup(page)
	movies = soup.findAll('a', {'class': 'MOVIETITLES2'})
	
	movieNames = [x.string.rstrip() for x in movies]
	
	dayHeaders = soup.findAll('b', {'class': 'INFOHEADERS'})
	days = [x.string.rstrip() for x in dayHeaders]
	
	timePeriods = len(days) / len(movieNames)
	
	times = []
	for t in dayHeaders:
		times.append(t.nextSibling.next)
	
	result = []
	for index, n in enumerate(movieNames):
		if(timePeriods == 4):
			result.append({'movieName':n, 'showtimes':[times[index*4], times[index*4+1], times[index*4+2], times[index*4+3]] })
		else:
			result.append({'movieName':n, 'showtimes':[times[index*3], times[index*3+1], times[index*3+2]] })
	
	return result


def getTheaterList(max_theaters):
	res = getPage(baseUrl)

	soup = BeautifulSoup(res)
	links = soup.findAll('a', {'class' : 'footer'})

	tNames = [x.string for x in links]
	tUrls = [y['href'] for y in links]

	theaters = []

	for index, t in enumerate(tNames):
		theaters.append({'name': t.strip(), 'url': baseUrl + '/' + tUrls[index]})
		
		if max_theaters > 0:
			if index >= max_theaters:
				break

	return theaters


def getMovieList():
	res = getPage(baseUrl)
	
	soup = BeautifulSoup(res)
	links = soup.findAll('a', {'class' : 'COMINGSOONLIST'})
	
	titles = [x.string.rstrip() for x in links]
	mUrls = [y['href'] for y in links]
	
	movies = []
	
	for index, t in enumerate(titles):
		movies.append({'title': t, 'url': baseUrl + "/" + mUrls[index]})
		
	return movies


def getPage(url):
	
	userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = { 'User-Agent' : userAgent }
	
	req = urllib2.Request(url, '', headers)
	response = urllib2.urlopen(req)
	return response.read()
		

if __name__ == '__main__':
	main()