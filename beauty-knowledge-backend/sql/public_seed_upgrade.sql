-- Public-facing beauty seed upgrade
-- Run after init.sql or on an existing beauty_knowledge database.
-- Reference links are documented in ../docs/public-data-sources.md

USE beauty_knowledge;

INSERT IGNORE INTO beauty_ingredient (name, alias_name, category, safety_level, intro, status)
VALUES
    ('壬二酸', NULL, '功效类', 'B', '常用于痘肌、泛红和肤色不均护理', 1),
    ('维生素B5', '泛醇', '修护类', 'A', '帮助舒缓和维持皮肤屏障状态', 1),
    ('视黄醇复配', NULL, '维A类', 'B', '用于平滑肤感和淡化痘印细纹', 1);

INSERT IGNORE INTO beauty_product (name, brand, product_type, skin_type, intro, status)
VALUES
    ('Hydrating Facial Cleanser', 'CeraVe', '洁面', '中性/干性', '主打温和清洁、神经酰胺和透明质酸保湿支持', 1),
    ('PM Facial Moisturizing Lotion', 'CeraVe', '乳液', '中性/混合/油性', '夜间保湿乳液，突出烟酰胺、透明质酸和三重神经酰胺', 1),
    ('Hydrating Hyaluronic Acid Serum', 'CeraVe', '精华', '中性/干性', '补水精华，强调透明质酸、维生素B5与神经酰胺协同', 1),
    ('Resurfacing Retinol Serum', 'CeraVe', '精华', '痘印肌', '聚焦视黄醇、烟酰胺和屏障修护，用于痘印与肤理改善', 1),
    ('Toleriane Double Repair Face Moisturizer', 'La Roche-Posay', '面霜', '敏感肌', '强调神经酰胺、烟酰胺和保湿修护的日常面霜', 1),
    ('Effaclar Salicylic Acid Acne Treatment Serum', 'La Roche-Posay', '精华', '油痘肌', '围绕水杨酸、烟酰胺与温和角质调理的痘肌精华', 1),
    ('Niacinamide 10% + Zinc 1%', 'The Ordinary', '精华', '混合/油性', '以烟酰胺和锌 PCA 为核心，面向油脂和肤色不均管理', 1),
    ('Hyaluronic Acid 2% + B5', 'The Ordinary', '精华', '全肤质', '补水向精华，突出透明质酸和维生素B5', 1);

INSERT IGNORE INTO rel_product_ingredient (product_id, ingredient_id, concentration)
SELECT p.id, i.id, '核心成分'
FROM beauty_product p
JOIN beauty_ingredient i
  ON (p.name = 'Hydrating Facial Cleanser' AND p.brand = 'CeraVe' AND i.name IN ('透明质酸钠', '神经酰胺NP', '神经酰胺AP', '神经酰胺EOP'))
  OR (p.name = 'PM Facial Moisturizing Lotion' AND p.brand = 'CeraVe' AND i.name IN ('烟酰胺', '透明质酸钠', '神经酰胺NP', '神经酰胺AP', '神经酰胺EOP'))
  OR (p.name = 'Hydrating Hyaluronic Acid Serum' AND p.brand = 'CeraVe' AND i.name IN ('透明质酸钠', '维生素B5', '神经酰胺NP'))
  OR (p.name = 'Resurfacing Retinol Serum' AND p.brand = 'CeraVe' AND i.name IN ('烟酰胺', '视黄醇复配', '神经酰胺NP'))
  OR (p.name = 'Toleriane Double Repair Face Moisturizer' AND p.brand = 'La Roche-Posay' AND i.name IN ('烟酰胺', '神经酰胺NP', '透明质酸钠'))
  OR (p.name = 'Effaclar Salicylic Acid Acne Treatment Serum' AND p.brand = 'La Roche-Posay' AND i.name IN ('水杨酸', '烟酰胺'))
  OR (p.name = 'Niacinamide 10% + Zinc 1%' AND p.brand = 'The Ordinary' AND i.name IN ('烟酰胺', '锌 PCA 复合体'))
  OR (p.name = 'Hyaluronic Acid 2% + B5' AND p.brand = 'The Ordinary' AND i.name IN ('透明质酸钠', '维生素B5'));

INSERT IGNORE INTO rel_ingredient_effect (ingredient_id, effect_id, confidence, source)
SELECT i.id, e.id, 0.88, 'public-seed'
FROM beauty_ingredient i
JOIN beauty_effect e
  ON (i.name = '烟酰胺' AND e.name IN ('提亮肤色', '控油平衡', '修护屏障'))
  OR (i.name = '透明质酸钠' AND e.name IN ('补水保湿', '保水锁水'))
  OR (i.name = '维生素B5' AND e.name IN ('舒缓镇静', '修护屏障'))
  OR (i.name = '神经酰胺NP' AND e.name IN ('修护屏障', '补脂修护'))
  OR (i.name = '神经酰胺AP' AND e.name IN ('修护屏障', '补脂修护'))
  OR (i.name = '神经酰胺EOP' AND e.name IN ('修护屏障', '补脂修护'))
  OR (i.name = '水杨酸' AND e.name IN ('祛痘调理', '毛孔管理', '角质调理'))
  OR (i.name = '壬二酸' AND e.name IN ('褪红修护', '均匀肤色', '祛痘调理'))
  OR (i.name = '视黄醇复配' AND e.name IN ('淡化细纹', '淡纹焕肤', '提亮肤色'));
