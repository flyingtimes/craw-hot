#!/usr/bin/env python3
"""
X.com (Twitter) 每日帖子综述脚本
每天早上 6 点执行，获取最新 20 个帖子并生成综述
"""

import json
import sys
import asyncio
import os
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

def get_chrome_profile_path():
    """获取 Chrome 默认用户数据目录"""
    return Path.home() / "Library/Application Support/Google/Chrome/Default"

async def fetch_posts_from_x():
    """
    通过已登录的 Chrome 浏览器访问 x.com 并获取最新的 20 个帖子
    """
    if not HAS_PLAYWRIGHT:
        print("❌ Playwright 未安装")
        return []
    
    print(f"{datetime.now()} - 开始获取 x.com 帖子...")
    
    profile_path = get_chrome_profile_path()
    if not profile_path.exists():
        print(f"❌ Chrome 用户数据目录不存在：{profile_path}")
        return []
    
    posts = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            str(profile_path),
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        try:
            # 访问 X.com，增加超时时间
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
            print(f"{datetime.now()} - 成功访问 x.com")
            
            # 等待更多内容加载
            await asyncio.sleep(5)
            await page.wait_for_selector("article", timeout=30000)
            
            # 滚动加载更多帖子
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # 提取帖子内容
            posts_data = await page.evaluate("""
                () => {
                    const articles = document.querySelectorAll('article');
                    return Array.from(articles).slice(0, 20).map(article => {
                        const text = article.querySelector('[data-testid="tweetText"]');
                        const author = article.querySelector('header a');
                        const time = article.querySelector('time');
                        
                        return {
                            author: author ? author.textContent.trim() : 'Unknown',
                            text: text ? text.textContent.trim() : '',
                            time: time ? time.getAttribute('datetime') : '',
                        };
                    }).filter(p => p.text && p.text.length > 0);
                }
            """)
            
            posts = posts_data
            print(f"{datetime.now()} - 成功获取 {len(posts)} 个帖子")
            
        except Exception as e:
            print(f"{datetime.now()} - 错误：{e}")
        finally:
            await browser.close()
    
    return posts

def save_posts_to_file(posts):
    """保存帖子到文件"""
    summary_file = Path("/Users/clark/clawd/scripts/x-summary-today.md")
    
    content = f"# X.com 每日综述\n\n"
    content += f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += f"📊 共获取 {len(posts)} 条帖子\n\n"
    content += "---\n\n"
    
    for i, post in enumerate(posts, 1):
        content += f"### {i}. {post['author']}\n\n"
        content += f"{post['text']}\n\n"
        content += f"_时间：{post.get('time', 'N/A')}_\n\n"
        content += "---\n\n"
    
    summary_file.write_text(content)
    return summary_file

def main():
    """
    主函数：获取帖子并保存
    """
    try:
        posts = asyncio.run(fetch_posts_from_x())
        summary_file = save_posts_to_file(posts)
        
        print(f"\n✅ 成功获取 {len(posts)} 个帖子")
        print(f"📄 综述文件已保存到：{summary_file}")
        print(f"\n📰 帖子摘要:")
        for post in posts[:5]:
            preview = post['text'][:100] + "..." if len(post['text']) > 100 else post['text']
            print(f"  • {post['author']}: {preview}")
        
        # 这里应该调用 OpenClaw 的 message 工具发送综述
        # 由于这是 cron 任务，我们会保存到日志，由主进程读取并发送
        log_file = Path.home() / "code/x-summary.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(f"获取帖子数: {len(posts)}\n")
            f.write(f"综述文件: {summary_file}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
