CREATE TABLE `users` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `fname` varchar(100) NULL,
  `lname` varchar(100) NULL,
  `api` varchar(50) DEFAULT NULL,
  `role` int(11) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB;

INSERT INTO `users` VALUES (1,'amir','11041104','','','8534780b4edccd5904fe6d6110b76624',0);


