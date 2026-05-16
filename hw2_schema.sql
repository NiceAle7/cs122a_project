DROP DATABASE IF EXISTS cs122a_hw2;
CREATE DATABASE cs122a_hw2;
USE cs122a_hw2;

-- Define entities and their supporting tables below here


-- Q1: User and Organizer/Participant/Administrator (SQL DDL for entity(ies) table(s) only)

-- User Table (10 points)
CREATE TABLE User (
    uid INT,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    joined DATE NOT NULL,
    PRIMARY KEY (uid)
);

-- Organizer (Delta Table for ISA Relationship) (10 points)
CREATE TABLE Organizer (
    uid INT,
    department TEXT NOT NULL,
    experience INT NOT NULL,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
);

-- Participant (Delta Table for ISA Relationship) (10 points)
CREATE TABLE Participant (
    uid INT,
    type TEXT,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
);

-- Administrator (Delta Table for ISA Relationship)(10 points)
CREATE TABLE Administrator (
    uid INT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
);


-- Q2: Event and Slot (SQL DDL for entity(ies) table(s) only)

-- Event Table(10 points)
CREATE TABLE Event (
    eid INT,
    creator_uid INT NOT NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    PRIMARY KEY (eid),
    FOREIGN KEY (creator_uid) REFERENCES Organizer(uid) ON DELETE CASCADE
);

-- Slot Table (Weak Entity)(10 points)
CREATE TABLE Slot (
    eid INT,
    snum INT NOT NULL,
    is_reserved BOOLEAN NOT NULL,
    uid INT,
    PRIMARY KEY (eid, snum),
    FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
    FOREIGN KEY (uid) REFERENCES Participant(uid) ON DELETE CASCADE
);

-- Q3: Venue and OnCampus / OffCampus (SQL DDL for entity(ies) table(s) only)

-- Venue Table (10 points)
CREATE TABLE Venue (
    vid INT,
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    PRIMARY KEY (vid)
);

-- OnCampus Table (5 points)
CREATE TABLE OnCampus (
    vid INT,
    code TEXT NOT NULL,
    PRIMARY KEY (vid),
    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
);

-- OffCampus Table (5 points)
CREATE TABLE OffCampus (
    vid INT,
    distance INT NOT NULL,
    PRIMARY KEY (vid),
    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
);

-- Q4: Write additional SQL DDL for relationship(s) table(s) below (20 points)

-- Hosting Relation Table (10 points)
CREATE TABLE Hosting (
    eid INT NOT NULL,
    vid INT NOT NULL,
    is_primary BOOLEAN NOT NULL,
    PRIMARY KEY (eid, vid),
    FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
);

-- Approval Relation Table (10 points)
CREATE TABLE Approval (
    uid INT NOT NULL,
    vid INT NOT NULL,
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    PRIMARY KEY (uid, vid),
    FOREIGN KEY (uid) REFERENCES Administrator(uid) ON DELETE CASCADE,
    FOREIGN KEY (vid) REFERENCES OffCampus(vid) ON DELETE CASCADE
);
