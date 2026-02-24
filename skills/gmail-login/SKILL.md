---
name: gmail-login
version: 1.0.0
description: 透過 noVNC Chrome (CDP) 登入 Gmail 帳號。需要先完成 novnc-setup skill。用戶需提供帳號密碼，並協助首次登入驗證。
---

# Gmail 登入 Skill 📧

透過 noVNC Chrome 登入 Gmail，為後續所有 Google OAuth 服務打基礎。

> ⚠️ **前置條件：** 必須先完成 `novnc-setup` skill，確認 CDP port 19800 可用。
> 
> ⚠️ **需要用戶提供：** Gmail 帳號、密碼。首次登入可能需要用戶協助驗證（手機/備用信箱驗證碼）。

---

## 第 0 步：確認 noVNC Chrome 正常運行

```bash
curl -s http://127.0.0.1:19800/json/version | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('✅ Chrome', d.get('Browser','?'))
" 2>/dev/null || echo "❌ CDP 無法連線，請先執行 novnc-setup skill"
```

**預期輸出：** `✅ Chrome Chrome/XXX.X.XXXX.XX`

**如果 ❌：** 停止，先回去執行 `novnc-setup` skill。

---

## 第 1 步：取得用戶資訊

向用戶要以下資訊（缺一不可）：

| 資訊 | 說明 | 範例 |
|------|------|------|
| Gmail 帳號 | 完整 email | example@gmail.com |
| 密碼 | Gmail 密碼 | xxxxxxxx |

**收到後設定變數（僅在你腦中記住，不要寫到檔案）：**
- `GMAIL_EMAIL` = 用戶提供的 email
- `GMAIL_PASSWORD` = 用戶提供的密碼

---

## 第 2 步：打開 Gmail 登入頁

使用 browser tool：

```
browser action=open profile=novnc-chrome targetUrl=https://accounts.google.com/signin
```

**等待 3 秒：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
```

**截圖確認：**
```
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：** Google 登入頁面，有一個 email 輸入框

---

## 第 3 步：輸入 Email

1. **找到 email 輸入框**（snapshot 中找 `textbox` 或 `input` 類型的 ref）

2. **點擊輸入框：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<email輸入框的ref>"}
```

3. **輸入 email：**
```
browser action=act profile=novnc-chrome request={"kind":"type","ref":"<email輸入框的ref>","text":"<GMAIL_EMAIL>"}
```

4. **點「下一步」按鈕：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<下一步按鈕的ref>"}
```

5. **等待 3 秒，然後 snapshot 確認進到密碼頁面：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":3000}
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：** 密碼輸入頁面

**如果看到「驗證你的身分」或「不尋常的活動」：**
→ 跳到「故障排除 - 驗證要求」

---

## 第 4 步：輸入密碼

1. **找到密碼輸入框**（snapshot 中找 password 類型的 ref）

2. **點擊並輸入密碼：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<密碼輸入框的ref>"}
browser action=act profile=novnc-chrome request={"kind":"type","ref":"<密碼輸入框的ref>","text":"<GMAIL_PASSWORD>"}
```

3. **點「下一步」：**
```
browser action=act profile=novnc-chrome request={"kind":"click","ref":"<下一步按鈕的ref>"}
```

4. **等待 5 秒（密碼驗證較慢）：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":5000}
browser action=snapshot profile=novnc-chrome compact=true
```

---

## 第 5 步：處理可能的驗證關卡

登入後可能出現以下情況，**依照看到的畫面選擇對應處理方式：**

### 情況 A：直接進入 Gmail 收件匣 ✅
看到 `mail.google.com` 或收件匣 → **登入成功！跳到第 7 步。**

### 情況 B：兩步驟驗證（2FA）
看到要求輸入驗證碼 → **告知用戶：**

```
「Gmail 要求兩步驟驗證。請檢查你的手機/備用信箱，
告訴我收到的驗證碼（6位數字）。」
```

收到驗證碼後：
1. 找到驗證碼輸入框
2. 輸入驗證碼
3. 點「下一步」/「驗證」
4. 等待 3 秒，snapshot 確認

### 情況 C：「確認這是你本人」
看到選擇驗證方式的頁面 → **告知用戶：**

```
「Google 要求額外驗證。畫面上有以下選項：
1. 發送驗證碼到 XXX
2. ...

請告訴我要用哪個方式，或直接提供驗證碼。」
```

### 情況 D：「不尋常的登入活動」
看到安全警告 → **告知用戶：**

```
「Google 偵測到不尋常的登入，可能因為是新裝置。
請到你的手機上點擊 Google 的通知確認是你本人，
或者告訴我備用驗證方式。」
```

### 情況 E：「保護你的帳號」彈窗
有時登入後會跳出建議加強安全性 → **直接跳過/關閉**

---

## 第 6 步：處理登入後彈窗

登入成功後可能出現各種提示，全部跳過：

1. **「保持登入狀態？」** → 點「是」
2. **「Chrome 同步」** → 點「不用了」或關閉
3. **「個人化」** → 跳過/關閉
4. **任何「稍後再說」** → 點它

**每次處理完一個彈窗：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":2000}
browser action=snapshot profile=novnc-chrome compact=true
```

---

## 第 7 步：導航到 Gmail 收件匣

```
browser action=navigate profile=novnc-chrome targetUrl=https://mail.google.com/mail/u/0/#inbox
```

**等待 5 秒：**
```
browser action=act profile=novnc-chrome request={"kind":"wait","timeMs":5000}
browser action=snapshot profile=novnc-chrome compact=true
```

**預期看到：** Gmail 收件匣頁面

---

## 第 8 步：最終驗證

```bash
# 用 CDP 確認 Gmail tab 存在
curl -s http://127.0.0.1:19800/json/list | python3 -c "
import json,sys
tabs=json.load(sys.stdin)
gmail=[t for t in tabs if 'mail.google' in t.get('url','')]
if gmail:
    print('✅ Gmail 已登入:', gmail[0]['title'][:60])
else:
    print('❌ 找不到 Gmail tab')
"
```

**預期輸出：** `✅ Gmail 已登入: 收件匣 (XX) - xxx@gmail.com - Gmail`

---

## 第 9 步：記錄結果

登入成功後，**必須**記錄到 `memory/registrations.md`：

```markdown
| Gmail | <email> | 密碼 | noVNC Chrome 已登入 |
```

**⚠️ 不要把密碼明文寫入檔案。** 只記錄帳號和登入方式。

---

## 完成 ✅

Gmail 登入完成。現在你有：
- ✅ noVNC Chrome 中的 Gmail 已登入 session
- ✅ Google OAuth 可用（後續服務可以用「Sign in with Google」）
- ✅ 可以收取驗證信

### 下一步

可以開始執行以下 skill：
- `github-signup` — 註冊 GitHub 帳號（Google OAuth）
- `web-signup` — 批量註冊 hosting 服務

---

## 故障排除

### Google 完全封鎖登入
如果看到「此瀏覽器或應用可能不安全」：
1. 確認 Chrome 是最新版（`google-chrome-stable --version`）
2. 確認沒加 `--headless` 參數
3. 可能需要先在手機上允許不安全應用

### Cookie / Session 保活
登入成功後，Chrome user data 會保存 session。但 Google session 會過期。

**建議設定 crontab 定期保活：**
```bash
# 每 3 天凌晨 3:00 訪問 Gmail 保活
echo "0 3 */3 * * curl -s http://127.0.0.1:19800/json/list > /dev/null" | crontab -
```

### noVNC 人工介入
如果 AI agent 無法處理驗證（例如圖片驗證碼），請用戶：
1. 打開瀏覽器訪問 `http://<伺服器IP>:6080/vnc.html`
2. 手動操作完成驗證
3. 完成後告知 AI agent 繼續

### 多帳號
如果需要登入多個 Gmail：
- 方法 1：Chrome profiles（不同 `--user-data-dir`）
- 方法 2：登入第一個帳號後，用 Google 多帳號切換
- **推薦方法 1**，避免帳號間干擾
