#!/usr/bin/env python3
"""
通过浏览器工具抓取 X.com 帖子
"""

import json
import subprocess
from datetime import datetime

def run_browser_command(cmd):
    """运行 openclaw browser 命令"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def fetch_posts(count=20):
    """获取帖子"""
    posts = []

    # 先导航到 x.com
    print("导航到 x.com...")
    run_browser_command([
        "openclaw", "browser", "navigate",
        "--profile", "chrome",
        "--targetUrl", "https://x.com/home"
    ])

    # 获取帖子数量
    article_count = 6  # 默认值
    print("检查帖子数量...")
    result = run_browser_command([
        "openclaw", "browser", "act",
        "--profile", "chrome",
        "--request", json.dumps({"kind": "evaluate", "fn": "document.querySelectorAll('article').length"})
    ])

    if result:
        try:
            data = json.loads(result)
            article_count = int(data.get("result", 6))
            print(f"找到 {article_count} 个帖子")
        except:
            article_count = 6
            print(f"默认读取 {article_count} 个帖子")

    # 提取每个帖子的信息
    for i in range(min(article_count, count)):
        try:
            # 获取文本内容
            text_result = run_browser_command([
                "openclaw", "browser", "act",
                "--profile", "chrome",
                "--request", json.dumps({
                    "kind": "evaluate",
                    "fn": f"document.querySelectorAll('article')[{i}].querySelector('[data-testid=\"tweetText\"]')?.textContent || ''"
                })
            ])

            # 获取作者
            author_result = run_browser_command([
                "openclaw", "browser", "act",
                "--profile", "chrome",
                "--request", json.dumps({
                    "kind": "evaluate",
                    "fn": f"document.querySelectorAll('article')[{i}].querySelector('header a')?.textContent || 'Unknown'"
                })
            ])

            # 获取时间
            time_result = run_browser_command([
                "openclaw", "browser", "act",
                "--profile", "chrome",
                "--request", json.dumps({
                    "kind": "evaluate",
                    "fn": f"document.querySelectorAll('article')[{i}].querySelector('time')?.getAttribute('datetime') || ''"
                })
            ])

            text = ""
            if text_result:
                try:
                    data = json.loads(text_result)
                    text = data.get("result", "")
                except:
                    pass

            author = "Unknown"
            if author_result:
                try:
                    data = json.loads(author_result)
                    author = data.get("result", "Unknown")
                except:
                    pass

            time_str = ""
            if time_result:
                try:
                    data = json.loads(time_result)
                    time_str = data.get("result", "")
                except:
                    pass

            if text:
                posts.append({
                    "author": author.strip(),
                    "text": text.strip(),
                    "time": time_str,
                    "index": i + 1
                })
                print(f"✓ 获取第 {i+1} 条帖子: {author[:30]}")

        except Exception as e:
            print(f"获取第 {i+1} 条帖子时出错: {e}")
            continue

    return posts

def main():
    print(f"\n{'='*60}")
    print("X.com 帖子抓取")
    print(f"{'='*60}\n")

    posts = fetch_posts(20)

    print(f"\n{'='*60}")
    print(f"✅ 成功获取 {len(posts)} 个帖子")
    print(f"{'='*60}\n")

    # 保存到文件
    output_file = "/Users/clark/clawd/x-posts-today.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"📄 数据已保存到: {output_file}\n")

    # 显示预览
    if posts:
        print("📰 帖子预览（前10条）：\n")
        for post in posts[:10]:
            print(f"{post['index']}. {post['author']}")
            preview = post['text'][:150] + "..." if len(post['text']) > 150 else post['text']
            print(f"   {preview}\n")

if __name__ == "__main__":
    main()