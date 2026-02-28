#!/usr/bin/env python3
"""
X.com (Twitter) 每日帖子综述脚本
使用当前已打开的 Chrome 浏览器访问 x.com
每天早上 6 点执行
"""

import sys
import asyncio
from datetime import datetime
from pathlib import Path
import subprocess

def start_remote_debugging():
    """
    启动 Chrome 远程调试模式
    """
    debug_port = 9222
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    user_data_dir = Path.home() / "Library/Application Support/Google/Chrome"
    
    # 检查是否已经在调试端口运行（使用 lsof 或 ps）
    try:
        import subprocess
        result = subprocess.run(
            ["lsof", "-i", f":{debug_port}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            print(f"{datetime.now()} - 调试端口 {debug_port} 已在使用")
            return True
    except:
        pass
    
    # 如果 lsof 不可用，检查是否有 Chrome 进程在使用该端口
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if "9222" in result.stdout and "chrome" in result.stdout.lower():
            print(f"{datetime.now()} - Chrome 已在使用调试端口")
            return True
    except:
        pass
    
    print(f"{datetime.now()} - 启动 Chrome 远程调试...")
    
    # 启动 Chrome 远程调试模式
    cmd = [
        chrome_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data_dir}",
        "--new-window",
    ]
    
    # 后台启动
    proc = subprocess.Popen(cmd)
    
    # 等待 Chrome 启动
    import time
    for i in range(30):
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{debug_port}"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                print(f"{datetime.now()} - Chrome 远程调试已启动")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"{datetime.now()} - 警告：Chrome 启动超时")
    return False

async def fetch_posts_with_remote_debugging(port=9222):
    """
    通过 Chrome 远程调试连接到已打开的浏览器
    """
    try:
        from playwright.async_api import async_playwright
        
        print(f"{datetime.now()} - 连接到 Chrome 远程调试端口 {port}...")
        
        async with async_playwright() as p:
            # 连接到现有的 Chrome 实例
            browser = await p.chromium.connect_over_cdp(f"http://localhost:{port}")
            
            print(f"{datetime.now()} - 已连接到浏览器")
            
            # 获取所有上下文
            contexts = browser.contexts
            if not contexts:
                print(f"{datetime.now()} - 警告：没有找到浏览器上下文")
                return []
            
            # 使用第一个上下文
            context = contexts[0]
            pages = context.pages
            
            # 如果有页面，使用第一个；否则创建新页面
            if pages:
                page = pages[0]
                print(f"{datetime.now()} - 使用现有页面")
            else:
                page = await context.new_page()
            
            print(f"{datetime.now()} - 导航到 x.com...")
            
            # 导航到 x.com
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
            print(f"{datetime.now()} - 成功访问 x.com")
            
            # 等待页面加载
            await asyncio.sleep(5)
            
            # 尝试找到帖子元素
            try:
                await page.wait_for_selector("article, [data-testid='tweet']", timeout=15000)
                print(f"{datetime.now()} - 找到帖子元素")
            except:
                print(f"{datetime.now()} - 警告：未找到帖子元素，继续尝试...")
            
            # 滚动加载更多
            for i in range(3):
                print(f"{datetime.now()} - 滚动 {i+1}/3...")
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # 提取帖子
            print(f"{datetime.now()} - 提取帖子内容...")
            posts = await page.evaluate("""
                () => {
                    const articles = document.querySelectorAll('article, [data-testid="tweet"]');
                    const posts = [];
                    
                    articles.forEach((article) => {
                        const textEl = article.querySelector('[data-testid="tweetText"]');
                        const authorEl = article.querySelector('header a, span.css-901oao span');
                        const timeEl = article.querySelector('time');
                        
                        if (textEl && textEl.textContent.trim().length > 0) {
                            posts.push({
                                author: authorEl ? authorEl.textContent.trim().substring(0, 100) : 'Unknown',
                                text: textEl.textContent.trim().substring(0, 500),
                                time: timeEl ? timeEl.getAttribute('datetime') : '',
                            });
                        }
                    });
                    
                    return posts.slice(0, 20);
                }
            """)
            
            print(f"{datetime.now()} - 成功获取 {len(posts)} 个帖子")
            return posts
            
    except Exception as e:
        print(f"{datetime.now()} - 错误：{e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        try:
            if 'browser' in locals():
                await browser.close()
        except:
            pass

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
        if post.get('time'):
            content += f"_时间：{post['time']}_\n\n"
        content += f"---\n\n"
    
    summary_file.write_text(content)
    return summary_file

async def main():
    """
    主函数
    """
    try:
        print("\n" + "="*60)
        print("X.com 每日综述脚本（使用当前浏览器）")
        print("="*60 + "\n")
        
        # 启动远程调试
        if not start_remote_debugging():
            print("\n❌ 无法启动 Chrome 远程调试")
            return False
        
        # 获取帖子
        posts = await fetch_posts_with_remote_debugging()
        
        # 保存结果
        summary_file = save_posts_to_file(posts)
        
        print("\n" + "="*60)
        print(f"✅ 成功获取 {len(posts)} 个帖子")
        print(f"📄 综述文件：{summary_file}")
        print("="*60 + "\n")
        
        if posts:
            print("📰 帖子预览（前5条）：\n")
            for post in posts[:5]:
                preview = post['text'][:120] + "..." if len(post['text']) > 120 else post['text']
                print(f"  • {post['author']}")
                print(f"    {preview}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)