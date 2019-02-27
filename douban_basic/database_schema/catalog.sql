/*
 Navicat Premium Data Transfer

 Source Server         : PythonDouban
 Source Server Type    : SQLite
 Source Server Version : 3012001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3012001
 File Encoding         : 65001

 Date: 27/02/2019 15:54:09
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for catalog
-- ----------------------------
DROP TABLE IF EXISTS "catalog";
CREATE TABLE "catalog" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "subject_id" TEXT,
  "title" TEXT,
  "year" INTEGER,
  "rate" REAL,
  "url" TEXT,
  "is_handle" INTEGER NOT NULL DEFAULT 0,
  UNIQUE ("subject_id" COLLATE BINARY ASC) ON CONFLICT REPLACE
);

PRAGMA foreign_keys = true;
