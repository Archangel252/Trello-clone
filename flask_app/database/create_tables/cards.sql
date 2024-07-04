CREATE TABLE IF NOT EXISTS `cards` (
`card_id`         int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this card',
`board_id`         int(11)  	   NOT NULL 	  COMMENT 'the id of this cards board',
`list_id`         int(11)  	   NOT NULL 	  COMMENT 'the id of this cards list',
`content`            varchar(100)  NOT NULL                   COMMENT 'content of the card',
PRIMARY KEY (`card_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id),
FOREIGN KEY (list_id) REFERENCES lists(list_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site board information";