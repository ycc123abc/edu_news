/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 80036 (8.0.36)
 Source Host           : localhost:3306
 Source Schema         : test

 Target Server Type    : MySQL
 Target Server Version : 80036 (8.0.36)
 File Encoding         : 65001

 Date: 18/07/2025 09:27:45
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for professionalscore
-- ----------------------------
DROP TABLE IF EXISTS `professionalscore`;
CREATE TABLE `professionalscore`  (
  `url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `year` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sign` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `school` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `province_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `school_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `special_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `batch` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `max` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `min` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `average` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `min_section` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `lq_num` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `province` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `spe_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `special_group` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `first_km` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_fxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_sxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_xuanke` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `is_score_range` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `min_range` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `min_rank_range` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level1_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level2_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level3_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level2` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level3` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `spname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `local_batch_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `diff` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_fxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_sxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_xuanke` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `range_max_rank` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for provincescore
-- ----------------------------
DROP TABLE IF EXISTS `provincescore`;
CREATE TABLE `provincescore`  (
  `url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `year` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sign` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `school` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `province_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `school_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `province_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `batch` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `xclevel` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `max` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `min_section` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `min` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `average` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `filing` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `special_group` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `first_km` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `num` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `local_province_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `local_type_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `local_batch_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `local_batch_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `xclevel_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx_rank` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_fxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_sxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `proscore` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `diff` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for specialplan
-- ----------------------------
DROP TABLE IF EXISTS `specialplan`;
CREATE TABLE `specialplan`  (
  `year` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sign` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `school` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `province_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `school_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `special_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `batch` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `num` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `province` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `length` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `tuition` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `spe_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `special_group` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `first_km` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_fxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_sxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_xuanke` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_fxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_sxk` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sg_xuanke` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level1_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level2_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level3_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level2` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `level3` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `spcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `spname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `sp_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `local_batch_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `zslx_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
