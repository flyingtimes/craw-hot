#!/usr/bin/env python3
"""
诊断脚本：检查 X.com 页面实际加载的内容
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

profile_path = Path.home() / "Library/Application Support/Google/Chrome/Default"

async def diagnose():
    print("启动诊断...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            str(profile_path),
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        try:
            print("访问 x.com...")
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=90000)
            print("✅ 页面加载成功")
            
            # 等待
            await asyncio.sleep(5)
            
            # 截图
            screenshot_path = "/Users/clark/clawd/scripts/diagnose_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ 截图已保存：{screenshot_path}")
            
            # 检查页面结构
            print("\n检查页面元素...")
            
            # 尝试各种可能的选择器
            selectors = [
                "article",
                "[data-testid='tweet']",
                "[data-testid='tweet-text']",
                ".tweet",
                ".Post",
                "div[role='article']",
                "[class*='tweet']",
                "[class*='Post']",
            ]
            
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"  ✅ 找到 {len(elements)} 个元素匹配 '{selector}'")
                    else:
                        print(f"  ❌ 未找到元素 '{selector}'")
                except Exception as e:
                    print(f"  ⚠️ 检查 '{selector}' 时出错: {e}")
            
            # 获取页面 HTML 的一部分用于分析
            html_preview = await page.evaluate("() => document.body.innerHTML.substring(0, 5000)")
            print(f"\n页面 HTML 预览（前5000字符）:\n{html_preview[:1000]}")
            
            # 检查是否有 Twitter 的特征元素
            has_twitter_element = await page.evaluate("""
                () => {
                    // 检查常见的 Twitter 元素
                    const tweets = document.querySelectorAll('article, [data-testid="tweet"], [data-testid="tweet-text"], [class*="tweet"], [class*="Post"]');
                    const buttons = document.querySelectorAll('button, a, [role="button"]');
                    
                    return {
                        tweets: tweets.length,
                        buttons: buttons.length,
                        hasTweetText: !!document.querySelector('[data-testid="tweetText"]'),
                        hasMainColumn: !!document.querySelector('[data-testid="primaryColumn"]'),
                    };
                }
            """)
            
            print(f"\n页面特征检查:")
            for key, value in has_twitter_element.items():
                print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose())