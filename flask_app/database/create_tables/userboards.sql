CREATE TABLE IF NOT EXISTS `userboards` (
`board_id`         int(11)    NOT NULL 	  COMMENT 'the id of this board',
`user_id`            int(11)  NOT NULL                   COMMENT 'id of theb user with access',
FOREIGN KEY (board_id) REFERENCES boards(board_id),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site board information";