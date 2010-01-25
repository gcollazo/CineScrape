#!/usr/bin/env python
# encoding: utf-8
"""
cinescraper.py

This app scrapes the showtime info from
http://www.caribbeancinemas.com

Created by Giovanni Collazo on 2010-01-24.
Copyright (c) 2010 24veces.com. All rights reserved.
"""

import urllib2
import re
from BeautifulSoup import BeautifulSoup
baseUrl = "http://www.caribbeancinemas.com"


def main():
	
	allData = getAllData()
	
	for t in allData:
		print "********** " + t['theaterName'] + " **********"
		
		sql = "INSERT INTO theater (name) VALUES ('" + t['theaterName'] + "');\n"
		sql += "SET @theater_id := LAST_INSERT_ID();\n"
				
		for x in t['data']:
			print x['movieName']
			
			sql += "INSERT INTO movie (name) VALUES ('" + x['movieName'] + "');\n"
			sql += "SET @movie_id := LAST_INSERT_ID();\n"
			sql += "INSERT INTO schedule (movie_id, theater_id) VALUES (@movie_id,@theater_id);\n"
			sql += "SET @schedule_id := LAST_INSERT_ID();\n"
			
			p = re.compile(r',')
			
			print 'MON-FRI: ' + x['showtimes'][0]
			
			for time in p.split(x['showtimes'][0]):
				sql += "INSERT INTO schedule_hour (schedule_id, day_M, day_T, day_W, day_Th, day_F, day_Sa, day_Su, time) "
				sql += " VALUES (@schedule_id,'1','1','1','1','1','0','0','" + time.strip() + "');\n"
			
			print 'SAT: ' + x['showtimes'][1]
			for time in p.split(x['showtimes'][1]):
				sql += "INSERT INTO schedule_hour (schedule_id, day_M, day_T, day_W, day_Th, day_F, day_Sa, day_Su, time) "
				sql += " VALUES (@schedule_id,'0','0','0','0','0','1','0','" + time.strip() + "');\n"

			print 'SUN & HOL: ' + x['showtimes'][2]
			for time in p.split(x['showtimes'][2]):
				sql += "INSERT INTO schedule_hour (schedule_id, day_M, day_T, day_W, day_Th, day_F, day_Sa, day_Su, time) "
				sql += " VALUES (@schedule_id,'0','0','0','0','0','0','1','" + time.strip() + "');\n"

			print "============================="
		print "\n\n"
		
		print "SQL: \n"
		print sql
		

def getAllData():
	theaters = getTheaterList()
	result = []
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
	
	times = []
	for t in dayHeaders:
		times.append(t.nextSibling.next)
	
	result = []
	i = 0
	for n in movieNames:
		result.append({'movieName':n, 'showtimes':[times[i*3], times[i*3+1], times[i*3+1]] })
		i = i+1
	
	return result


def getTheaterList():
	res = getPage(baseUrl)

	soup = BeautifulSoup(res)
	links = soup.findAll('a', {'class' : 'footer'})

	tNames = [x.string for x in links]
	tUrls = [y['href'] for y in links]

	theaters = []

	i = 0
	for t in tNames:
		theaters.append({'name': t, 'url': baseUrl + '/' + tUrls[i]})
		i = i+1
		#break
	
	return theaters


def getMovieList():
	res = getPage(baseUrl)
	
	soup = BeautifulSoup(res)
	links = soup.findAll('a', {'class' : 'COMINGSOONLIST'})
	
	titles = [x.string.rstrip() for x in links]
	mUrls = [y['href'] for y in links]
	
	movies = []
	
	i = 0
	for t in titles:
		movies.append({'title': t, 'url': baseUrl + "/" + mUrls[i]})
		i = i+1
		
	return movies


def getPage(url):
	
	userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = { 'User-Agent' : userAgent }
	
	req = urllib2.Request(url, '', headers)
	response = urllib2.urlopen(req)
	return response.read()
		

if __name__ == '__main__':
	main()