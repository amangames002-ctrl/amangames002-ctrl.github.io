---
name: netlify-setup
version: 1.0.0
description: 用 noVNC Chrome 透過 GitHub OAuth 註冊 Netlify 帳號。需要先完成 gmail-login 和 github-pages-setup skill。
---

# Netlify 註冊 Skill 🔷

透過 GitHub OAuth 一鍵註冊 Netlify。

> ⚠️ **前置條件：**
> - `novnc-setup` skill 已完成（CDP port 19800 可用）
> - `gmail-login` skill 已完成（Gmail 已登入）
> - `github-pages-setup` skill 已完成（GitHub 帳號已建立且已登入）
>
> ⚠️ **需要用戶提供：** 想要的 team 名稱（例如 `myteam`）

---

## 第 1 步：確認 GitHub 已登入

```bash
curl -s http://127.0.0.1:19800/json/list | python3 -c "
import json,sys
tabs=json.load(sys.stdin)
gh=[t for t in tabs if 'github.com' in t.get('url','')]
if gh:
    print('✅ GitHub tab found:', gh[0]['title'][:60])
else:
    print('⚠️ 沒有 GitHub tab，建議先開一個確認登入狀態')
"
```

如果沒有 GitHub tab，先確認登入：
```
browser action=open profile=novnc-chrome targetUrl=https://github.com
```
等 3 秒後 snapshot，確認右上角有頭像（已登入）。

---

## 第 2 步：打開 Netlify 註冊頁面

```
browser action=open profile=novnc-chrome targetUrl=https://app.netlify.com/signup
```

等待 3 秒後 snapshot：
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：** Netlify 註冊頁面，有多個註冊選項（GitHub, GitLab, Bitbucket, Email）

---

## 第 3 步：點擊「Sign up with GitHub」

1. **在 snapshot 中找到 GitHub 註冊按鈕**（文字包含 "GitHub"）
2. **點擊：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<GitHub按鈕的ref>"}
```

3. **等待 3 秒：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
```

---

## 第 4 步：處理 GitHub OAuth 授權

**可能出現兩種情況：**

### 情況 A：直接跳轉到 Netlify（GitHub 已授權過）
→ 直接到第 5 步

### 情況 B：GitHub OAuth 授權頁面
Snapshot 看到「Authorize Netlify」之類的頁面：

1. **點「Authorize」按鈕：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<Authorize按鈕的ref>"}
```

2. **等待 3 秒，可能要輸入 GitHub 密碼確認：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

3. **如果要求輸入密碼** → 輸入 GitHub 密碼

### 情況 C：開了新分頁/彈窗
```
browser action=tabs profile=novnc-chrome
```
找到 Netlify 或 GitHub OAuth 相關的新分頁，切換過去操作。

---

## 第 5 步：完成 Onboarding

Netlify 首次登入會有 onboarding wizard，**全部跳過或填最少資訊：**

1. **Team name**：輸入用戶提供的 team 名稱
2. **其他問卷**：找「Skip」或「Skip this step」按鈕一路按

每個畫面都：
```
browser action=snapshot profile=novnc-chrome compact=true
```
找按鈕 → 點擊 → 等 2 秒 → 下一個 snapshot

**持續到看到 Netlify Dashboard（Projects 列表頁面）。**

---

## 第 6 步：驗證

```
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：**
- URL 包含 `app.netlify.com`
- 頁面有「Projects」或「Sites」字樣
- 可能是空的 project 列表（正常）

**額外驗證：**
```bash
curl -s http://127.0.0.1:19800/json/list | python3 -c "
import json,sys
tabs=json.load(sys.stdin)
nl=[t for t in tabs if 'netlify' in t.get('url','').lower()]
if nl:
    print('✅ Netlify:', nl[0]['title'][:60], '|', nl[0]['url'][:80])
else:
    print('❌ 沒有 Netlify tab')
"
```

---

## 第 7 步：記錄結果

記錄到 `memory/registrations.md`：
```markdown
| Netlify | app.netlify.com (<TEAMNAME>) | GitHub OAuth | team: <TEAMNAME> |
```

---

## 完成 ✅

你現在有：
- ✅ Netlify 帳號（透過 GitHub OAuth）
- ✅ Team: `<TEAMNAME>`
- ✅ Dashboard: `https://app.netlify.com/teams/<TEAMNAME>/projects`

### 後續部署方式

**方法 1 — Netlify CLI：**
```bash
npm install -g netlify-cli
netlify login  # 會開瀏覽器授權
netlify deploy --dir=/path/to/site --prod
```

**方法 2 — 連結 GitHub repo（自動部署）：**
在 Dashboard 中 New Site → Import from Git → 選 GitHub repo

---

## 故障排除

| 問題 | 解法 |
|------|------|
| OAuth 頁面空白 | 等 5 秒重新 snapshot |
| 「Authorize」後沒反應 | 檢查是否開了新分頁（browser tabs） |
| Onboarding 卡住 | 找任何「Skip」按鈕 |
| GitHub 沒登入 | 先回去執行 github-pages-setup |
| 彈窗擋住 | 按 Escape 或找 X 按鈕關閉 |

## 變數清單

| 變數 | 說明 |
|------|------|
| `<TEAMNAME>` | Netlify team 名稱 |
