"""
爬虫启动入口
AI生成：调度各平台爬虫并写入数据
"""
import sys
import os
import asyncio

# 将项目根目录加入 Python 路径，解决 PyCharm 运行时找不到 crawler 模块的问题
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.spiders.mock_spider import MockSpider, MockHotListSpider
from crawler.spiders.douyin_spider import DouyinSpider
from crawler.spiders.weibo_spider import WeiboSpider
from crawler.spiders.xiaohongshu_spider import XiaohongshuSpider
from crawler.spiders.tmall_spider import TmallSpider
from crawler.spiders.jd_spider import JdSpider
from crawler.spiders.playwright_spider import PlaywrightSpider
from crawler.pipelines.data_pipeline import DataPipeline


async def main():
    print("=" * 50)
    print("金宫味业 - 数据采集任务启动")
    print("=" * 50)

    pipeline = DataPipeline()

    # 1. 运行模拟爬虫
    spider = MockSpider()
    data = await spider.crawl()
    print(f"[Mock爬虫] 获取 {len(data)} 条数据")
    result = await pipeline.save_batch(data)
    print(f"[写入结果] 成功: {result['success']}, 失败: {result['failed']}")

    # 2. 运行热榜爬虫
    hot_spider = MockHotListSpider()
    hot_data = await hot_spider.crawl()
    print(f"[热榜爬虫] 获取 {len(hot_data)} 条数据")
    result2 = await pipeline.save_batch(hot_data)
    print(f"[写入结果] 成功: {result2['success']}, 失败: {result2['failed']}")

    # 3. 运行抖音爬虫
    douyin_spider = DouyinSpider()
    douyin_data = await douyin_spider.crawl()
    print(f"[抖音爬虫] 获取 {len(douyin_data)} 条数据")
    result3 = await pipeline.save_batch(douyin_data)
    print(f"[写入结果] 成功: {result3['success']}, 失败: {result3['failed']}")

    # 4. 运行微博爬虫
    weibo_spider = WeiboSpider()
    weibo_data = await weibo_spider.crawl()
    print(f"[微博爬虫] 获取 {len(weibo_data)} 条数据")
    result4 = await pipeline.save_batch(weibo_data)
    print(f"[写入结果] 成功: {result4['success']}, 失败: {result4['failed']}")

    # 5. 运行小红书爬虫
    xhs_spider = XiaohongshuSpider()
    xhs_data = await xhs_spider.crawl()
    print(f"[小红书爬虫] 获取 {len(xhs_data)} 条数据")
    result5 = await pipeline.save_batch(xhs_data)
    print(f"[写入结果] 成功: {result5['success']}, 失败: {result5['failed']}")

    # 6. 运行天猫爬虫
    tmall_spider = TmallSpider()
    tmall_data = await tmall_spider.crawl()
    print(f"[天猫爬虫] 获取 {len(tmall_data)} 条数据")
    result6 = await pipeline.save_batch(tmall_data)
    print(f"[写入结果] 成功: {result6['success']}, 失败: {result6['failed']}")

    # 7. 运行京东爬虫
    jd_spider = JdSpider()
    jd_data = await jd_spider.crawl()
    print(f"[京东爬虫] 获取 {len(jd_data)} 条数据")
    result7 = await pipeline.save_batch(jd_data)
    print(f"[写入结果] 成功: {result7['success']}, 失败: {result7['failed']}")

    # 8. 运行 Playwright 爬虫（JS渲染页面）
    pw_spider = PlaywrightSpider()
    pw_data = await pw_spider.crawl()
    print(f"[Playwright爬虫] 获取 {len(pw_data)} 条数据")
    result8 = await pipeline.save_batch(pw_data)
    print(f"[写入结果] 成功: {result8['success']}, 失败: {result8['failed']}")

    await pipeline.close()
    print("\n采集任务完成!")


if __name__ == "__main__":
    asyncio.run(main())
