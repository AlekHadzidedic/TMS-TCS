CREATE SCHEMA IF NOT EXISTS tms;


CREATE TABLE IF NOT EXISTS tms.instructor (
  id                SERIAL PRIMARY KEY,
  first_name        VARCHAR (20) NOT NULL,
  last_name         VARCHAR (50) NOT NULL,
  email             VARCHAR (50) NOT NULL UNIQUE,
  password          VARCHAR (255)
);

CREATE TABLE IF NOT EXISTS tms.team (
  id                SERIAL PRIMARY KEY,
  team_name         VARCHAR (50) NOT NULL UNIQUE,
  max_team_size     INTEGER,
  min_team_size     INTEGER,
  team_size         INTEGER
);

CREATE TABLE IF NOT EXISTS tms.student (
  id                SERIAL PRIMARY KEY,
  first_name        VARCHAR (20) NOT NULL,
  last_name         VARCHAR (50) NOT NULL,
  student_number    INTEGER NOT NULL UNIQUE,
  email             VARCHAR (50) NOT NULL UNIQUE,
  password          VARCHAR (255),
  is_liason         BOOLEAN,
  team_name VARCHAR (50) REFERENCES tms.team (team_name) ON DELETE RESTRICT

);

CREATE TABLE IF NOT EXISTS tms.team_parameters (
  id                    SERIAL PRIMARY KEY,
  max_team_size         INTEGER,
  min_team_size         INTEGER,
  are_parameters_set    BOOLEAN
);

CREATE TABLE IF NOT EXISTS tms.team_request (
  id                    SERIAL PRIMARY KEY,
  team_name VARCHAR (50) REFERENCES tms.team (team_name) ON DELETE RESTRICT,
  student_email VARCHAR (50) REFERENCES tms.student (email) ON DELETE RESTRICT,
  request_status VARCHAR (50),
  student_name VARCHAR (100)
);