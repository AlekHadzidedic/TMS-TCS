CREATE SCHEMA IF NOT EXISTS tms;


CREATE TABLE IF NOT EXISTS tms.instructor (
  id                SERIAL PRIMARY KEY,
  first_name        VARCHAR (20) NOT NULL,
  last_name         VARCHAR (50) NOT NULL,
  email             VARCHAR (50) NOT NULL UNIQUE,
  password          TEXT
);

CREATE TABLE IF NOT EXISTS tms.team (
  id                SERIAL PRIMARY KEY,
  name              VARCHAR (50) NOT NULL UNIQUE,
  max_team_size     INTEGER,
  team_size         INTEGER
);

CREATE TABLE IF NOT EXISTS tms.student (
  id                SERIAL PRIMARY KEY,
  first_name        VARCHAR (20) NOT NULL,
  last_name         VARCHAR (50) NOT NULL,
  student_number    INTEGER,
  email             VARCHAR (50) NOT NULL UNIQUE,
  password          TEXT,
  is_liason         boolean,
  team_id SERIAL REFERENCES tms.team (id) ON DELETE RESTRICT
);

