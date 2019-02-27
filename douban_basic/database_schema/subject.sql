/*
 Navicat Premium Data Transfer

 Source Server         : PythonDouban
 Source Server Type    : SQLite
 Source Server Version : 3012001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3012001
 File Encoding         : 65001

 Date: 27/02/2019 15:55:02
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for subject
-- ----------------------------
DROP TABLE IF EXISTS "subject";
CREATE TABLE "subject" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "subject_id" text,
  "type" text,
  "name" text,
  "year" integer,
  "rating_value" real,
  "rating_count" integer,
  "image" text,
  "url" text,
  "duration" integer,
  "genre" text,
  "directors" text,
  "authors" text,
  "actors" text,
  "release" text,
  "districts" text,
  "imdb" text,
  "remark" text,
  UNIQUE ("subject_id" COLLATE BINARY ASC) ON CONFLICT IGNORE
);

PRAGMA foreign_keys = true;
