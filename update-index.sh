#!/bin/bash
# 簡單更新 index.html 加入今天的連結
sed -i 's|</ul>|<li><a href="2026-03-17.html">2026-03-17</a></li></ul>|g' index.html 2>/dev/null || true
git add index.html
git commit -m "Add 2026-03-17 link" 2>/dev/null || true
git push origin main 2>&1
