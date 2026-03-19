#!/usr/bin/env python3
"""更新 x-digest.html 索引頁"""
import json
import os
from pathlib import Path
from datetime import datetime

REPO_DIR = Path("/tmp/amangames002-ctrl.github.io")
OUTPUT_FILE = REPO_DIR / "x-digest.html"

def get_all_dates():
    """從 repo 目錄取得所有日期 HTML 檔案"""
    dates = []
    for f in REPO_DIR.glob("*.html"):
        if f.name.startswith("20") and f.name.endswith(".html"):
            date_str = f.stem  # 2026-03-17
            dates.append(date_str)
    dates.sort(reverse=True)  # 最新的在前方
    return dates

def generate_index_html(dates):
    """生成索引頁 HTML"""
    dates_info = []
    for date_str in dates:
        # 計算該日期的推文數（從 HTML 標題估算）
        html_file = REPO_DIR / f"{date_str}.html"
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 計算推文數（計算 <article> 標籤數）
                count = content.count('<div class="tweet-content"')
                dates_info.append({'date': date_str, 'count': count})
    
    dates_html = ""
    for date_info in dates_info:
        date_str = date_info['date']
        count = date_info['count']
        date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
        dates_html += f'''
 <a href="{date_str}.html" class="date-item">
 <div class="date">📅 {date_formatted}</div>
 <div class="count">{count} 則推文</div>
 </a>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X Daily Digest</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
 background: #000; color: #e7e9ea;
 font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
 line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto;
}}
.header {{
 padding: 40px 0; border-bottom: 1px solid #2f3336; margin-bottom: 30px; text-align: center;
}}
.header h1 {{ font-size: 36px; font-weight: 800; color: #fff; margin-bottom: 10px; }}
.header p {{ color: #71767b; font-size: 16px; }}
.date-list {{ display: flex; flex-direction: column; gap: 12px; }}
.date-item {{
 display: block; background: #16181c; padding: 20px; border-radius: 16px;
 text-decoration: none; color: #e7e9ea; transition: all 0.2s;
}}
.date-item:hover {{
 background: #1d9bf0; transform: translateY(-2px);
}}
.date-item .date {{ font-size: 18px; font-weight: 700; }}
.date-item .count {{ color: #71767b; font-size: 14px; margin-top: 5px; }}
.date-item:hover .count {{ color: #fff; }}
.footer {{
 text-align: center; padding: 30px 0; color: #71767b; font-size: 14px;
 border-top: 1px solid #2f3336; margin-top: 40px;
}}
</style>
</head>
<body>
<div class="header">
<h1>🐦 X Daily Digest</h1>
<p>每日精選推文</p>
</div>
<div class="date-list">
{dates_html}
</div>
<div class="footer">
<p>每日 08:00 自動更新</p>
</div>
</body>
</html>'''
    return html

def main():
    print("🔄 更新 x-digest.html 索引頁")
    dates = get_all_dates()
    print(f"📅 找到 {len(dates)} 個日期檔案")
    
    html = generate_index_html(dates)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 已生成 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
