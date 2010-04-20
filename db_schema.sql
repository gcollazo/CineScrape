# Dump of table movies
# ------------------------------------------------------------

DROP TABLE IF EXISTS `movies`;

CREATE TABLE `movies` (
  `id` int(11) NOT NULL auto_increment,
  `theater_id` int(11) default NULL,
  `name` text,
  `period1` text,
  `period2` text,
  `period3` text,
  `period4` text,
  PRIMARY KEY  (`id`),
  KEY `theater_id` (`theater_id`),
  CONSTRAINT `movies_ibfk_1` FOREIGN KEY (`theater_id`) REFERENCES `theaters` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table theaters
# ------------------------------------------------------------

DROP TABLE IF EXISTS `theaters`;

CREATE TABLE `theaters` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
