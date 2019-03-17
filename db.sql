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

CREATE TABLE `tickets` (
    `ID` int(11) NOT NULL AUTO_INCREMENT,
    `title` varchar(100) NOT NULL,
    `body` varchar(100) NOT NULL,
    `status` int(11) NOT NULL,
    `userID` int(11) NOT NULL,
    FOREIGN KEY (`userID`) References `users` (`ID`),
    PRIMARY KEY (`ID`)
)ENGINE=InnoDB;

INSERT INTO `users` VALUES (1,'amir','11041104','','','8534780b4edccd5904fe6d6110b76624',0);


