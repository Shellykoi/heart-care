-- heart_care_postgres.sql
-- 转换规则：
--  AUTO_INCREMENT -> SERIAL
--  datetime -> timestamp
--  tinyint(1) -> boolean
--  enum(...) -> text CHECK (col IN (...))
--  删除 ENGINE/CHARSET/COLLATE/ROW_FORMAT
--  保留 DEFAULT CURRENT_TIMESTAMP
--  为每个 SERIAL 创建后的序列设置 setval(..., max(id))

BEGIN;

-- client encoding
SET client_encoding = 'UTF8';

-- ---------- appointments ----------
DROP TABLE IF EXISTS appointments CASCADE;
CREATE TABLE appointments (
  id               SERIAL PRIMARY KEY,
  user_id          integer,
  counselor_id     integer,
  consult_type     varchar(100),
  consult_method   varchar(50) NOT NULL,
  appointment_date timestamp NOT NULL,
  description      text,
  status           text CHECK (status IN ('PENDING','CONFIRMED','COMPLETED','CANCELLED','REJECTED')),
  summary          text,
  review           text,
  created_at       timestamp DEFAULT CURRENT_TIMESTAMP,
  updated_at       timestamp,
  user_confirmed_complete boolean DEFAULT false,
  counselor_confirmed_complete boolean DEFAULT false
);
CREATE INDEX ix_appointments_user_id ON appointments (user_id);
CREATE INDEX ix_appointments_counselor_id ON appointments (counselor_id);

-- ---------- comments ----------
DROP TABLE IF EXISTS comments CASCADE;
CREATE TABLE comments (
  id         SERIAL PRIMARY KEY,
  post_id    integer,
  user_id    integer,
  content    text NOT NULL,
  like_count integer,
  is_approved boolean,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_comments_post_id ON comments (post_id);
CREATE INDEX ix_comments_user_id ON comments (user_id);

-- ---------- community_posts ----------
DROP TABLE IF EXISTS community_posts CASCADE;
CREATE TABLE community_posts (
  id           SERIAL PRIMARY KEY,
  author_id    integer,
  category     varchar(50) NOT NULL,
  content      text NOT NULL,
  tags         varchar(200),
  like_count   integer,
  comment_count integer,
  is_approved  boolean,
  is_deleted   boolean,
  created_at   timestamp DEFAULT CURRENT_TIMESTAMP,
  report_count integer DEFAULT 0
);
CREATE INDEX ix_community_posts_author_id ON community_posts (author_id);

-- ---------- consultation_records ----------
DROP TABLE IF EXISTS consultation_records CASCADE;
CREATE TABLE consultation_records (
  id                    SERIAL PRIMARY KEY,
  appointment_id        integer,
  user_id               integer,
  counselor_id          integer,
  consult_type          varchar(100),
  consult_method        varchar(50) NOT NULL,
  appointment_date      timestamp NOT NULL,
  description           text,
  summary               text,
  rating                integer,
  review                text,
  user_confirmed_at     timestamp,
  counselor_confirmed_at timestamp,
  created_at            timestamp DEFAULT CURRENT_TIMESTAMP,
  updated_at            timestamp
);
CREATE UNIQUE INDEX ux_consultation_records_appointment_id ON consultation_records (appointment_id);
CREATE INDEX ix_consultation_records_user_id ON consultation_records (user_id);
CREATE INDEX ix_consultation_records_counselor_id ON consultation_records (counselor_id);

-- ---------- content_likes ----------
DROP TABLE IF EXISTS content_likes CASCADE;
CREATE TABLE content_likes (
  id          SERIAL PRIMARY KEY,
  user_id     integer,
  content_type varchar(20) NOT NULL,
  content_id  integer NOT NULL,
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_content_likes_user_id ON content_likes (user_id);

-- ---------- contents ----------
DROP TABLE IF EXISTS contents CASCADE;
CREATE TABLE contents (
  id          SERIAL PRIMARY KEY,
  title       varchar(200) NOT NULL,
  content_type varchar(20) NOT NULL,
  category    varchar(50),
  content     text,
  media_url   varchar(500),
  cover_image varchar(500),
  duration    varchar(20),
  author      varchar(100),
  tags        varchar(200),
  view_count  integer,
  like_count  integer,
  is_published boolean,
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP,
  updated_at  timestamp
);

-- ---------- counselor_favorites ----------
DROP TABLE IF EXISTS counselor_favorites CASCADE;
CREATE TABLE counselor_favorites (
  id          SERIAL PRIMARY KEY,
  user_id     integer NOT NULL,
  counselor_id integer NOT NULL,
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, counselor_id)
);
CREATE INDEX ix_counselor_favorites_user_id ON counselor_favorites (user_id);
CREATE INDEX ix_counselor_favorites_counselor_id ON counselor_favorites (counselor_id);

-- ---------- counselor_ratings ----------
DROP TABLE IF EXISTS counselor_ratings CASCADE;
CREATE TABLE counselor_ratings (
  id           SERIAL PRIMARY KEY,
  appointment_id integer,
  user_id      integer,
  counselor_id integer,
  rating       integer NOT NULL,
  review       text,
  created_at   timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX ux_counselor_ratings_appointment_id ON counselor_ratings (appointment_id);
CREATE INDEX ix_counselor_ratings_user_id ON counselor_ratings (user_id);
CREATE INDEX ix_counselor_ratings_counselor_id ON counselor_ratings (counselor_id);

-- ---------- counselor_schedules ----------
DROP TABLE IF EXISTS counselor_schedules CASCADE;
CREATE TABLE counselor_schedules (
  id            SERIAL PRIMARY KEY,
  counselor_id  integer,
  weekday       integer NOT NULL,
  start_time    varchar(10) NOT NULL,
  end_time      varchar(10) NOT NULL,
  max_num       integer NOT NULL DEFAULT 1,
  is_available  boolean
);
CREATE INDEX ix_counselor_schedules_counselor_id ON counselor_schedules (counselor_id);

-- ---------- counselor_unavailable ----------
DROP TABLE IF EXISTS counselor_unavailable CASCADE;
CREATE TABLE counselor_unavailable (
  id          SERIAL PRIMARY KEY,
  counselor_id integer NOT NULL,
  start_date  date NOT NULL,
  end_date    date NOT NULL,
  start_time  time,
  end_time    time,
  reason      varchar(200),
  status      integer,
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_counselor_unavailable_counselor_id ON counselor_unavailable (counselor_id);

-- ---------- counselors ----------
DROP TABLE IF EXISTS counselors CASCADE;
CREATE TABLE counselors (
  id                 SERIAL PRIMARY KEY,
  user_id            integer UNIQUE,
  real_name          varchar(50) NOT NULL,
  gender             text CHECK (gender IN ('MALE','FEMALE','OTHER')) NOT NULL,
  specialty          varchar(200) NOT NULL,
  experience_years   integer NOT NULL,
  qualification      varchar(200),
  certificate_url    varchar(500),
  bio                text,
  intro              text,
  consult_methods    varchar(100),
  consult_type       text,
  fee                double precision,
  consult_place      varchar(255),
  max_daily_appointments integer,
  avatar             varchar(500),
  total_consultations integer,
  average_rating     double precision,
  review_count       integer,
  status             text CHECK (status IN ('PENDING','ACTIVE','INACTIVE','REJECTED')),
  created_at         timestamp DEFAULT CURRENT_TIMESTAMP,
  updated_at         timestamp,
  age                integer
);
CREATE INDEX ix_counselors_id ON counselors (id);

-- ---------- emergency_helps ----------
DROP TABLE IF EXISTS emergency_helps CASCADE;
CREATE TABLE emergency_helps (
  id         SERIAL PRIMARY KEY,
  user_id    integer,
  help_type  varchar(50) NOT NULL,
  content    text,
  status     varchar(20),
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_emergency_helps_user_id ON emergency_helps (user_id);

-- ---------- post_reports ----------
DROP TABLE IF EXISTS post_reports CASCADE;
CREATE TABLE post_reports (
  id         SERIAL PRIMARY KEY,
  post_id    integer NOT NULL,
  user_id    integer NOT NULL,
  reason     varchar(200),
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX ux_post_reports_post_user ON post_reports (post_id, user_id);
CREATE INDEX ix_post_reports_user_id ON post_reports (user_id);

-- ---------- private_messages ----------
DROP TABLE IF EXISTS private_messages CASCADE;
CREATE TABLE private_messages (
  id            SERIAL PRIMARY KEY,
  sender_id     integer,
  receiver_id   integer,
  content       text NOT NULL,
  is_read       boolean,
  is_deleted_by_sender boolean,
  is_deleted_by_receiver boolean,
  created_at    timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_private_messages_sender_id ON private_messages (sender_id);
CREATE INDEX ix_private_messages_receiver_id ON private_messages (receiver_id);

-- ---------- system_logs ----------
DROP TABLE IF EXISTS system_logs CASCADE;
CREATE TABLE system_logs (
  id         SERIAL PRIMARY KEY,
  user_id    integer,
  action     varchar(100) NOT NULL,
  detail     text,
  ip_address varchar(50),
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_system_logs_user_id ON system_logs (user_id);

-- ---------- test_reports ----------
DROP TABLE IF EXISTS test_reports CASCADE;
CREATE TABLE test_reports (
  id          SERIAL PRIMARY KEY,
  user_id     integer,
  scale_id    integer,
  score       integer NOT NULL,
  level       varchar(50),
  result_json text,
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_test_reports_user_id ON test_reports (user_id);
CREATE INDEX ix_test_reports_scale_id ON test_reports (scale_id);

-- ---------- test_scales ----------
DROP TABLE IF EXISTS test_scales CASCADE;
CREATE TABLE test_scales (
  id            SERIAL PRIMARY KEY,
  name          varchar(100) NOT NULL,
  abbreviation  varchar(20),
  category      varchar(50) NOT NULL,
  description   text,
  duration      varchar(20),
  question_count integer NOT NULL,
  questions_json text,
  is_active     boolean,
  created_at    timestamp DEFAULT CURRENT_TIMESTAMP
);

-- ---------- user_blocks ----------
DROP TABLE IF EXISTS user_blocks CASCADE;
CREATE TABLE user_blocks (
  id         SERIAL PRIMARY KEY,
  blocker_id integer,
  blocked_id integer,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_user_blocks_blocker_id ON user_blocks (blocker_id);
CREATE INDEX ix_user_blocks_blocked_id ON user_blocks (blocked_id);

-- ---------- user_favorites ----------
DROP TABLE IF EXISTS user_favorites CASCADE;
CREATE TABLE user_favorites (
  id          SERIAL PRIMARY KEY,
  user_id     integer,
  content_type varchar(20) NOT NULL,
  content_id  integer NOT NULL,
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_user_favorites_user_id ON user_favorites (user_id);

-- ---------- users ----------
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
  id          SERIAL PRIMARY KEY,
  username    varchar(50) NOT NULL UNIQUE,
  phone       varchar(20),
  email       varchar(100),
  student_id  varchar(50),
  password_hash varchar(255) NOT NULL,
  nickname    varchar(50),
  gender      text CHECK (gender IN ('MALE','FEMALE','OTHER')),
  age         integer,
  school      varchar(100),
  role        text CHECK (role IN ('USER','COUNSELOR','VOLUNTEER','ADMIN')),
  is_active   boolean,
  is_anonymous boolean,
  show_test_results boolean,
  record_retention varchar(20),
  created_at  timestamp DEFAULT CURRENT_TIMESTAMP,
  updated_at  timestamp,
  avatar      varchar(500)
);
CREATE UNIQUE INDEX ux_users_phone ON users (phone);
CREATE UNIQUE INDEX ux_users_email ON users (email);
CREATE UNIQUE INDEX ux_users_student_id ON users (student_id);

-- =========================
-- 插入数据（来自你的 MySQL 导出） —— 保留原 id 值
-- =========================

-- appointments records
INSERT INTO appointments (id, user_id, counselor_id, consult_type, consult_method, appointment_date, description, status, summary, review, created_at, updated_at, user_confirmed_complete, counselor_confirmed_complete) VALUES
(1, 2, 5, '心理咨询', '线上视频', '2025-11-07 15:00:00', NULL, 'COMPLETED', NULL, NULL, '2025-11-05 13:07:11', '2025-11-11 12:30:03', true, true),
(2, 2, 1, '心理咨询', '线下面谈', '2025-11-08 12:00:00', NULL, 'COMPLETED', '耶斯！！完成！！', NULL, '2025-11-05 13:18:43', '2025-11-12 22:48:52', true, true),
(3, 2, 1, '心理咨询', '线下面谈', '2025-11-05 18:00:00', NULL, 'COMPLETED', NULL, NULL, '2025-11-05 17:41:14', '2025-11-06 14:02:58', true, true),
(4, 2, 4, '心理咨询', '线上视频', '2025-11-11 12:00:00', NULL, 'PENDING', NULL, NULL, '2025-11-11 11:47:19', '2025-11-11 11:58:05', false, false),
(5, 2, 1, '心理咨询', '线上视频', '2025-11-11 17:00:00', NULL, 'COMPLETED', '嘻嘻很好！！❀❀', NULL, '2025-11-11 13:56:57', '2025-11-12 22:49:30', true, true),
(6, 8, 3, '心理咨询', '线上视频', '2025-11-11 14:00:00', NULL, 'PENDING', NULL, NULL, '2025-11-11 13:59:59', NULL, false, false),
(7, 8, 5, '心理咨询', '线上视频', '2025-11-11 18:00:00', NULL, 'COMPLETED', '耶斯很好！！( •̀ ω •́ )y', NULL, '2025-11-11 14:01:56', '2025-11-13 20:19:42', true, true),
(8, 2, 1, '心理咨询', '线上视频', '2025-11-13 14:00:00', '|END_TIME:2025-11-13T16:00:00', 'COMPLETED', '嘻嘻很好', NULL, '2025-11-13 13:11:08', '2025-11-14 10:47:03', true, true),
(9, 2, 5, '心理咨询', '线上视频', '2025-11-14 09:00:00', '|END_TIME:2025-11-14T11:30:00', 'CONFIRMED', NULL, NULL, '2025-11-13 13:11:40', '2025-11-14 10:47:57', true, false),
(10, 2, 5, '心理咨询', '线上视频', '2025-11-13 20:00:00', '|END_TIME:2025-11-13T21:00:00', 'COMPLETED', '这次咨询非常好！！', NULL, '2025-11-13 19:39:17', '2025-11-14 17:11:30', true, true),
(11, 8, 1, '心理咨询', '线上视频', '2025-11-13 21:00:00', '|END_TIME:2025-11-13T22:00:00', 'COMPLETED', '耶斯耶斯', NULL, '2025-11-13 20:20:13', '2025-11-14 12:54:47', true, true),
(12, 2, 1, '心理咨询', '线上视频', '2025-11-14 16:00:00', '|END_TIME:2025-11-14T17:00:00', 'CONFIRMED', NULL, NULL, '2025-11-13 20:21:10', '2025-11-13 21:40:24', false, false),
(13, 8, 1, '心理咨询', '线上视频', '2025-11-14 17:00:00', '|END_TIME:2025-11-14T19:00:00', 'CONFIRMED', NULL, NULL, '2025-11-13 20:21:57', '2025-11-13 21:40:24', false, false),
(14, 2, 1, '心理咨询', '线上视频', '2025-11-17 10:00:00', '123123123|END_TIME:2025-11-17T12:00:00', 'CONFIRMED', NULL, NULL, '2025-11-13 21:39:46', '2025-11-13 21:40:22', false, false),
(15, 2, 6, '心理咨询', '线上视频', '2025-11-19 17:00:00', '我也喜欢吃年糕|END_TIME:2025-11-19T18:00:00', 'CONFIRMED', NULL, NULL, '2025-11-13 22:06:56', '2025-11-13 22:07:05', false, false),
(16, 2, 5, '心理咨询', '线上视频', '2025-11-14 19:00:00', 'xixixi|END_TIME:2025-11-14T20:00:00', 'CONFIRMED', NULL, NULL, '2025-11-14 17:09:59', '2025-11-14 17:11:14', false, false);

-- comments records
INSERT INTO comments (id, post_id, user_id, content, like_count, is_approved, created_at) VALUES
(1, 3, 2, '( •̀ ω •́ )y我也看到了嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻❤\n.          ?????\n           ?????\n   ᘏ▸◂ᘏ     ???  “ ᕬ ᕬ＂\n( ˶• ᴗ •)    \\?/   ( • ᴗ •˶ )\n⁽⁽ଘ ♡  つ     /?\\   cc   ▸◂   ｜\n しー-Ｊ                  しー-Ｊ', 0, true, '2025-11-13 20:31:14');

-- community_posts records
INSERT INTO community_posts (id, author_id, category, content, tags, like_count, comment_count, is_approved, is_deleted, created_at, report_count) VALUES
(1, 2, '心情树洞', '嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻第一个测试帖(●''◡''●)', '#年糕，#蛋挞', 0, 0, true, false, '2025-11-05 18:01:22', 0),
(2, 2, '心情树洞', 'test111111111balbablablaba', '#年糕，#蛋挞', 2, 0, true, false, '2025-11-05 18:03:33', 0),
(3, 8, '互助问答', '耶我看到lzy发的帖了，测试很成功', '#test', 2, 1, true, false, '2025-11-13 20:30:06', 0),
(4, 2, '经验分享', '.          ?????\n           ?????\n   ᘏ▸◂ᘏ     ???  “ ᕬ ᕬ＂\n( ˶• ᴗ •)    \\?/   ( • ᴗ •˶ )\n⁽⁽ଘ ♡  つ     /?\\   cc   ▸◂   ｜\n しー-Ｊ                  しー-Ｊ', '#送花小兔', 2, 0, true, false, '2025-11-13 20:31:43', 0),
(5, 4, '经验分享', '啦啦啦啦啦啦我是泡泡金鱼！', NULL, 0, 0, true, false, '2025-11-13 21:41:02', 0),
(6, 2, '互助问答', '耶斯，❀嘻嘻嘻', '#炸虾', 1, 0, true, false, '2025-11-14 17:10:56', 0),
(7, 3, '经验分享', '我是一颗米粒嘻嘻嘻我喜欢吃米粒( •̀ ω •́ )y', NULL, 0, 0, true, false, '2025-11-14 17:12:03', 0);

-- consultation_records records
INSERT INTO consultation_records (id, appointment_id, user_id, counselor_id, consult_type, consult_method, appointment_date, description, summary, rating, review, user_confirmed_at, counselor_confirmed_at, created_at, updated_at) VALUES
(1, 3, 2, 1, '心理咨询', '线下面谈', '2025-11-05 18:00:00', NULL, NULL, NULL, NULL, '2025-11-06 14:02:58', '2025-11-06 14:02:58', '2025-11-06 14:02:58', NULL),
(2, 1, 2, 5, '心理咨询', '线上视频', '2025-11-07 15:00:00', NULL, NULL, NULL, NULL, '2025-11-07 16:00:00', '2025-11-11 12:30:03', '2025-11-11 12:30:03', NULL),
(3, 2, 2, 1, '心理咨询', '线下面谈', '2025-11-08 12:00:00', NULL, '耶斯！！完成！！', NULL, NULL, '2025-11-08 13:00:00', '2025-11-12 22:48:53', '2025-11-12 22:48:52', NULL),
(4, 5, 2, 1, '心理咨询', '线上视频', '2025-11-11 17:00:00', NULL, '嘻嘻很好！！❀❀', NULL, NULL, '2025-11-12 22:49:31', '2025-11-11 18:00:00', '2025-11-12 22:49:30', NULL),
(5, 7, 8, 5, '心理咨询', '线上视频', '2025-11-11 18:00:00', NULL, '耶斯很好！！( •̀ ω •́ )y', NULL, NULL, '2025-11-13 20:19:43', '2025-11-11 19:00:00', '2025-11-13 20:19:42', NULL),
(6, 8, 2, 1, '心理咨询', '线上视频', '2025-11-13 14:00:00', '|END_TIME:2025-11-13T16:00:00', '嘻嘻很好', NULL, NULL, '2025-11-13 15:00:00', '2025-11-14 10:47:03', '2025-11-14 10:47:03', NULL),
(7, 11, 8, 1, '心理咨询', '线上视频', '2025-11-13 21:00:00', '|END_TIME:2025-11-13T22:00:00', '耶斯耶斯', NULL, NULL, '2025-11-14 12:54:48', '2025-11-13 22:00:00', '2025-11-14 12:54:47', NULL),
(8, 10, 2, 5, '心理咨询', '线上视频', '2025-11-13 20:00:00', '|END_TIME:2025-11-13T21:00:00', '这次咨询非常好！！', NULL, NULL, '2025-11-13 21:00:00', '2025-11-14 17:11:31', '2025-11-14 17:11:30', NULL);

-- content_likes records
INSERT INTO content_likes (id, user_id, content_type, content_id, created_at) VALUES
(1, 2, 'post', 4, '2025-11-13 20:32:10'),
(2, 2, 'post', 3, '2025-11-13 20:32:12'),
(3, 2, 'post', 2, '2025-11-13 20:32:13'),
(4, 8, 'post', 4, '2025-11-13 20:32:23'),
(5, 8, 'post', 3, '2025-11-13 20:32:24'),
(6, 8, 'post', 2, '2025-11-14 12:55:01'),
(7, 2, 'post', 6, '2025-11-14 17:10:58');

-- counselor_schedules records
INSERT INTO counselor_schedules (id, counselor_id, weekday, start_time, end_time, max_num, is_available) VALUES
(24, 1, 7, '08:00:00', '22:00:00', 3, true),
(23, 1, 6, '08:00:00', '22:00:00', 3, true),
(22, 1, 5, '08:00:00', '22:00:00', 3, true),
(21, 1, 4, '08:00:00', '22:00:00', 3, true),
(20, 1, 3, '08:00:00', '22:00:00', 3, true),
(19, 1, 2, '08:00:00', '22:00:00', 3, true),
(18, 1, 1, '08:00:00', '22:00:00', 3, true);

-- counselor_unavailable records
INSERT INTO counselor_unavailable (id, counselor_id, start_date, end_date, start_time, end_time, reason, status, created_at) VALUES
(1, 5, '2025-11-06', '2025-11-06', NULL, NULL, '个人事务', 1, '2025-11-05 10:21:32'),
(2, 5, '2025-11-06', '2025-11-06', '11:35:00', '16:35:00', '个人事务', 1, '2025-11-05 10:36:05');

-- counselors records
INSERT INTO counselors (id, user_id, real_name, gender, specialty, experience_years, qualification, certificate_url, bio, intro, consult_methods, consult_type, fee, consult_place, max_daily_appointments, avatar, total_consultations, average_rating, review_count, status, created_at, updated_at, age) VALUES
(1, 4, '泡泡金鱼', 'MALE', '["双相情感障碍", "学业压力", "职业发展"]', 2, NULL, NULL, '我是泡泡金鱼！O(∩_∩)O', '嘿嘿1111111111111111111111111111111', '["文字", "线下", "text", "video", "audio", "offline"]', NULL, 0, '南湖心理咨询室', 3, NULL, 5, 0, 0, 'ACTIVE', '2025-11-04 22:04:55', '2025-11-14 12:54:47', 43),
(2, 5, '烤焦面包', 'MALE', '学业压力，情感咨询', 4, NULL, NULL, '有任何生活中的烦恼都可以来找我', NULL, '["文字", "视频"]', NULL, 80, NULL, 3, NULL, 0, 0, 0, 'ACTIVE', '2025-11-04 22:40:56', NULL, 40),
(3, 6, '包袱', 'FEMALE', '情绪调节', 1, NULL, NULL, '情绪不受控制的时候欢迎来咨询我', NULL, '["视频"]', NULL, 50, NULL, 3, NULL, 0, 0, 0, 'ACTIVE', '2025-11-04 22:42:31', NULL, 44),
(4, 7, '梅干', 'MALE', '学业压力，抑郁情绪', 5, NULL, NULL, '(●''◡''●)', NULL, '["文字"]', NULL, 80, NULL, 3, NULL, 0, 0, 0, 'ACTIVE', '2025-11-04 22:44:06', NULL, 38),
(5, 3, '一颗米粒', 'FEMALE', '学业压力, 职业发展', 3, '心理咨询师', NULL, '(*^_^*)(*^_^*)', '我是一颗米粒\n嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻嘻', '["video", "text", "audio", "offline"]', NULL, 0, '南湖', NULL, '/uploads/avatars/5_水母10.ico', 3, NULL, NULL, 'ACTIVE', '2025-11-04 23:37:26', '2025-11-14 17:11:30', 25),
(6, 10, '年糕兔', 'FEMALE', '["情感咨询", "学业压力", "情感困扰", "焦虑抑郁", "家庭关系", "心理创伤"]', 1, NULL, NULL, '我是年糕兔，我爱吃年糕', NULL, '[]', NULL, 0, NULL, 3, NULL, 0, 0, 0, 'ACTIVE', '2025-11-13 21:51:35', '2025-11-13 22:05:05', NULL);

-- post_reports: (no records in dump)

-- private_messages: (no records in dump)

-- system_logs: (no records in dump)

-- test_reports: (no records in dump)

-- test_scales: (no records in dump)

-- user_blocks: (no records in dump)

-- user_favorites: (no records in dump)

-- users records
INSERT INTO users (id, username, phone, email, student_id, password_hash, nickname, gender, age, school, role, is_active, is_anonymous, show_test_results, record_retention, created_at, updated_at, avatar) VALUES
(1, '一只炸虾', '', NULL, NULL, '123456', '一只炸虾', 'OTHER', NULL, NULL, 'ADMIN', true, false, false, '3months', '2025-11-04 20:30:07', '2025-11-04 21:59:13', NULL),
(2, '刘紫湲', '13343538562', '1223756427@qq.com', '1023006395', '123456', '刘紫湲', 'OTHER', NULL, NULL, 'USER', true, false, false, '3months', '2025-11-04 20:47:24', '2025-11-14 20:07:42', NULL),
(8, '殷瑞涵', '11111111111', NULL, NULL, '123456', '殷瑞涵', 'OTHER', NULL, NULL, 'USER', true, false, false, '3months', '2025-11-11 13:59:35', NULL, NULL),
(3, '一颗米粒', NULL, NULL, NULL, '123456', '一颗米粒', 'OTHER', NULL, NULL, 'COUNSELOR', true, false, false, '3months', '2025-11-04 22:02:39', '2025-11-04 23:38:11', NULL),
(4, '泡泡金鱼', NULL, NULL, NULL, '123456', '泡泡金鱼', 'OTHER', NULL, NULL, 'COUNSELOR', true, false, false, '3months', '2025-11-04 22:04:55', '2025-11-04 23:38:11', NULL),
(5, '烤焦面包', NULL, NULL, NULL, '123456', '烤焦面包', 'OTHER', NULL, NULL, 'COUNSELOR', true, false, false, '3months', '2025-11-04 22:40:56', '2025-11-04 23:38:12', NULL),
(6, '包袱', NULL, NULL, NULL, '123456', '包袱', 'OTHER', NULL, NULL, 'COUNSELOR', true, false, false, '3months', '2025-11-04 22:42:31', '2025-11-04 23:38:12', NULL),
(7, '姊呭共', NULL, NULL, NULL, '123456', '姊呭共', 'OTHER', NULL, NULL, 'COUNSELOR', true, false, false, '3months', '2025-11-04 22:44:06', '2025-11-11 21:54:16', NULL),
(9, '沙发兔', NULL, NULL, NULL, '123456', '沙发兔', 'OTHER', NULL, NULL, 'USER', true, false, false, '3months', '2025-11-13 21:49:06', NULL, NULL),
(10, '年糕兔', NULL, NULL, NULL, '123456', '年糕兔', 'OTHER', NULL, NULL, 'COUNSELOR', true, false, false, '3months', '2025-11-13 21:51:35', NULL, NULL);

-- counselor_ratings, contents, other tables had no INSERTs in the provided dump excerpt,
-- but if你有更多 INSERT 片段可以贴上来，我会继续完整转换。

-- ========== set sequences to max(id) ==========
-- 对每个使用 SERIAL 的表把对应 sequence 调到当前 max(id)，以保证后续自增正确。
DO
$$
DECLARE
  r record;
BEGIN
  FOR r IN
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public'
  LOOP
    BEGIN
      EXECUTE format('SELECT setval(pg_get_serial_sequence(%L, %L), COALESCE(MAX(id),0)) FROM %I', r.tablename, 'id', r.tablename);
    EXCEPTION WHEN others THEN
      -- ignore tables without id or sequence
      NULL;
    END;
  END LOOP;
END;
$$;


COMMIT;
