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

    await pipeline.close()
    print("\n采集任务完成!")


if __name__ == "__main__":
    asyncio.run(main())
