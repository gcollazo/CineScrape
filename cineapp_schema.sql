# Sequel Pro dump
# Version 1630
# http://code.google.com/p/sequel-pro
#
# Generation Time: 2010-01-25 16:18:25 -0400
# ************************************************************


# Dump of table movie
# ------------------------------------------------------------

CREATE TABLE `movie` (
  `id` int(11) NOT NULL auto_increment,
  `name` text character set latin1,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table schedule
# ------------------------------------------------------------

CREATE TABLE `schedule` (
  `id` int(11) NOT NULL auto_increment,
  `movie_id` int(11) default NULL,
  `theater_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table schedule_hour
# ------------------------------------------------------------

CREATE TABLE `schedule_hour` (
  `id` int(11) NOT NULL auto_increment,
  `day_M` varchar(1) character set latin1 default '0',
  `day_T` varchar(1) character set latin1 default '0',
  `day_W` varchar(1) character set latin1 default '0',
  `day_Th` varchar(1) character set latin1 default '0',
  `day_F` varchar(1) character set latin1 default '0',
  `day_Sa` varchar(1) character set latin1 default '0',
  `day_Su` varchar(1) character set latin1 default '0',
  `time` varchar(10) character set latin1 default NULL,
  `schedule_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table theater
# ------------------------------------------------------------

CREATE TABLE `theater` (
  `id` int(11) NOT NULL auto_increment,
  `name` text character set latin1,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

