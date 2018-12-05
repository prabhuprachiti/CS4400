CREATE TABLE user_base ( -- a user can't be just in the user_base table, the user also has to be in admin, staff or visitor!
    username VARCHAR(255) NOT NULL,
    email    VARCHAR(255) NOT NULL,
    pwd      BINARY(32) NOT NULL, -- SHA-256 hashed password
    type     ENUM('admin', 'staff', 'visitor'),

    PRIMARY KEY (username),
    UNIQUE (email)
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE admin (
    username VARCHAR(255) NOT NULL,
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES user_base(username) ON DELETE CASCADE ON UPDATE CASCADE -- users have to be deleted by deleting an entry in user_base
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE staff (
    username VARCHAR(255) NOT NULL,
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES user_base(username) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE visitor (
    username VARCHAR(255) NOT NULL,
    PRIMARY KEY (username),
    FOREIGN KEY (username) REFERENCES user_base(username) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = INNODB, CHARSET=utf8;


CREATE TABLE exhibit (
    name     VARCHAR(255) NOT NULL,
    haswater BOOL NOT NULL,
    exhsize  INT NOT NULL,

    PRIMARY KEY (name)
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE exhibit_show (
    name      VARCHAR(255) NOT NULL,
    showtime  DATETIME NOT NULL,
    exhname   VARCHAR(255) NOT NULL,
    hostname  VARCHAR(255) NOT NULL,

    PRIMARY KEY (name, showtime),
    FOREIGN KEY (exhname) REFERENCES exhibit(name) ON DELETE RESTRICT ON UPDATE CASCADE, -- we generally don't want to delete (old) exhibits or shows so users can still track visits to them
    FOREIGN KEY (hostname) REFERENCES staff(username) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE animal (
    name    VARCHAR(255) NOT NULL,
    species VARCHAR(255) NOT NULL,
    type    ENUM('mammal', 'bird', 'amphibian', 'reptile', 'fish', 'invertebrate') NOT NULL,
    age     INT UNSIGNED NOT NULL,
    exhname VARCHAR(255) NOT NULL,

    PRIMARY KEY (name, species),
    FOREIGN KEY (exhname) REFERENCES exhibit(name) ON DELETE RESTRICT ON UPDATE CASCADE -- do not delete an exhibit without first moving or deleting the animals in it!
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE note (
    subjname    VARCHAR(255) NOT NULL,
    subjspecies VARCHAR(255) NOT NULL,
    authuname   VARCHAR(255) NOT NULL,
    notetime    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notetext    TEXT,

    PRIMARY KEY (subjname, subjspecies, authuname, notetime),
    FOREIGN KEY (subjname, subjspecies) REFERENCES animal(name, species) ON DELETE CASCADE ON UPDATE CASCADE, -- we don't need notes for an animal that doesn't exist
    FOREIGN KEY (authuname) REFERENCES staff(username) ON DELETE CASCADE ON UPDATE CASCADE -- a deleted staff's notes are, sadly, deleted...
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE show_visit (
    name          VARCHAR(255) NOT NULL,
    time          DATETIME NOT NULL, -- show time
    visitoruname  VARCHAR(255) NOT NULL,

    PRIMARY KEY (name, time, visitoruname),
    FOREIGN KEY (name, time) REFERENCES exhibit_show(name, showtime) ON DELETE CASCADE ON UPDATE CASCADE, -- old exhibits and shows are not deleted so users can still track visits to them
    FOREIGN KEY (visitoruname) REFERENCES visitor(username) ON DELETE CASCADE ON UPDATE CASCADE -- we don't need to keep data for a deleted visitor account
) ENGINE = INNODB, CHARSET=utf8;

CREATE TABLE exhibit_visit (
    name           VARCHAR(255) NOT NULL,
    time           DATETIME NOT NULL, -- exhibit visit time
    visitoruname   VARCHAR(255) NOT NULL,

    PRIMARY KEY (name, visitoruname, time),
    FOREIGN KEY (name) REFERENCES exhibit(name) ON DELETE RESTRICT ON UPDATE CASCADE, -- old exhibits and shows are deleted and users can't track visits to them!
    FOREIGN KEY (visitoruname) REFERENCES visitor(username) ON DELETE CASCADE ON UPDATE CASCADE -- we don't need to keep data for a deleted visitor account
) ENGINE = INNODB, CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1; 

INSERT INTO user_base(username, email, pwd, type) VALUES ('admin', 'admin@website.com', UNHEX(/*SHA2('password', 256)*/'5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'), 'admin');
INSERT INTO admin(username) VALUES ('admin');

INSERT INTO exhibit(name, haswater, exhsize) VALUES
('Pacific', 1, 850),
('Jungle', 0, 600),
('Sahara', 0, 1000),
('Mountainous', 0, 1200),
('Birds', 1, 1000);
