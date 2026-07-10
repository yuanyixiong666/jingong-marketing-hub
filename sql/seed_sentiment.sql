-- 插入舆情数据（AI生成：模拟金宫味业相关舆情）
USE jingong_marketing;

INSERT INTO sentiment_data (keyword, platform, title, content, sentiment, sentiment_score, published_at) VALUES
-- 零添加
('零添加', 'weibo', '零添加酱油真的更健康吗？', '研究表明零添加酱油减少了食品添加剂，但口感可能略有不同', 'positive', 0.6, NOW() - INTERVAL 2 HOUR),
('零添加', 'xiaohongshu', '零添加调味品推荐', '家里一直在用零添加的调味品，感觉味道更纯正', 'positive', 0.8, NOW() - INTERVAL 5 HOUR),
('零添加', 'douyin', '零添加vs普通酱油对比', '实测对比零添加和普通酱油，结果出乎意料', 'neutral', 0.1, NOW() - INTERVAL 8 HOUR),
('零添加', 'weibo', '零添加酱油测评', '这款零添加酱油味道偏淡，不太适合重口味', 'negative', -0.4, NOW() - INTERVAL 12 HOUR),
('零添加', 'xiaohongshu', '调味品选购指南', '选调味品一定要看配料表，零添加是趋势', 'positive', 0.7, NOW() - INTERVAL 1 DAY),
('零添加', 'douyin', '零添加酱油工厂探秘', '参观了金宫味业工厂，零添加生产线很规范', 'positive', 0.9, NOW() - INTERVAL 1 DAY),
('零添加', 'weibo', '零添加是智商税？', '有人认为零添加只是营销噱头，你怎么看', 'neutral', 0.0, NOW() - INTERVAL 2 DAY),
('零添加', 'xiaohongshu', '家庭厨房调味品分享', '分享我家常用的零添加调味品清单', 'positive', 0.5, NOW() - INTERVAL 2 DAY),

-- 有机酱油
('有机酱油', 'weibo', '有机酱油市场报告', '有机酱油市场规模持续增长，消费者健康意识提升', 'positive', 0.7, NOW() - INTERVAL 3 HOUR),
('有机酱油', 'xiaohongshu', '有机酱油推荐', '这款有机酱油口感醇厚，回购第三次了', 'positive', 0.8, NOW() - INTERVAL 6 HOUR),
('有机酱油', 'douyin', '有机酱油价格对比', '有机酱油价格普遍偏高，但品质确实好', 'neutral', 0.2, NOW() - INTERVAL 10 HOUR),
('有机酱油', 'weibo', '有机酱油真的值吗', '花了大价钱买有机酱油，感觉和普通的差不多', 'negative', -0.3, NOW() - INTERVAL 1 DAY),
('有机酱油', 'xiaohongshu', '有机调味品合集', '整理了市面上能买到的有机调味品，建议收藏', 'positive', 0.6, NOW() - INTERVAL 2 DAY),
('有机酱油', 'douyin', '有机酱油酿造过程', '带你看看有机酱油是怎么酿造的', 'positive', 0.5, NOW() - INTERVAL 3 DAY),

-- 调味品推荐
('调味品推荐', 'douyin', '2026调味品排行榜', '年度调味品排行榜出炉，看看你常用的排第几', 'positive', 0.4, NOW() - INTERVAL 1 HOUR),
('调味品推荐', 'xiaohongshu', '厨房必备调味品清单', '新手厨房必看！这些调味品缺一不可', 'positive', 0.6, NOW() - INTERVAL 4 HOUR),
('调味品推荐', 'weibo', '调味品安全事件', '某品牌调味品被检出超标，消费者需注意', 'negative', -0.8, NOW() - INTERVAL 7 HOUR),
('调味品推荐', 'douyin', '川菜调味品搭配', '做川菜必备的调味品搭配，收藏不亏', 'positive', 0.5, NOW() - INTERVAL 1 DAY),
('调味品推荐', 'xiaohongshu', '火锅底料测评', '10款火锅底料横评，这款性价比最高', 'neutral', 0.1, NOW() - INTERVAL 2 DAY),
('调味品推荐', 'weibo', '调味品行业趋势', '2026年调味品行业趋势：健康化、个性化', 'neutral', 0.3, NOW() - INTERVAL 3 DAY),

-- 鸡精怎么选
('鸡精怎么选', 'xiaohongshu', '鸡精选购攻略', '买鸡精看这3点，不踩雷', 'positive', 0.5, NOW() - INTERVAL 2 HOUR),
('鸡精怎么选', 'douyin', '鸡精和味精的区别', '原来鸡精和味精区别这么大，涨知识了', 'neutral', 0.2, NOW() - INTERVAL 9 HOUR),
('鸡精怎么选', 'weibo', '鸡精品牌推荐', '用了这么多年鸡精，还是这个牌子最好', 'positive', 0.7, NOW() - INTERVAL 1 DAY),
('鸡精怎么选', 'xiaohongshu', '鸡精食用安全讨论', '适量使用鸡精是安全的，不必过度担心', 'neutral', 0.1, NOW() - INTERVAL 2 DAY),

-- 火锅底料测评
('火锅底料测评', 'douyin', '10款火锅底料大测评', '花了500块买了10款火锅底料，最推荐这款', 'positive', 0.6, NOW() - INTERVAL 3 HOUR),
('火锅底料测评', 'xiaohongshu', '自制火锅底料教程', '自制火锅底料其实很简单，比买的好吃', 'positive', 0.8, NOW() - INTERVAL 8 HOUR),
('火锅底料测评', 'weibo', '火锅底料食品安全', '某品牌火锅底料检出问题，行业需加强监管', 'negative', -0.7, NOW() - INTERVAL 1 DAY),
('火锅底料测评', 'douyin', '四川人推荐的火锅底料', '作为四川人，这几款火锅底料我从小吃到大', 'positive', 0.9, NOW() - INTERVAL 2 DAY),
('火锅底料测评', 'xiaohongshu', '清汤火锅底料推荐', '不吃辣也能享受火锅，这几款清汤底料超赞', 'positive', 0.4, NOW() - INTERVAL 3 DAY);
