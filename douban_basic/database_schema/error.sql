/*
 Navicat Premium Data Transfer

 Source Server         : PythonDouban
 Source Server Type    : SQLite
 Source Server Version : 3012001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3012001
 File Encoding         : 65001

 Date: 27/02/2019 15:58:30
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for error
-- ----------------------------
DROP TABLE IF EXISTS "error";
CREATE TABLE "error" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "subject_id" TEXT,
  "year" INTEGER,
  UNIQUE ("subject_id" COLLATE BINARY ASC) ON CONFLICT IGNORE
);

PRAGMA foreign_keys = true;
