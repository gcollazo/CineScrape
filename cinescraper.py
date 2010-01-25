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
from BeautifulSoup import BeautifulSoup
baseUrl = "http://www.caribbeancinemas.com"


def main():
	
	allData = getAllData()
	
	for t in allData:
		print "********** " + t['theaterName'] + " **********"
	
		for x in t['data']:
			print x['movieName']	
			print 'MON-FRI: ' + x['showtimes'][0]
			print 'SAT: ' + x['showtimes'][1]
			print 'SUN & HOL: ' + x['showtimes'][2]
			print "============================="
		print "\n\n"


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