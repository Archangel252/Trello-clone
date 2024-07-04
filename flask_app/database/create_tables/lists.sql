CREATE TABLE IF NOT EXISTS `lists` (
`list_id`         int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this list',
`board_id`         int(11)  	   NOT NULL 	  COMMENT 'the id of this board',
`name`            varchar(10)  NOT NULL                   COMMENT 'name of the board',
PRIMARY KEY (`list_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site board information";