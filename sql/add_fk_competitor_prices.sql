-- 为 competitor_prices 表添加外键约束
-- 执行前提：确保 competitors 表中已有对应数据
ALTER TABLE competitor_prices
  ADD CONSTRAINT fk_competitor_prices_competitor_id
  FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE;
