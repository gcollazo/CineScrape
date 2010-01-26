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
import sys
import getopt
from BeautifulSoup import BeautifulSoup
baseUrl = "http://www.caribbeancinemas.com"

schema = """
CREATE TABLE IF NOT EXISTS `theater` (
  `id` int(11) NOT NULL auto_increment,
  `name` text,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `movie` (
  `id` int(11) NOT NULL auto_increment,
  `name` text,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `schedule` (
  `id` int(11) NOT NULL auto_increment,
  `movie_id` int(11) default NULL,
  `theater_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `schedule_hour` (
  `id` int(11) NOT NULL auto_increment,
  `day_M` varchar(1) default '0',
  `day_T` varchar(1) default '0',
  `day_W` varchar(1) default '0',
  `day_Th` varchar(1) default '0',
  `day_F` varchar(1) default '0',
  `day_Sa` varchar(1) default '0',
  `day_Su` varchar(1) default '0',
  `time` varchar(10) default NULL,
  `schedule_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

delimiter //

DROP PROCEDURE IF EXISTS cleanup_movies//

CREATE PROCEDURE cleanup_movies()
BEGIN

SELECT @num_repeats := SUM(1)  FROM (SELECT *, SUM(1) as count FROM movie GROUP by name ORDER BY id) as movies WHERE movies.count > 1 INTO @null;

repeat_label: LOOP

SELECT id FROM (SELECT @id := id as id, @name := name FROM (SELECT *, SUM(1) as count FROM movie GROUP by name ORDER BY id) as movies WHERE count > 1 LIMIT 1) as temp1 INTO @null;
UPDATE schedule SET movie_id = @id WHERE movie_id IN (SELECT id FROM movie WHERE name = @name);
DELETE FROM movie WHERE name = @name AND id <> @id;

SELECT @num_repeats := SUM(1)  FROM (SELECT *, SUM(1) as count FROM movie GROUP by name ORDER BY id) as movies WHERE movies.count > 1 INTO @null;

IF @num_repeats > 0 THEN ITERATE repeat_label; END IF;

LEAVE repeat_label;
END LOOP repeat_label;

END//

delimiter ;

"""

def main(argv):
	
	try:
		opts, args = getopt.getopt(argv, "tscn:h", ["text", "sql", "create"])
	except getopt.GetoptError:
		print "ERROR: Did not understand arguments\n"
		usage()
		sys.exit(2)
	
	output = "sql"
	max_theaters = 0
	create = 0
	
	for opt, arg in opts:
		if opt in ("-t", "--text"):
			output = "text"
		elif opt in ("-s", "--sql"):
			output = "sql"
		elif opt in ("-c", "--create"):
			create = 1
		elif opt in ("-n"):
			max_theaters = int(arg)
		elif opt in ("-h"):
			usage()
			sys.exit(0)
			
	
	allData = getAllData(max_theaters)
	
	sql = "DELETE FROM movie; DELETE FROM schedule; DELETE FROM schedule_hour; DELETE FROM theater;"
	
	for t in allData:
		text = "********** " + t['theaterName'] + " **********\n"
		
		sql += "INSERT INTO theater (name) VALUES ('" + t['theaterName'].replace('\'','\\\'') + "');\n"
		sql += "SET @theater_id := LAST_INSERT_ID();\n"
				
		for x in t['data']:
			text += x['movieName'] + "\n"
			
			sql += "INSERT INTO movie (name) VALUES ('" + x['movieName'].replace('\'','\\\'') + "');\n"
			sql += "SET @movie_id := LAST_INSERT_ID();\n"
			sql += "INSERT INTO schedule (movie_id, theater_id) VALUES (@movie_id,@theater_id);\n"
			sql += "SET @schedule_id := LAST_INSERT_ID();\n"
			
			p = re.compile(r',')
			
			text += 'MON-FRI: ' + x['showtimes'][0]	+ "\n"
			for time in p.split(x['showtimes'][0]):
				sql += "INSERT INTO schedule_hour (schedule_id, day_M, day_T, day_W, day_Th, day_F, day_Sa, day_Su, time) "
				sql += " VALUES (@schedule_id,'1','1','1','1','1','0','0','" + timeTo24Hrs(time.strip()) + "');\n"
			
			text += 'SAT: ' + x['showtimes'][1]	+ "\n"
			for time in p.split(x['showtimes'][1]):
				sql += "INSERT INTO schedule_hour (schedule_id, day_M, day_T, day_W, day_Th, day_F, day_Sa, day_Su, time) "
				sql += " VALUES (@schedule_id,'0','0','0','0','0','1','0','" + timeTo24Hrs(time.strip()) + "');\n"

			text += 'SUN & HOL: ' + x['showtimes'][2]	+ "\n"
			for time in p.split(x['showtimes'][2]):
				sql += "INSERT INTO schedule_hour (schedule_id, day_M, day_T, day_W, day_Th, day_F, day_Sa, day_Su, time) "
				sql += " VALUES (@schedule_id,'0','0','0','0','0','0','1','" + timeTo24Hrs(time.strip()) + "');\n"

			text += "=============================\n"
		text += "\n\n\n"
		
		sql += "CALL cleanup_movies;\n"
		
		if output == 'sql':
			if create == 1:
				print schema
			print sql.encode('ascii', 'xmlcharrefreplace')
			
		else:
			print text.encode('ascii', 'xmlcharrefreplace')

def usage():
	print "usage: " + sys.argv[0] + " [-s|--sql] [-t|--text] [-c|--create] [-n limit]\n"
	print "Options:"
	print "\t-c, --create:\tOutput schema"
	print "\t-s, --sql:\tOutput in SQL for piping to mysql"
	print "\t-t, --text:\tOutput in human readable"
	print "\t-n limit:\tOutput from n theaters only"
	print "\t-h:\t\tThis message"

def timeTo24Hrs(time12):
	stripped_time = time12.strip()
	
	split_hour = re.compile(r':')
	split_ampm = re.compile(r' ')
	
	hour_min = split_hour.split(stripped_time)
	min_ampm = split_ampm.split(hour_min[1])
	
	hour = hour_min[0]
	minute = min_ampm[0]
	ampm = min_ampm[1]
	
	
	if ampm.upper() == 'AM':
		ret = (hour + minute).rjust(4,"0")
	else:
		ret = str(int(hour) + 12) + minute
	
	# print stripped_time + " ==> " + ret
	
	return ret
	
	
def getAllData(max_theaters):
	theaters = getTheaterList(max_theaters)
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


def getTheaterList(max_theaters):
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
		
		if max_theaters > 0:
			if i >= max_theaters:
				break

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
	main(sys.argv[1:])