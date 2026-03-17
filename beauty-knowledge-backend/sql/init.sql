-- ============================================================
-- AI美业知识官 · 初始化脚本（14张表 + 大体量真实样本数据）
-- MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS beauty_knowledge
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE beauty_knowledge;

-- ------------------------------------------------------------
-- 清理旧表（按依赖逆序）
-- ------------------------------------------------------------
-- DROP TABLE statements removed intentionally to avoid destructive initialization.

-- ============================================================
-- 1) 用户表
-- ============================================================
CREATE TABLE sys_user
(
    id         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    username   VARCHAR(50)  NOT NULL COMMENT '用户名',
    password   VARCHAR(100) NOT NULL COMMENT 'BCrypt密码',
    nickname   VARCHAR(50)           DEFAULT NULL COMMENT '昵称',
    phone      VARCHAR(20)           DEFAULT NULL COMMENT '手机号',
    role       VARCHAR(20)  NOT NULL DEFAULT 'user' COMMENT 'admin/user',
    status     TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0禁用',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    KEY idx_role (role),
    KEY idx_status (status)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='系统用户表';

-- ============================================================
-- 2) 分类表
-- ============================================================
CREATE TABLE kb_category
(
    id          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    name        VARCHAR(64) NOT NULL COMMENT '分类名',
    parent_id   BIGINT      NOT NULL DEFAULT 0 COMMENT '父级分类ID，0为根',
    sort_order  INT         NOT NULL DEFAULT 0 COMMENT '排序',
    status      TINYINT     NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_parent (parent_id),
    KEY idx_status (status),
    UNIQUE KEY uk_parent_name (parent_id, name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='知识分类表';

-- ============================================================
-- 3) 知识内容表
-- ============================================================
CREATE TABLE kb_knowledge
(
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '知识ID',
    title       VARCHAR(255) NOT NULL COMMENT '标题',
    summary     VARCHAR(500)          DEFAULT NULL COMMENT '摘要',
    content     LONGTEXT     NOT NULL COMMENT '正文',
    category_id BIGINT       NOT NULL COMMENT '分类ID',
    type        VARCHAR(32)  NOT NULL DEFAULT 'TEXT' COMMENT 'TEXT/PDF/IMAGE',
    cover_url   VARCHAR(255)          DEFAULT NULL COMMENT '封面地址',
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1发布 0草稿',
    view_count  INT          NOT NULL DEFAULT 0 COMMENT '阅读量',
    author_id   BIGINT       NOT NULL COMMENT '作者ID',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_category_status (category_id, status),
    KEY idx_author (author_id),
    FULLTEXT KEY ft_title_content (title, content) WITH PARSER ngram
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='知识内容表';

-- ============================================================
-- 4) 文件表
-- ============================================================
CREATE TABLE kb_file
(
    id             BIGINT       NOT NULL AUTO_INCREMENT COMMENT '文件ID',
    knowledge_id   BIGINT       NOT NULL COMMENT '知识ID',
    original_name  VARCHAR(255) NOT NULL COMMENT '原文件名',
    file_type      VARCHAR(20)  NOT NULL COMMENT 'pdf/image',
    file_size      BIGINT       NOT NULL COMMENT '字节大小',
    minio_path     VARCHAR(255) NOT NULL COMMENT 'MinIO路径',
    file_hash      CHAR(64)     NOT NULL COMMENT 'SHA-256',
    version        INT          NOT NULL DEFAULT 1 COMMENT '版本号',
    process_status VARCHAR(20)  NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/PROCESSING/SUCCESS/FAILED',
    uploaded_by    BIGINT       NOT NULL COMMENT '上传人',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_file_hash (file_hash),
    KEY idx_knowledge (knowledge_id),
    KEY idx_process_status (process_status)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='知识文件表';

-- ============================================================
-- 5) 分块表
-- ============================================================
CREATE TABLE kb_chunk
(
    id            BIGINT    NOT NULL AUTO_INCREMENT COMMENT '分块ID',
    knowledge_id  BIGINT    NOT NULL COMMENT '知识ID',
    file_id       BIGINT    NOT NULL COMMENT '文件ID',
    chunk_index   INT       NOT NULL COMMENT '块序号',
    page_no       INT       NOT NULL DEFAULT 1 COMMENT '页码',
    content       TEXT      NOT NULL COMMENT '分块文本',
    char_count    INT       NOT NULL DEFAULT 0 COMMENT '字符数',
    vector_status TINYINT   NOT NULL DEFAULT 1 COMMENT '1已向量化 0未向量化',
    created_at    DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file_chunk (file_id, chunk_index),
    KEY idx_knowledge (knowledge_id),
    FULLTEXT KEY ft_chunk_content (content) WITH PARSER ngram
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='文本分块表';

-- ============================================================
-- 6) 处理任务表
-- ============================================================
CREATE TABLE process_task
(
    id          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    file_id     BIGINT      NOT NULL COMMENT '文件ID',
    task_type   VARCHAR(32) NOT NULL DEFAULT 'KNOWLEDGE_PROCESS' COMMENT '任务类型',
    status      VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/PROCESSING/SUCCESS/FAILED',
    progress    INT         NOT NULL DEFAULT 0 COMMENT '进度0~100',
    result_msg  VARCHAR(500)         DEFAULT NULL COMMENT '结果信息',
    retry_count INT         NOT NULL DEFAULT 0 COMMENT '已重试次数',
    max_retry   INT         NOT NULL DEFAULT 3 COMMENT '最大重试次数',
    started_at  DATETIME             DEFAULT NULL COMMENT '开始时间',
    finished_at DATETIME             DEFAULT NULL COMMENT '结束时间',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file (file_id),
    KEY idx_status (status)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='异步处理任务表';

-- ============================================================
-- 7) 会话表
-- ============================================================
CREATE TABLE chat_session
(
    id         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '会话ID',
    user_id    BIGINT       NOT NULL COMMENT '用户ID',
    title      VARCHAR(200) NOT NULL COMMENT '会话标题',
    status     TINYINT      NOT NULL DEFAULT 1 COMMENT '1有效 0删除',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_user_updated (user_id, updated_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='聊天会话表';

-- ============================================================
-- 8) 消息表
-- ============================================================
CREATE TABLE chat_message
(
    id          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    session_id  BIGINT      NOT NULL COMMENT '会话ID',
    role        VARCHAR(20) NOT NULL COMMENT 'user/assistant',
    content     LONGTEXT    NOT NULL COMMENT '消息内容',
    token_count INT         NOT NULL DEFAULT 0 COMMENT 'token计数',
    sources     JSON                 DEFAULT NULL COMMENT '引用来源',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_session_created (session_id, created_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='聊天消息表';

-- ============================================================
-- 9) 成分表
-- ============================================================
CREATE TABLE beauty_ingredient
(
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '成分ID',
    name        VARCHAR(100) NOT NULL COMMENT '成分名称',
    alias_name  VARCHAR(100)          DEFAULT NULL COMMENT '别名',
    category    VARCHAR(50)           DEFAULT NULL COMMENT '成分类别',
    safety_level VARCHAR(20)          DEFAULT NULL COMMENT '安全等级',
    intro       VARCHAR(500)          DEFAULT NULL COMMENT '简介',
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1有效 0无效',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_ingredient_name (name),
    KEY idx_status (status)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='美业成分表';

-- ============================================================
-- 10) 功效表
-- ============================================================
CREATE TABLE beauty_effect
(
    id         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '功效ID',
    name       VARCHAR(100) NOT NULL COMMENT '功效名称',
    scene      VARCHAR(100)          DEFAULT NULL COMMENT '适用场景',
    intro      VARCHAR(500)          DEFAULT NULL COMMENT '简介',
    status     TINYINT      NOT NULL DEFAULT 1 COMMENT '1有效 0无效',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_effect_name (name),
    KEY idx_status (status)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='美业功效表';

-- ============================================================
-- 11) 产品表
-- ============================================================
CREATE TABLE beauty_product
(
    id           BIGINT       NOT NULL AUTO_INCREMENT COMMENT '产品ID',
    name         VARCHAR(150) NOT NULL COMMENT '产品名称',
    brand        VARCHAR(100)          DEFAULT NULL COMMENT '品牌',
    product_type VARCHAR(50)           DEFAULT NULL COMMENT '产品类型',
    skin_type    VARCHAR(50)           DEFAULT NULL COMMENT '适用肤质',
    intro        VARCHAR(500)          DEFAULT NULL COMMENT '简介',
    status       TINYINT      NOT NULL DEFAULT 1 COMMENT '1有效 0无效',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_product_name_brand (name, brand),
    KEY idx_status (status)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='美业产品表';

-- ============================================================
-- 12) 成分-功效关系表
-- ============================================================
CREATE TABLE rel_ingredient_effect
(
    id            BIGINT      NOT NULL AUTO_INCREMENT COMMENT '关系ID',
    ingredient_id BIGINT      NOT NULL COMMENT '成分ID',
    effect_id     BIGINT      NOT NULL COMMENT '功效ID',
    confidence    DECIMAL(5,2)         DEFAULT 0.80 COMMENT '置信度',
    source        VARCHAR(100)         DEFAULT 'dictionary' COMMENT '来源',
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_ing_effect (ingredient_id, effect_id),
    KEY idx_effect (effect_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='成分功效关系表';

-- ============================================================
-- 13) 产品-成分关系表
-- ============================================================
CREATE TABLE rel_product_ingredient
(
    id            BIGINT      NOT NULL AUTO_INCREMENT COMMENT '关系ID',
    product_id    BIGINT      NOT NULL COMMENT '产品ID',
    ingredient_id BIGINT      NOT NULL COMMENT '成分ID',
    concentration VARCHAR(50)          DEFAULT NULL COMMENT '浓度区间',
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_product_ing (product_id, ingredient_id),
    KEY idx_ingredient (ingredient_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='产品成分关系表';

-- ============================================================
-- 14) 实体抽取待确认表
-- ============================================================
CREATE TABLE entity_extract_pending
(
    id            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '待确认ID',
    file_id       BIGINT       NOT NULL COMMENT '来源文件ID',
    entity_type   VARCHAR(20)  NOT NULL COMMENT 'ingredient/effect/product',
    entity_name   VARCHAR(120) NOT NULL COMMENT '实体名',
    source_text   VARCHAR(500)          DEFAULT NULL COMMENT '来源文本',
    extract_method VARCHAR(20) NOT NULL DEFAULT 'dictionary' COMMENT 'dictionary/llm',
    status        VARCHAR(20)  NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/CONFIRMED/REJECTED',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file_status (file_id, status),
    KEY idx_entity_type (entity_type)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='实体抽取待确认表';

-- ============================================================
-- 初始化数据（真实风格 + 大体量）
-- ============================================================

INSERT INTO sys_user (id, username, password, nickname, phone, role, status)
VALUES (1, 'admin', '$2a$10$Xkzvqpccpw58aTSzFTliC./y3PIBlw31cd0EHgQl7lC4.g6A36cq2', '系统管理员', '13800000001', 'admin', 1),
       (2, 'user', '$2a$10$yxVRdh03A9RJt0hCXgmHceViy26jD1YObkOQ5Dkurxof9CbfkebqK', '普通用户', '13800000002', 'user', 1),
       (3, 'trainer01', '$2a$10$Xkzvqpccpw58aTSzFTliC./y3PIBlw31cd0EHgQl7lC4.g6A36cq2', '培训讲师A', '13800000003', 'admin', 1),
       (4, 'staff01', '$2a$10$yxVRdh03A9RJt0hCXgmHceViy26jD1YObkOQ5Dkurxof9CbfkebqK', '美容师小林', '13800000004', 'user', 1),
       (5, 'staff02', '$2a$10$yxVRdh03A9RJt0hCXgmHceViy26jD1YObkOQ5Dkurxof9CbfkebqK', '美容师小周', '13800000005', 'user', 1);

INSERT INTO kb_category (id, name, parent_id, sort_order, status)
VALUES (1, '护肤理论', 0, 1, 1),
       (2, '产品资料', 0, 2, 1),
       (3, '门店流程', 0, 3, 1),
       (4, '问题处理', 0, 4, 1),
       (11, '皮肤结构基础', 1, 1, 1),
       (12, '屏障与修护', 1, 2, 1),
       (13, '敏感肌管理', 1, 3, 1),
       (21, '洁面与卸妆', 2, 1, 1),
       (22, '精华与功效', 2, 2, 1),
       (23, '面膜与护理', 2, 3, 1),
       (31, '接待标准话术', 3, 1, 1),
       (32, '项目操作SOP', 3, 2, 1),
       (33, '售后回访', 3, 3, 1),
       (41, '不良反应处理', 4, 1, 1),
       (42, '客诉应对', 4, 2, 1),
       (43, '禁忌与风险提示', 4, 3, 1);

INSERT INTO beauty_effect (name, scene, intro)
VALUES ('补水保湿', '日常护理', '提升角质层含水量，缓解干燥紧绷'),
       ('修护屏障', '敏感修护', '改善泛红刺痛，增强皮肤屏障'),
       ('控油平衡', '油皮护理', '减少多余油脂分泌，改善油光'),
       ('舒缓镇静', '敏感护理', '减轻刺激感与不适'),
       ('提亮肤色', '暗沉改善', '改善肤色不均和暗沉'),
       ('淡化色沉', '色沉管理', '降低炎症后色沉显现'),
       ('抗氧化', '初老护理', '减少自由基损伤'),
       ('抗老紧致', '熟龄护理', '提升皮肤弹性与紧实度'),
       ('淡化细纹', '初老护理', '改善干纹细纹外观'),
       ('毛孔管理', '粗糙改善', '视觉收敛毛孔并优化肤理'),
       ('角质调理', '代谢管理', '促进老废角质代谢'),
       ('祛痘调理', '痘肌护理', '减少粉刺痘痘发生'),
       ('抑菌净肤', '痘肌护理', '减少致痘环境'),
       ('褪红修护', '敏感泛红', '缓解红感和热感'),
       ('保水锁水', '秋冬干燥', '增强保湿持久度'),
       ('淡纹焕肤', '焕肤护理', '改善粗糙与细纹'),
       ('亮泽通透', '肤质优化', '提升肌肤光泽度'),
       ('舒缓清洁', '清洁护理', '温和清洁并减少刺激'),
       ('头皮舒缓', '头皮护理', '缓解头皮紧绷瘙痒'),
       ('头皮控油', '头皮护理', '减少头皮油脂负担'),
       ('发丝修护', '发质护理', '改善毛躁分叉'),
       ('烫后修护', '烫染护理', '修复烫染后受损结构'),
       ('晒后修护', '夏季护理', '缓解晒后不适'),
       ('均匀肤色', '提亮护理', '改善局部暗沉'),
       ('温和去角质', '代谢管理', '平衡代谢不伤屏障'),
       ('补脂修护', '干敏护理', '补充皮脂膜所需脂质'),
       ('水油平衡', '混合肤质', '平衡T区与U区状态'),
       ('抗糖化', '熟龄护理', '降低糖化导致的暗黄'),
       ('即时舒缓', '急救护理', '快速缓解突发刺激'),
       ('术后维护', '专业护理', '配合术后恢复周期');

INSERT INTO beauty_ingredient (name, alias_name, category, safety_level, intro)
VALUES ('烟酰胺', NULL, '维生素类', 'A', '帮助提亮与屏障修护'),
       ('透明质酸钠', '玻尿酸', '保湿类', 'A', '高效保湿成分'),
       ('泛醇', '维生素B5', '修护类', 'A', '舒缓并修护屏障'),
       ('积雪草提取物', NULL, '植物提取', 'A', '舒缓修护'),
       ('神经酰胺NP', NULL, '脂质类', 'A', '强化屏障脂质结构'),
       ('角鲨烷', NULL, '油脂类', 'A', '柔润保湿'),
       ('甘油', NULL, '保湿类', 'A', '经典吸湿保湿'),
       ('尿囊素', NULL, '舒缓类', 'A', '舒缓不适'),
       ('马齿苋提取物', NULL, '植物提取', 'A', '舒缓泛红'),
       ('β-葡聚糖', NULL, '修护类', 'A', '舒缓和修护'),
       ('水杨酸', 'BHA', '酸类', 'B', '角质调理与毛孔管理'),
       ('乳酸', 'AHA', '酸类', 'B', '焕肤与保湿'),
       ('杏仁酸', NULL, '酸类', 'B', '温和焕肤'),
       ('果酸复合物', NULL, '酸类', 'B', '促进代谢'),
       ('壬二酸衍生物', NULL, '功效类', 'B', '痘肌调理'),
       ('茶树精油', NULL, '精油类', 'B', '净肤调理'),
       ('PCA锌', NULL, '矿物盐', 'A', '控油平衡'),
       ('羟基乙酸', '甘醇酸', '酸类', 'B', '加速角质代谢'),
       ('抗坏血酸葡糖苷', 'AA2G', '维C衍生物', 'A', '提亮抗氧化'),
       ('3-O-乙基抗坏血酸', '乙基VC', '维C衍生物', 'A', '稳定提亮'),
       ('传明酸', NULL, '功效类', 'A', '色沉管理'),
       ('熊果苷', 'α-熊果苷', '功效类', 'A', '均匀肤色'),
       ('377', '苯乙基间苯二酚', '功效类', 'B', '提亮肤色'),
       ('辅酶Q10', NULL, '抗氧化', 'A', '抗氧化支持'),
       ('白藜芦醇', NULL, '抗氧化', 'A', '抵御氧化压力'),
       ('艾地苯', NULL, '抗氧化', 'B', '高效抗氧化'),
       ('视黄醇', 'A醇', '维A类', 'B', '抗老淡纹'),
       ('视黄醛', NULL, '维A类', 'B', '抗老焕肤'),
       ('胜肽复合物', NULL, '胜肽类', 'A', '促进紧致'),
       ('棕榈酰三肽-1', NULL, '胜肽类', 'A', '抗老支持'),
       ('乙酰基六肽-8', NULL, '胜肽类', 'A', '细纹管理'),
       ('海藻糖', NULL, '保湿类', 'A', '保湿抗干燥'),
       ('霍霍巴籽油', NULL, '油脂类', 'A', '柔润保护'),
       ('乳木果脂', NULL, '油脂类', 'A', '补脂修护'),
       ('胆固醇', NULL, '脂质类', 'A', '修护皮脂膜'),
       ('磷脂', NULL, '脂质类', 'A', '屏障支持'),
       ('甘草酸二钾', NULL, '舒缓类', 'A', '缓解刺激'),
       ('红没药醇', NULL, '舒缓类', 'A', '舒缓泛红'),
       ('尿素', NULL, '保湿类', 'B', '角质层保湿'),
       ('燕麦β葡聚糖', NULL, '修护类', 'A', '舒缓屏障'),
       ('金盏花提取物', NULL, '植物提取', 'A', '舒缓敏感'),
       ('绿茶提取物', NULL, '植物提取', 'A', '抗氧化净肤'),
       ('迷迭香提取物', NULL, '植物提取', 'A', '抗氧化支持'),
       ('光果甘草根提取物', NULL, '植物提取', 'A', '提亮肤色'),
       ('桑白皮提取物', NULL, '植物提取', 'A', '色沉管理'),
       ('川谷籽提取物', NULL, '植物提取', 'A', '舒缓保湿'),
       ('二裂酵母发酵产物溶胞物', NULL, '发酵类', 'A', '修护抗氧化'),
       ('半乳糖酵母样菌发酵滤液', NULL, '发酵类', 'A', '润泽提亮'),
       ('乳酸杆菌发酵产物', NULL, '发酵类', 'A', '维稳修护'),
       ('烟酰胺复合体', NULL, '复配类', 'A', '提亮+修护'),
       ('透明质酸交联聚合物', NULL, '保湿类', 'A', '长效保湿'),
       ('聚谷氨酸', NULL, '保湿类', 'A', '锁水膜感'),
       ('依克多因', NULL, '修护类', 'A', '抗刺激保护'),
       ('麦角硫因', NULL, '抗氧化', 'A', '抗氧化防护'),
       ('肌肽', NULL, '抗糖化', 'A', '抗糖化支持'),
       ('咖啡因', NULL, '功效类', 'A', '循环支持'),
       ('腺苷', NULL, '功效类', 'A', '抗皱支持'),
       ('海茴香干细胞提取物', NULL, '植物提取', 'A', '抗老修护'),
       ('木糖醇葡糖苷', NULL, '保湿类', 'A', '保湿通路支持'),
       ('脱水木糖醇', NULL, '保湿类', 'A', '补水保湿'),
       ('木糖醇', NULL, '保湿类', 'A', '增润保湿'),
       ('PDRN', NULL, '修护类', 'B', '修护支持'),
       ('胶原蛋白肽', NULL, '蛋白类', 'A', '紧致弹润'),
       ('弹性蛋白', NULL, '蛋白类', 'A', '弹性支持'),
       ('神经酰胺AP', NULL, '脂质类', 'A', '屏障修护'),
       ('神经酰胺EOP', NULL, '脂质类', 'A', '屏障修护'),
       ('辛酰水杨酸', 'LHA', '酸类', 'B', '温和角质调理'),
       ('葡糖酸内酯', 'PHA', '酸类', 'A', '温和焕肤'),
       ('乳糖酸', NULL, '酸类', 'A', '温和焕肤'),
       ('壳聚糖', NULL, '成膜类', 'A', '成膜修护'),
       ('海盐矿物复合物', NULL, '矿物类', 'A', '平衡调理'),
       ('锌 PCA 复合体', NULL, '复配类', 'A', '控油净肤'),
       ('维生素E', '生育酚', '维生素类', 'A', '抗氧化'),
       ('维生素F', NULL, '脂肪酸类', 'A', '补脂修护'),
       ('葡萄籽提取物', NULL, '植物提取', 'A', '抗氧化'),
       ('蓝铜胜肽', NULL, '胜肽类', 'A', '修护紧致'),
       ('寡肽-1', 'EGF', '胜肽类', 'B', '修护支持'),
       ('寡肽-5', NULL, '胜肽类', 'A', '弹润支持'),
       ('蛇毒肽', NULL, '胜肽类', 'B', '表情纹管理'),
       ('棕榈酰五肽-4', NULL, '胜肽类', 'A', '细纹管理'),
       ('海藻糖复配物', NULL, '复配类', 'A', '锁水舒缓');

WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 120
)
INSERT INTO beauty_product (name, brand, product_type, skin_type, intro)
SELECT CONCAT('专业护理产品-', LPAD(n, 3, '0')) AS name,
       ELT((n % 6) + 1, '澜肌实验室', '羽萃美研', '诺颜医研', '清苒皮肤学', '悦见美学', '臻研皮肤中心') AS brand,
       ELT((n % 8) + 1, '洁面', '爽肤水', '精华', '乳液', '面霜', '面膜', '头皮护理', '修护霜') AS product_type,
       ELT((n % 5) + 1, '干性', '油性', '混合', '敏感', '中性') AS skin_type,
       CONCAT('用于门店项目标准化护理，批次', DATE_FORMAT(NOW(), '%Y%m'), '，样本编号', LPAD(n, 3, '0')) AS intro
FROM seq;

WITH RECURSIVE seq_rel AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_rel WHERE n < 120
)
INSERT IGNORE INTO rel_ingredient_effect (ingredient_id, effect_id, confidence, source)
SELECT ((n - 1) % 80) + 1 AS ingredient_id,
       ((n - 1) % 30) + 1 AS effect_id,
       ROUND(0.72 + (n % 20) * 0.01, 2) AS confidence,
       ELT((n % 2) + 1, 'dictionary', 'llm') AS source
FROM seq_rel;

WITH RECURSIVE seq_pi AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_pi WHERE n < 360
)
INSERT IGNORE INTO rel_product_ingredient (product_id, ingredient_id, concentration)
SELECT ((n - 1) % 120) + 1 AS product_id,
       ((n * 3 - 1) % 80) + 1 AS ingredient_id,
       ELT((n % 5) + 1, '0.1%-0.3%', '0.3%-1%', '1%-3%', '3%-5%', '5%-10%') AS concentration
FROM seq_pi;

WITH RECURSIVE seq_k AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_k WHERE n < 300
)
INSERT INTO kb_knowledge (title, summary, content, category_id, type, cover_url, status, view_count, author_id)
SELECT CONCAT(
               ELT((n % 5) + 1, '门店实操', '产品知识', '成分科普', '客诉处理', '项目SOP'),
               ' · ',
               ELT((n % 7) + 1, '敏感肌', '油痘肌', '屏障修护', '术后维护', '提亮焕肤', '头皮护理', '季节护理'),
               ' 第', n, '讲'
           ) AS title,
       CONCAT('用于门店培训与新人上手，编号', n) AS summary,
       CONCAT(
               '本节重点：先评估肤质与近期状态，再匹配项目与产品。',
               '操作中遵循低刺激、可追溯、分层护理原则。',
               '当出现泛红、刺痛、爆痘等信号时，优先执行舒缓与减量策略。',
               '推荐话术：先解释原理，再给可执行方案与复访时间。',
               '培训编号：', n, '。'
           ) AS content,
       ELT((n % 12) + 1, 11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43) AS category_id,
       ELT((n % 3) + 1, 'TEXT', 'PDF', 'IMAGE') AS type,
       CONCAT('https://cdn.example.com/cover/', n, '.jpg') AS cover_url,
       1 AS status,
       (n * 17) % 2000 AS view_count,
       ELT((n % 3) + 1, 1, 3, 4) AS author_id
FROM seq_k;

INSERT INTO kb_file (knowledge_id, original_name, file_type, file_size, minio_path, file_hash, version, process_status, uploaded_by)
SELECT k.id,
       CONCAT('knowledge_', k.id, '.', IF(k.type = 'IMAGE', 'png', 'pdf')) AS original_name,
       IF(k.type = 'IMAGE', 'image', 'pdf') AS file_type,
       120000 + k.id * 321 AS file_size,
       CONCAT(IF(k.type = 'IMAGE', 'image', 'pdf'), '/2026/03/', LPAD((k.id % 28) + 1, 2, '0'), '/', k.id, '.', IF(k.type = 'IMAGE', 'png', 'pdf')) AS minio_path,
       SHA2(CONCAT('file-', k.id, '-seed-20260316'), 256) AS file_hash,
       1 AS version,
       'SUCCESS' AS process_status,
       ELT((k.id % 3) + 1, 1, 3, 4) AS uploaded_by
FROM kb_knowledge k;

INSERT INTO process_task (file_id, task_type, status, progress, result_msg, retry_count, max_retry, started_at, finished_at)
SELECT f.id,
       'KNOWLEDGE_PROCESS' AS task_type,
       'SUCCESS' AS status,
       100 AS progress,
       '处理成功' AS result_msg,
       0 AS retry_count,
       3 AS max_retry,
       DATE_SUB(NOW(), INTERVAL (f.id % 30) DAY) AS started_at,
       DATE_SUB(NOW(), INTERVAL (f.id % 30) DAY) + INTERVAL 5 MINUTE AS finished_at
FROM kb_file f;

WITH RECURSIVE seq_c AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_c WHERE n < 6
)
INSERT INTO kb_chunk (knowledge_id, file_id, chunk_index, page_no, content, char_count, vector_status)
SELECT f.knowledge_id,
       f.id AS file_id,
       seq_c.n AS chunk_index,
       seq_c.n AS page_no,
       CONCAT('知识ID', f.knowledge_id, ' 文件ID', f.id, ' 的第', seq_c.n, '分块。',
              '内容包含皮肤评估、成分选择、操作步骤、风险提示和回访建议。',
              '该分块用于BM25检索与向量召回融合。') AS content,
       120 + seq_c.n * 5 AS char_count,
       1 AS vector_status
FROM kb_file f
         CROSS JOIN seq_c;

WITH RECURSIVE seq_s AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_s WHERE n < 80
)
INSERT INTO chat_session (user_id, title, status, created_at, updated_at)
SELECT ELT((n % 3) + 1, 2, 4, 5) AS user_id,
       CONCAT('问答会话-', LPAD(n, 3, '0')) AS title,
       1 AS status,
       DATE_SUB(NOW(), INTERVAL n DAY) AS created_at,
       DATE_SUB(NOW(), INTERVAL n DAY) + INTERVAL 30 MINUTE AS updated_at
FROM seq_s;

WITH RECURSIVE seq_m AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_m WHERE n < 5
)
INSERT INTO chat_message (session_id, role, content, token_count, sources, created_at)
SELECT s.id,
       IF(seq_m.n % 2 = 1, 'user', 'assistant') AS role,
       IF(seq_m.n % 2 = 1,
          CONCAT('用户提问：我的皮肤最近泛红，应该先用什么项目？（会话', s.id, '）'),
          CONCAT('建议先做舒缓修护流程，减少酸类频次，优先补水+修护屏障。（会话', s.id, '）')) AS content,
       60 + seq_m.n * 15 AS token_count,
       IF(seq_m.n % 2 = 0,
          JSON_ARRAY(JSON_OBJECT('file', CONCAT('knowledge_', (s.id % 300) + 1, '.pdf'),
                                 'page', 2,
                                 'chunk', '先稳后进，优先舒缓修护')),
          NULL) AS sources,
       DATE_SUB(NOW(), INTERVAL s.id DAY) + INTERVAL seq_m.n MINUTE AS created_at
FROM chat_session s
         CROSS JOIN seq_m;

WITH RECURSIVE seq_p AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_p WHERE n < 240
)
INSERT INTO entity_extract_pending (file_id, entity_type, entity_name, source_text, extract_method, status)
SELECT ((n - 1) % 300) + 1 AS file_id,
       ELT((n % 3) + 1, 'ingredient', 'effect', 'product') AS entity_type,
       CONCAT(ELT((n % 3) + 1, '候选成分-', '候选功效-', '候选产品-'), LPAD(n, 4, '0')) AS entity_name,
       CONCAT('来源文本片段：第', (n % 6) + 1, '块识别到关键词组合。') AS source_text,
       ELT((n % 2) + 1, 'dictionary', 'llm') AS extract_method,
       ELT((n % 10) + 1, 'PENDING', 'PENDING', 'PENDING', 'PENDING', 'PENDING', 'CONFIRMED', 'PENDING', 'PENDING', 'REJECTED', 'PENDING') AS status
FROM seq_p;

SELECT COUNT(*)
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'beauty_knowledge';
