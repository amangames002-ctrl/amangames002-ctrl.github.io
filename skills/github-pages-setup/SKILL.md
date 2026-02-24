---
name: github-pages-setup
version: 1.0.0
description: 註冊 GitHub 帳號（Google OAuth）、建立 PAT、建立 GitHub Pages 網站。需要先完成 gmail-login skill。
---

# GitHub Pages 完整設置 Skill 🐙

從 GitHub 註冊到 Pages 網站上線的完整流程。

> ⚠️ **前置條件：**
> - `novnc-setup` skill 已完成（CDP port 19800 可用）
> - `gmail-login` skill 已完成（Gmail 已登入）
> 
> ⚠️ **需要用戶提供：** 想要的 GitHub 用戶名（例如 `myname-bot`）

---

## Part A：註冊 GitHub 帳號

如果已有 GitHub 帳號，跳到 Part B。

### A-1：打開 GitHub 註冊頁

```
browser action=open profile=novnc-chrome targetUrl=https://github.com/signup
```

等待 3 秒後 snapshot：
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

### A-2：填寫註冊表單

GitHub signup 是分步驟的，每次只顯示一個欄位：

**步驟 1 — Email：**
1. 找到 email 輸入框的 ref
2. 輸入 Gmail 地址：
```
browser action=act profile=novnc-chrome request={"kind":"type","ref":"<ref>","text":"<GMAIL_EMAIL>"}
```
3. 點「Continue」

**步驟 2 — 密碼：**
1. 找到 password 輸入框的 ref
2. 輸入密碼（自訂一個強密碼）：
```
browser action=act profile=novnc-chrome request={"kind":"type","ref":"<ref>","text":"<自訂密碼>"}
```
3. 點「Continue」

**步驟 3 — Username：**
1. 找到 username 輸入框的 ref
2. 輸入用戶提供的用戶名：
```
browser action=act profile=novnc-chrome request={"kind":"type","ref":"<ref>","text":"<USERNAME>"}
```
3. 如果顯示「Username is already taken」→ 告知用戶換一個
4. 點「Continue」

**步驟 4 — Email preferences：**
1. 通常問要不要收通知信
2. 輸入 `n` 或取消勾選
3. 點「Continue」

**步驟 5 — 驗證（拼圖/圖片）：**
⚠️ **這裡很可能出現人機驗證（CAPTCHA）。**

如果出現拼圖或圖片驗證：
```
「GitHub 要求人機驗證（圖片/拼圖），AI 無法自動完成。
請到 noVNC 手動操作：http://<IP>:6080/vnc.html
完成驗證後告訴我。」
```

### A-3：Email 驗證碼

GitHub 會發驗證碼到 Gmail。

1. **開新分頁到 Gmail：**
```
browser action=open profile=novnc-chrome targetUrl=https://mail.google.com/mail/u/0/#inbox
```

2. **等 5 秒，snapshot 找 GitHub 的驗證信：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":5000}
browser action=snapshot profile=novnc-chrome compact=true
```

3. **點開 GitHub 的驗證信，找到 6-8 位數驗證碼**

4. **回到 GitHub 分頁，輸入驗證碼**

5. **告知用戶驗證碼是什麼，請用戶確認要輸入**

### A-4：完成 Onboarding

GitHub 註冊後會有 onboarding 問卷：
- 「How many team members?」→ 選 Just me
- 「What features are you interested in?」→ 全部跳過
- 找「Skip this step」或「Continue」一路按到底

**驗證：**
```
browser action=snapshot profile=novnc-chrome compact=true
```
看到 GitHub Dashboard → 註冊成功 ✅

### A-5：記錄帳號

記錄到 `memory/registrations.md`：
```markdown
| GitHub | <USERNAME> | Google OAuth / email+pwd | 已完成 |
```

---

## Part B：建立 Personal Access Token (PAT)

PAT 用於 git push，不需每次輸入密碼。

### B-1：打開 PAT 建立頁面

```
browser action=open profile=novnc-chrome targetUrl=https://github.com/settings/tokens/new?scopes=repo&description=auto-deploy
```

等待 3 秒後 snapshot：
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

### B-2：設定 Token

1. **Note（描述）：** 應該已自動填入 `auto-deploy`，沒有的話手動填
2. **Expiration（期限）：** 選 `30 days` 或 `90 days`
3. **Scopes（權限）：** `repo` 應該已勾選（URL 參數帶的）
   - 確認 `repo` 前面有打勾 ✅
   - 不需要其他權限

### B-3：生成 Token

1. **滾到頁面底部**
2. **點「Generate token」按鈕**
3. **等待 3 秒**

### B-4：複製 Token

⚠️ **Token 只顯示一次，必須立刻複製！**

```
browser action=act profile=novnc-chrome request={"kind":"evaluate","fn":"(function(){ var code = document.querySelector('#new-oauth-token') || document.querySelector('code'); return code ? (code.value || code.textContent) : 'NOT_FOUND'; })()"}
```

**預期輸出：** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`（以 `ghp_` 開頭）

**如果是 `NOT_FOUND`：**
```
browser action=snapshot profile=novnc-chrome compact=true
```
手動從 snapshot 中找到 token 文字。

### B-5：保存 Token

```bash
# 存到本地檔案（注意權限）
echo "ghp_xxxxxx" > /home/<USER>/.github-pat
chmod 600 /home/<USER>/.github-pat
```

同時設定 git credential：
```bash
git config --global credential.helper store
```

---

## Part C：建立 GitHub Pages 網站

### C-1：建立 Repository

```bash
PAT=$(cat /home/<USER>/.github-pat)
USERNAME="<USERNAME>"

# 建立 <username>.github.io repo
curl -s -H "Authorization: token $PAT" \
  -d "{\"name\":\"${USERNAME}.github.io\",\"auto_init\":true}" \
  https://api.github.com/user/repos | python3 -c "
import json,sys
d=json.load(sys.stdin)
if 'html_url' in d:
    print('✅ Repo created:', d['html_url'])
elif 'errors' in d:
    print('❌ Error:', d['errors'][0].get('message','unknown'))
else:
    print('⚠️ Response:', json.dumps(d)[:200])
"
```

**預期輸出：** `✅ Repo created: https://github.com/<USERNAME>/<USERNAME>.github.io`

**如果 repo 已存在：** 不需要再建，直接下一步。

### C-2：Clone 並初始化

```bash
PAT=$(cat /home/<USER>/.github-pat)
USERNAME="<USERNAME>"

cd /tmp
rm -rf gh-pages-setup
git clone https://${PAT}@github.com/${USERNAME}/${USERNAME}.github.io.git gh-pages-setup
cd gh-pages-setup
```

### C-3：加入必要檔案

```bash
# .nojekyll — 關鍵！不加這個 HTML 會 404
touch .nojekyll

# index.html — 首頁
cat > index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Home</title>
<style>
body{font-family:system-ui;background:#0a0a0a;color:#e7e9ea;max-width:600px;margin:40px auto;padding:16px}
h1{color:#1d9bf0}
a{color:#1d9bf0}
</style>
</head>
<body>
<h1>🏠 Welcome</h1>
<p>Site is live!</p>
</body>
</html>
HTMLEOF
```

### C-4：Push

```bash
git add -A
git -c user.name="${USERNAME}" -c user.email="<GMAIL_EMAIL>" \
  commit -m "Initial setup with .nojekyll"
git push 2>&1
```

**預期輸出：** `main -> main`（push 成功）

### C-5：等待部署 + 驗證

```bash
echo "等待 GitHub Pages 部署..."
sleep 30

# 驗證
curl -sI https://${USERNAME}.github.io/ | head -3
```

**預期輸出：** `HTTP/2 200`

**如果 404：**
1. 再等 30 秒重試
2. 確認 `.nojekyll` 檔案存在
3. 到 repo Settings → Pages 確認 Source 是 `main` / `/ (root)`

如果 Settings 裡 Pages 沒有自動啟用：
```
browser action=open profile=novnc-chrome targetUrl=https://github.com/<USERNAME>/<USERNAME>.github.io/settings/pages
```
找到 Source dropdown，選 `main` branch，`/ (root)` 目錄，點 Save。

### C-6：記錄結果

記錄到 `memory/registrations.md`：
```markdown
| GitHub Pages | <USERNAME>.github.io | — | PAT 存在 ~/.github-pat |
```

---

## 完成 ✅

你現在有：
- ✅ GitHub 帳號（`<USERNAME>`）
- ✅ Personal Access Token（存在 `~/.github-pat`）
- ✅ GitHub Pages 網站（`https://<USERNAME>.github.io/`）

### 後續部署方式

```bash
# 以後要更新網站內容：
PAT=$(cat /home/<USER>/.github-pat)
cd /tmp/gh-pages-setup  # 或重新 clone
# 修改/新增 HTML 檔案
git add -A && git commit -m "update" && git push
# 等 30 秒生效
```

---

## 故障排除

| 問題 | 解法 |
|------|------|
| `repo name already exists` | repo 已存在，直接 clone 用 |
| push 403 | PAT 過期或權限不足，重新建立 PAT |
| Pages 404 | 確認有 `.nojekyll`，確認 Settings/Pages source 是 main |
| 部署慢 | 正常要 30-60 秒，最慢 5 分鐘 |
| CAPTCHA 卡關 | 告知用戶手動到 noVNC 完成 |

## 變數清單

| 變數 | 說明 |
|------|------|
| `<USERNAME>` | GitHub 用戶名 |
| `<GMAIL_EMAIL>` | Gmail 地址 |
| `<USER>` | Linux 系統用戶名 |
| `<IP>` | 伺服器 IP |
