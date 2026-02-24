---
name: render-setup
version: 1.0.0
description: 用 noVNC Chrome 透過 Google OAuth 一鍵註冊 Render 帳號。所有服務中最簡單的。需要先完成 gmail-login skill。
---

# Render 註冊 Skill 🟢

Google OAuth 一鍵完成，是所有服務中最簡單的。

> ⚠️ **前置條件：**
> - `novnc-setup` skill 已完成（CDP port 19800 可用）
> - `gmail-login` skill 已完成（Gmail 已登入）
>
> ⚠️ **不需要用戶額外提供任何資訊**（Google OAuth 自動帶入）

---

## 第 1 步：打開 Render 註冊頁面

```
browser action=open profile=novnc-chrome targetUrl=https://dashboard.render.com/register
```

等待 3 秒後 snapshot：
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：** Render 註冊頁面，有 Google / GitHub / GitLab / Email 等選項

---

## 第 2 步：點擊「Google」

1. **在 snapshot 中找到 Google 登入按鈕**（文字包含 "Google"）
2. **點擊：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<Google按鈕的ref>"}
```

3. **等待 3 秒：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

---

## 第 3 步：處理 Google OAuth

**可能出現的情況：**

### 情況 A：Google 帳號選擇頁面
看到「選擇帳號」頁面：
1. **找到你的 Gmail 帳號**
2. **點擊：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<帳號的ref>"}
```

### 情況 B：Google 授權確認
看到「Render 想要存取你的 Google 帳號」：
1. **點「允許」或「Continue」**

### 情況 C：直接跳轉到 Render Dashboard
→ 登入成功！跳到第 4 步

### 情況 D：開了新分頁/彈窗
```
browser action=tabs profile=novnc-chrome
```
找到 Google OAuth 相關的新分頁，切換過去操作。

**每次操作後：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

---

## 第 4 步：處理 Onboarding（如果有）

Render 可能會問幾個問題：
- 用途？→ 選 Personal / Hobby
- 其他問卷 → 找 Skip 或最快的選項

---

## 第 5 步：驗證

```
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：**
- URL 包含 `dashboard.render.com`
- 頁面有 Dashboard / Projects / Services 字樣

**額外驗證：**
```bash
curl -s http://127.0.0.1:19800/json/list | python3 -c "
import json,sys
tabs=json.load(sys.stdin)
rn=[t for t in tabs if 'render.com' in t.get('url','').lower()]
if rn:
    print('✅ Render:', rn[0]['title'][:60], '|', rn[0]['url'][:80])
else:
    print('❌ 沒有 Render tab')
"
```

---

## 第 6 步：記錄結果

記錄到 `memory/registrations.md`：
```markdown
| Render | dashboard.render.com | Google OAuth | — |
```

---

## 完成 ✅

你現在有：
- ✅ Render 帳號（透過 Google OAuth）
- ✅ Dashboard: `https://dashboard.render.com/`

### 後續部署方式

在 Dashboard 中：
- **Static Site**: New → Static Site → 連結 GitHub repo
- **Web Service**: New → Web Service → 連結 GitHub repo（支援 Node.js/Python/Go 等）

---

## 故障排除

| 問題 | 解法 |
|------|------|
| Google OAuth 彈窗沒出現 | 用 `browser tabs` 找新分頁 |
| 帳號選擇頁面沒出現 | Gmail 只有一個帳號時會自動選擇 |
| 授權後白畫面 | 等 5 秒再 snapshot |
| 「此瀏覽器不安全」| 確認 Chrome 不是用 --headless |

## 變數清單

| 變數 | 說明 |
|------|------|
| （無）| Render 用 Google OAuth，不需額外變數 |
