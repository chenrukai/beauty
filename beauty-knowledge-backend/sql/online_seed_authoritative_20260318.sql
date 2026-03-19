USE beauty_knowledge;

-- ============================================================
-- 权威来源补充数据（2026-03-18）
-- 目标：
-- 1) 补充可发布知识内容（含来源链接）
-- 2) 补充实体/关系数据（成分-功效）
-- 3) 补充行为日志（用于运营报表图表）
-- ============================================================

-- ---------------------------
-- 分类补充
-- ---------------------------
INSERT INTO kb_category (name, parent_id, sort_order, status)
VALUES ('权威研究与指南', 0, 90, 1)
ON DUPLICATE KEY UPDATE sort_order = VALUES(sort_order), status = VALUES(status);

SET @root_id = (
  SELECT id FROM kb_category WHERE name = '权威研究与指南' AND parent_id = 0 LIMIT 1
);

INSERT INTO kb_category (name, parent_id, sort_order, status)
VALUES
  ('痤疮管理', @root_id, 1, 1),
  ('屏障修护', @root_id, 2, 1),
  ('防晒与光老化', @root_id, 3, 1),
  ('成分安全', @root_id, 4, 1)
ON DUPLICATE KEY UPDATE sort_order = VALUES(sort_order), status = VALUES(status);

SET @cat_acne = (SELECT id FROM kb_category WHERE parent_id = @root_id AND name = '痤疮管理' LIMIT 1);
SET @cat_barrier = (SELECT id FROM kb_category WHERE parent_id = @root_id AND name = '屏障修护' LIMIT 1);
SET @cat_sun = (SELECT id FROM kb_category WHERE parent_id = @root_id AND name = '防晒与光老化' LIMIT 1);
SET @cat_safe = (SELECT id FROM kb_category WHERE parent_id = @root_id AND name = '成分安全' LIMIT 1);

SET @admin_id = (SELECT id FROM sys_user WHERE username = 'admin' LIMIT 1);
SET @admin_id = IFNULL(@admin_id, 1);

-- ---------------------------
-- 权威知识内容
-- ---------------------------
INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜痤疮治疗指南关键点（AAD）',
  'AAD 临床指南强调痤疮治疗应多机制联合，常见外用方案包含过氧化苯甲酰、维A酸类、水杨酸、壬二酸等。',
  '要点梳理：\n1. 外用治疗优先考虑多机制组合，减少单一方案长期效果波动。\n2. 系统抗生素应限制疗程，并与外用方案联用。\n3. 壬二酸、水杨酸、维A酸类、过氧化苯甲酰均在指南推荐范围。\n\n来源：\n- AAD Acne clinical guideline: https://www.aad.org/member/clinical-quality/guidelines/acne',
  @cat_acne, 'TEXT_MD', 1, NOW(), 0, 368, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜痤疮治疗指南关键点（AAD）' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜过氧化苯甲酰安全通报（AAD + FDA）',
  '针对过氧化苯甲酰产品稳定性与苯问题，权威机构建议关注官方抽检和召回信息，避免高温长期存放。',
  '实务建议：\n1. 优先采购来源清晰、批次可追溯的产品。\n2. 做库存管理，避免高温或阳光暴晒环境。\n3. 若监管或品牌发布召回，应立即下架同批次并记录。\n\n来源：\n- AAD statement: https://www.aad.org/news/benzoyl-peroxide-personal-care-products\n- FDA consumer update: https://www.fda.gov/consumers/consumer-updates/tips-stay-safe-sun-sunscreen-sunglasses',
  @cat_safe, 'TEXT_MD', 1, NOW(), 0, 292, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜过氧化苯甲酰安全通报（AAD + FDA）' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜烟酰胺+神经酰胺在痤疮治疗期的修护价值',
  '随机对照研究显示，治疗期配合含烟酰胺和神经酰胺的保湿修护方案，可改善耐受性并支持依从性。',
  '门店应用建议：\n1. 将“治疗成分 + 修护底座”作为标准组合。\n2. 刺激期优先补水修护，降低客户停用概率。\n3. 首次使用建议先小范围试用，再逐步增加频率。\n\n来源：\n- PubMed (RCT): https://pubmed.ncbi.nlm.nih.gov/38299457/',
  @cat_barrier, 'TEXT_MD', 1, NOW(), 0, 334, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜烟酰胺+神经酰胺在痤疮治疗期的修护价值' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜伪神经酰胺修护喷雾对屏障指标的影响',
  '随机对照研究提示，含伪神经酰胺方案可改善经皮水分流失（TEWL）等屏障指标，适合敏弱期修护。',
  '实操建议：\n1. 作为术后或屏障受损期的基础护理步骤。\n2. 与高刺激项目错峰使用，避免同天叠加。\n3. 通过“干燥感、刺痛感、泛红持续时长”评估效果。\n\n来源：\n- PubMed (RCT): https://pubmed.ncbi.nlm.nih.gov/39492723/',
  @cat_barrier, 'TEXT_MD', 1, NOW(), 0, 278, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜伪神经酰胺修护喷雾对屏障指标的影响' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜防晒执行SOP（FDA建议）',
  'FDA 面向消费者建议：选择广谱、按需补涂，并配合衣帽遮挡，不仅是“涂防晒”，而是整套光防护。',
  '门店标准话术：\n1. 广谱防晒是基础，室内外都要考虑。\n2. 出汗、游泳、长时间户外需更频繁补涂。\n3. 防晒和遮挡要同时做，不能互相替代。\n\n来源：\n- FDA consumer update: https://www.fda.gov/consumers/consumer-updates/tips-stay-safe-sun-sunscreen-sunglasses',
  @cat_sun, 'TEXT_MD', 1, NOW(), 0, 419, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜防晒执行SOP（FDA建议）' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜痤疮方案中“联合机制”为什么重要',
  '指南倾向于多机制组合：控油、角质调理、抗炎、抑菌、修护同步推进，避免单点策略反复。',
  '落地模板：\n- 白天：温和清洁 + 修护 + 防晒\n- 夜间：按耐受叠加功能成分\n- 每周：根据刺激反应调整频次\n\n来源：\n- AAD guideline highlights: https://www.aad.org/member/clinical-quality/guidelines/acne',
  @cat_acne, 'TEXT_MD', 1, NOW(), 0, 245, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜痤疮方案中“联合机制”为什么重要' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜敏感肌客户接待的风险提示模板',
  '针对敏感肌，先评估再给方案，尤其强调“低频、低浓度、先修护后进阶”的节奏。',
  '接待流程：\n1. 询问既往不耐受与近期项目史。\n2. 首次方案以修护和耐受建立为主。\n3. 明确告知出现刺痛、红斑加重时的处理与复诊节点。\n\n来源：\n- AAD patient resources & guideline context: https://www.aad.org/member/clinical-quality/guidelines/acne',
  @cat_safe, 'TEXT_MD', 1, NOW(), 0, 198, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜敏感肌客户接待的风险提示模板' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜水杨酸项目沟通要点（结合指南）',
  '水杨酸常用于角质与毛孔管理，但应按肤质和耐受设置频次，避免过度去角质。',
  '沟通重点：\n1. 先讲适用人群，再讲禁忌和反应窗口。\n2. 使用后需加强修护与防晒。\n3. 出现连续刺激反应时，暂停并回归基础修护。\n\n来源：\n- AAD acne guideline highlights: https://www.aad.org/member/clinical-quality/guidelines/acne',
  @cat_acne, 'TEXT_MD', 1, NOW(), 0, 226, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜水杨酸项目沟通要点（结合指南）' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜壬二酸在痤疮与色沉管理中的位置',
  '指南提及壬二酸可作为痤疮管理的一部分，兼顾炎症后色沉的长期维护策略。',
  '门店建议：\n1. 可放在“痘痘 + 色沉”双目标路径中。\n2. 与修护产品并行，减少早期不耐受风险。\n3. 强调持续性，不追求短期过度刺激。\n\n来源：\n- AAD acne guideline highlights: https://www.aad.org/member/clinical-quality/guidelines/acne',
  @cat_acne, 'TEXT_MD', 1, NOW(), 0, 207, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜壬二酸在痤疮与色沉管理中的位置' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜维A类夜间建立耐受的三步法',
  '维A类是常见痤疮与抗老成分，门店应关注起始频率、叠加顺序和刺激管理。',
  '三步法：\n1. 低频起步：每周 2-3 次。\n2. 保湿夹心：先保湿、后功能、再保湿。\n3. 动态加量：稳定 2-4 周后再提高频次。\n\n来源：\n- AAD acne guideline context: https://www.aad.org/member/clinical-quality/guidelines/acne',
  @cat_acne, 'TEXT_MD', 1, NOW(), 0, 256, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜维A类夜间建立耐受的三步法' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜门店防晒复购提升：从“补涂教育”切入',
  '防晒效果依赖正确用量与补涂频率，门店可用标准化提醒提升执行率与复购率。',
  '执行建议：\n1. 首购时同步发放补涂提醒卡。\n2. 针对通勤、户外、运动场景分别给补涂策略。\n3. 复访时记录执行情况，形成个体化建议。\n\n来源：\n- FDA consumer update: https://www.fda.gov/consumers/consumer-updates/tips-stay-safe-sun-sunscreen-sunglasses',
  @cat_sun, 'TEXT_MD', 1, NOW(), 0, 243, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜门店防晒复购提升：从“补涂教育”切入' AND is_deleted = 0);

INSERT INTO kb_knowledge (title, summary, content, category_id, type, status, publish_at, is_deleted, view_count, author_id)
SELECT
  '权威资料｜合规提示：内容仅用于健康教育，不替代医疗诊断',
  '门店知识库需明确边界：用于健康教育与护理建议，不应替代医生诊疗结论。',
  '合规建议：\n1. 对重度炎症、反复感染等高风险场景应建议就医。\n2. 避免承诺性疗效表述，使用“可能/建议/可考虑”等措辞。\n3. 留存咨询记录与异常反馈，便于复盘与质量管理。\n\n来源：\n- AAD guideline context: https://www.aad.org/member/clinical-quality/guidelines/acne\n- FDA consumer education: https://www.fda.gov/consumers/consumer-updates/tips-stay-safe-sun-sunscreen-sunglasses',
  @cat_safe, 'TEXT_MD', 1, NOW(), 0, 191, @admin_id
WHERE NOT EXISTS (SELECT 1 FROM kb_knowledge WHERE title = '权威资料｜合规提示：内容仅用于健康教育，不替代医疗诊断' AND is_deleted = 0);

-- ---------------------------
-- 公告补充
-- ---------------------------
INSERT INTO sys_notice (title, content, is_top, status, publish_time, created_by)
SELECT
  '【数据更新】权威资料已补充',
  '已新增一批基于 AAD / FDA / PubMed 的知识内容，可在“知识列表”筛选“权威研究与指南”查看。',
  1, 1, NOW(), @admin_id
WHERE NOT EXISTS (
  SELECT 1 FROM sys_notice WHERE title = '【数据更新】权威资料已补充'
);

-- ---------------------------
-- 实体与关系补充
-- ---------------------------
INSERT IGNORE INTO beauty_effect (name, scene, intro, status)
VALUES
  ('控油祛痘', '痤疮管理', '用于油脂分泌旺盛及痤疮倾向皮肤管理', 1),
  ('抗炎舒缓', '敏感修护', '用于减轻泛红、刺痛等不适感', 1),
  ('屏障修护', '修护维护', '用于支持皮肤屏障稳定和耐受建立', 1),
  ('提亮均匀', '色沉管理', '用于暗沉与肤色不均护理', 1),
  ('防晒防护', '日间防护', '用于光老化风险管理', 1);

INSERT IGNORE INTO beauty_ingredient (name, alias_name, category, safety_level, intro, status)
VALUES
  ('烟酰胺', NULL, '维生素类', 'A', '常用于提亮、屏障支持与耐受维护', 1),
  ('壬二酸', NULL, '有机酸', 'A', '用于痤疮和色沉相关护理场景', 1),
  ('过氧化苯甲酰', 'BPO', '抗痤疮', 'B', '常见痤疮外用成分，需重视稳定性与刺激管理', 1),
  ('维A醇', 'Retinol', '维A类', 'B', '常用于夜间抗老和痤疮管理', 1),
  ('水杨酸', 'BHA', '酸类', 'B', '用于角质和毛孔管理', 1),
  ('神经酰胺', 'Ceramide', '脂质', 'A', '用于屏障修护', 1),
  ('泛醇', '维生素B5', '维生素类', 'A', '用于舒缓保湿与修护支持', 1),
  ('透明质酸', '玻尿酸', '保湿', 'A', '用于补水保湿', 1);

SET @ing_niacinamide = (SELECT id FROM beauty_ingredient WHERE name = '烟酰胺' LIMIT 1);
SET @ing_azelaic = (SELECT id FROM beauty_ingredient WHERE name = '壬二酸' LIMIT 1);
SET @ing_bpo = (SELECT id FROM beauty_ingredient WHERE name = '过氧化苯甲酰' LIMIT 1);
SET @ing_retinol = (SELECT id FROM beauty_ingredient WHERE name = '维A醇' LIMIT 1);
SET @ing_sa = (SELECT id FROM beauty_ingredient WHERE name = '水杨酸' LIMIT 1);
SET @ing_ceramide = (SELECT id FROM beauty_ingredient WHERE name = '神经酰胺' LIMIT 1);
SET @ing_panthenol = (SELECT id FROM beauty_ingredient WHERE name = '泛醇' LIMIT 1);
SET @ing_ha = (SELECT id FROM beauty_ingredient WHERE name = '透明质酸' LIMIT 1);

SET @eff_acne = (SELECT id FROM beauty_effect WHERE name = '控油祛痘' LIMIT 1);
SET @eff_soothe = (SELECT id FROM beauty_effect WHERE name = '抗炎舒缓' LIMIT 1);
SET @eff_barrier = (SELECT id FROM beauty_effect WHERE name = '屏障修护' LIMIT 1);
SET @eff_bright = (SELECT id FROM beauty_effect WHERE name = '提亮均匀' LIMIT 1);
SET @eff_sun = (SELECT id FROM beauty_effect WHERE name = '防晒防护' LIMIT 1);

INSERT IGNORE INTO rel_ingredient_effect (ingredient_id, effect_id, confidence, source)
VALUES
  (@ing_niacinamide, @eff_barrier, 0.88, 'pubmed:38299457'),
  (@ing_niacinamide, @eff_bright, 0.84, 'aad-guideline'),
  (@ing_azelaic, @eff_acne, 0.86, 'aad-guideline'),
  (@ing_azelaic, @eff_bright, 0.82, 'aad-guideline'),
  (@ing_bpo, @eff_acne, 0.90, 'aad-guideline'),
  (@ing_retinol, @eff_acne, 0.85, 'aad-guideline'),
  (@ing_sa, @eff_acne, 0.84, 'aad-guideline'),
  (@ing_ceramide, @eff_barrier, 0.89, 'pubmed:39492723'),
  (@ing_panthenol, @eff_soothe, 0.80, 'clinical-practice'),
  (@ing_ha, @eff_barrier, 0.78, 'clinical-practice');

-- ---------------------------
-- 行为日志与搜索词统计补充
-- ---------------------------
CREATE TEMPORARY TABLE tmp_seed_knowledge AS
SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
FROM kb_knowledge
WHERE is_deleted = 0 AND status = 1
ORDER BY id DESC
LIMIT 18;

SET @kcnt = (SELECT COUNT(1) FROM tmp_seed_knowledge);
SET @user_id = (SELECT id FROM sys_user WHERE role = 'user' ORDER BY id LIMIT 1);
SET @user_id = IFNULL(@user_id, @admin_id);

WITH RECURSIVE seq AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM seq WHERE n < 120
)
INSERT INTO user_action_log (user_id, action_type, target_type, target_id, keyword, extra, ip, user_agent, created_at)
SELECT
  @user_id AS user_id,
  CASE
    WHEN MOD(n, 4) = 1 THEN 'browse'
    WHEN MOD(n, 4) = 2 THEN 'search'
    WHEN MOD(n, 4) = 3 THEN 'click'
    ELSE 'favorite'
  END AS action_type,
  'knowledge' AS target_type,
  k.id AS target_id,
  CASE
    WHEN MOD(n, 4) = 2 THEN ELT(MOD(n, 6) + 1, '烟酰胺', '壬二酸', '防晒', '维A醇', '水杨酸', '敏感肌')
    ELSE NULL
  END AS keyword,
  CASE
    WHEN MOD(n, 4) = 1 THEN ELT(MOD(n, 3) + 1, 'recommend', 'search', 'favorite')
    WHEN MOD(n, 4) = 2 THEN 'search'
    WHEN MOD(n, 4) = 3 THEN ELT(MOD(n, 2) + 1, 'recommend', 'favorite')
    ELSE 'favorite'
  END AS extra,
  '127.0.0.1',
  'seed-script/20260318',
  DATE_SUB(NOW(), INTERVAL MOD(n, 7) DAY) - INTERVAL MOD(n * 3, 23) HOUR
FROM seq
JOIN tmp_seed_knowledge k ON k.rn = MOD(n - 1, @kcnt) + 1;

DROP TEMPORARY TABLE IF EXISTS tmp_seed_knowledge;

INSERT INTO search_keyword_stat (stat_date, keyword, search_count, user_count)
VALUES
  (CURDATE(), '烟酰胺', 23, 1),
  (CURDATE(), '壬二酸', 17, 1),
  (CURDATE(), '防晒', 19, 1),
  (CURDATE(), '维A醇', 14, 1),
  (CURDATE(), '水杨酸', 16, 1),
  (CURDATE(), '敏感肌', 21, 1),
  (DATE_SUB(CURDATE(), INTERVAL 1 DAY), '烟酰胺', 18, 1),
  (DATE_SUB(CURDATE(), INTERVAL 1 DAY), '防晒', 15, 1),
  (DATE_SUB(CURDATE(), INTERVAL 2 DAY), '壬二酸', 13, 1),
  (DATE_SUB(CURDATE(), INTERVAL 2 DAY), '维A醇', 12, 1)
ON DUPLICATE KEY UPDATE
  search_count = VALUES(search_count),
  user_count = VALUES(user_count);

-- 执行完成提示
SELECT
  (SELECT COUNT(1) FROM kb_knowledge WHERE title LIKE '权威资料｜%' AND is_deleted = 0) AS seeded_knowledge_count,
  (SELECT COUNT(1) FROM beauty_ingredient WHERE name IN ('烟酰胺','壬二酸','过氧化苯甲酰','维A醇','水杨酸','神经酰胺','泛醇','透明质酸')) AS seeded_ingredient_count,
  (SELECT COUNT(1) FROM user_action_log WHERE user_agent = 'seed-script/20260318') AS seeded_action_count;
