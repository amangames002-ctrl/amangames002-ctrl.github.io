---
name: surge-setup
version: 1.0.0
description: 用 CLI 註冊 Surge.sh 帳號並部署靜態網站。不需要瀏覽器，純 terminal 操作。需要 Node.js 和 npm。
---

# Surge.sh 註冊 + 部署 Skill ⚡

Surge.sh 是最簡單的靜態網站 hosting，全程 CLI 操作，不需要瀏覽器。

> ⚠️ **前置條件：**
> - Node.js + npm 已安裝（`node --version` 能跑）
> - 有一個 email 地址（Gmail）
> 
> ⚠️ **需要用戶提供：**
> - Email 地址
> - 自訂密碼（Surge 專用，可以跟 Gmail 不同）
> - 想要的子域名（例如 `mysite` → `mysite.surge.sh`）

---

## 第 1 步：安裝 Surge CLI

```bash
npm install -g surge
```

**驗證：**
```bash
which surge
surge --version
```

**預期輸出：** 版本號，例如 `0.23.1`

**如果 npm 報權限錯誤：**
```bash
sudo npm install -g surge
```

---

## 第 2 步：建立測試網站

```bash
mkdir -p /tmp/surge-site

cat > /tmp/surge-site/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Home</title>
<style>
body{font-family:system-ui;background:#0a0a0a;color:#e7e9ea;max-width:600px;margin:40px auto;padding:16px}
h1{color:#1d9bf0}
</style>
</head>
<body>
<h1>⚡ Surge Site</h1>
<p>Site is live!</p>
</body>
</html>
HTMLEOF

echo "✅ 測試網站建立完成"
ls -la /tmp/surge-site/
```

---

## 第 3 步：註冊 + 部署（一次完成）

Surge 的註冊和部署是同一個指令。**這是互動式 CLI，需要用 pty。**

```bash
# 使用 exec pty=true
cd /tmp/surge-site && surge --domain <DESIRED_NAME>.surge.sh
```

**互動流程：**

```
   Welcome to surge! (surge.sh)
   Login (or create an account) by entering email & password.

          email: <輸入 GMAIL_EMAIL>
       password: <輸入自訂密碼>
```

1. **看到 `email:` 提示** → 輸入用戶提供的 Gmail
2. **看到 `password:` 提示** → 輸入用戶提供的密碼
   - 如果是第一次，會自動建立帳號
   - 密碼輸入時不會顯示字元（正常）
3. **看到 `project:` 提示** → 應該已自動填入 `/tmp/surge-site`，按 Enter
4. **看到 `domain:` 提示** → 應該已自動填入（因為 `--domain` 參數），按 Enter

**如果用 exec tool 操作：**
```
exec command="surge /tmp/surge-site --domain <DESIRED_NAME>.surge.sh" pty=true yieldMs=5000
```

然後依序寫入：
```
process action=write sessionId=<id> data="<GMAIL_EMAIL>\n"
# 等 2 秒
process action=write sessionId=<id> data="<PASSWORD>\n"
```

**預期最終輸出：**
```
   Success! - Published to <DESIRED_NAME>.surge.sh
```

---

## 第 4 步：驗證

```bash
curl -sI https://<DESIRED_NAME>.surge.sh/ | head -3
```

**預期輸出：** `HTTP/2 200` 或 `HTTP/1.1 200`

**如果 404 或 Connection refused：**
1. 確認域名拼寫正確
2. 重新執行 `surge /tmp/surge-site --domain <DESIRED_NAME>.surge.sh`

---

## 第 5 步：保存登入狀態

Surge 登入後會在 `~/.netrc` 保存 token：

```bash
cat ~/.netrc 2>/dev/null | grep surge
```

**預期輸出：** 看到 `machine surge.surge.sh` 和 token

以後再次部署不需要重新輸入帳密。

---

## 第 6 步：記錄結果

記錄到 `memory/registrations.md`：
```markdown
| Surge.sh | <DESIRED_NAME>.surge.sh | email+pwd | 密碼: <提示用戶自行記錄> |
```

⚠️ **密碼務必記錄**，Surge 沒有 OAuth，忘記就要重設。

---

## 完成 ✅

你現在有：
- ✅ Surge.sh 帳號
- ✅ 網站上線：`https://<DESIRED_NAME>.surge.sh/`
- ✅ 登入 token 已保存（`~/.netrc`）

### 後續部署方式

```bash
# 更新網站：
surge /tmp/surge-site --domain <DESIRED_NAME>.surge.sh
# 已登入狀態，不需再輸入帳密
```

### 刪除網站

```bash
surge teardown <DESIRED_NAME>.surge.sh
```

---

## 故障排除

| 問題 | 解法 |
|------|------|
| `npm: command not found` | 先安裝 Node.js（見 novnc-setup skill 第 8 步）|
| `EACCES` 權限錯誤 | `sudo npm install -g surge` |
| 域名已被占用 | 換一個名字，例如加數字 `mysite-01.surge.sh` |
| `Unauthorized` | `~/.netrc` 的 token 過期，重新執行 surge 登入 |
| 互動式卡住 | 確認用 pty=true，或手動用 noVNC terminal |

## 變數清單

| 變數 | 說明 |
|------|------|
| `<GMAIL_EMAIL>` | 註冊用的 email |
| `<PASSWORD>` | Surge 專用密碼（自訂）|
| `<DESIRED_NAME>` | 子域名，例如 `mysite` → `mysite.surge.sh` |
