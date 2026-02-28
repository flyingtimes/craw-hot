#!/usr/bin/env python3
"""
X.com (Twitter) 每日帖子综述脚本
每天早上 6 点执行，获取最新 20 个帖子并生成综述
"""

import sys
import asyncio
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
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                str(profile_path),
                headless=True,  # 使用 headless 模式
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = browser.pages[0] if browser.pages else await browser.new_page()
            
            # 访问 X.com，使用 domcontentloaded 而不是 networkidle
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=90000)
            print(f"{datetime.now()} - 成功访问 x.com")
            
            # 等待页面完全加载
            await asyncio.sleep(8)
            
            # 等待帖子内容出现
            try:
                await page.wait_for_selector("article", timeout=20000)
                print(f"{datetime.now()} - 页面内容已加载")
            except Exception as e:
                print(f"{datetime.now()} - 警告：等待帖子超时: {e}")
                # 即使没有找到 article，也继续尝试提取
            
            # 滚动加载更多帖子
            for i in range(4):
                print(f"{datetime.now()} - 滚动加载帖子 {i+1}/4...")
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
            
            # 提取帖子内容
            print(f"{datetime.now()} - 开始提取帖子内容...")
            posts_data = await page.evaluate("""
                () => {
                    const articles = document.querySelectorAll('article');
                    const posts = [];

                    // 遍历所有帖子
                    articles.forEach((article) => {
                        const textEl = article.querySelector('[data-testid="tweetText"]');
                        const authorEl = article.querySelector('header a');
                        const timeEl = article.querySelector('time');
                        const linkEl = article.querySelector('a[href*="/status/"]');

                        if (textEl && textEl.textContent.trim().length > 0) {
                            posts.push({
                                author: authorEl ? authorEl.textContent.trim() : 'Unknown',
                                text: textEl.textContent.trim().substring(0, 500), // 限制长度
                                time: timeEl ? timeEl.getAttribute('datetime') : '',
                                url: linkEl ? linkEl.href : ''
                            });
                        }
                    });

                    return posts.slice(0, 20); // 只返回前20个
                }
            """)
            
            posts = posts_data
            print(f"{datetime.now()} - 成功获取 {len(posts)} 个帖子")
            
    except Exception as e:
        print(f"{datetime.now()} - 错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if 'browser' in locals():
                await browser.close()
        except:
            pass
    
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
        if post.get('url'):
            content += f"[查看原文]({post['url']})\n\n"
        content += f"---\n\n"
    
    summary_file.write_text(content)
    return summary_file

def main():
    """
    主函数：获取帖子并保存
    """
    try:
        posts = asyncio.run(fetch_posts_from_x())
        summary_file = save_posts_to_file(posts)
        
        print(f"\n{'='*60}")
        print(f"✅ 成功获取 {len(posts)} 个帖子")
        print(f"📄 综述文件已保存到：{summary_file}")
        print(f"{'='*60}\n")
        
        # 打印前5个帖子预览
        if posts:
            print("📰 帖子预览（前5条）：\n")
            for post in posts[:5]:
                preview = post['text'][:120] + "..." if len(post['text']) > 120 else post['text']
                print(f"  • {post['author']}")
                print(f"    {preview}\n")
        
        # 保存到日志
        log_file = Path.home() / "code/x-summary.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"获取帖子数：{len(posts)}\n")
            f.write(f"综述文件：{summary_file}\n")
            f.write(f"{'='*60}\n\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        
        # 记录错误到日志
        log_file = Path.home() / "code/x-summary.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"\n❌ 执行失败：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"错误：{str(e)}\n\n")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)