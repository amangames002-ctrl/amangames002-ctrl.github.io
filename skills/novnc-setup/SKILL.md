---
name: novnc-setup
version: 1.0.0
description: 在最小化 Ubuntu 環境（LXC/VM）安裝 noVNC + Chrome + x11vnc，建立無頭瀏覽器環境供 AI agent 操作。完成後提供 CDP port 供 browser tool 使用。
---

# noVNC + Chrome 環境安裝 Skill 🖥️

在全新的 Ubuntu（最小安裝、LXC、VM 皆適用）上安裝完整的無頭瀏覽器環境。

> ⚠️ 本 skill 的每一步都必須**按順序執行**，不可跳過。
> 每一步執行完必須**檢查輸出**確認成功，失敗就停下來回報。

---

## 第 0 步：確認環境

執行以下指令，確認你在什麼環境：

```bash
# 確認是 Ubuntu
cat /etc/os-release | grep -i ubuntu

# 確認是 root 或有 sudo
whoami
sudo whoami
```

**預期輸出：**
- 看到 `Ubuntu` 字樣
- `sudo whoami` 回傳 `root`

**如果不是 Ubuntu**：本 skill 僅支援 Ubuntu 20.04/22.04/24.04，其他發行版需調整套件名。

---

## 第 1 步：取得使用者名稱

```bash
# 如果是 root，先建立普通使用者（用你的用戶名取代 USERNAME）
# 如果已有普通使用者，跳到下面的 export

# 建立使用者（僅在需要時執行）
# sudo adduser USERNAME
# sudo usermod -aG sudo USERNAME

# 設定變數（替換成實際的使用者名稱）
export TARGET_USER="aman"
echo "使用者: $TARGET_USER"
echo "家目錄: /home/$TARGET_USER"
```

**⚠️ 重要：** 把 `aman` 替換成實際的使用者名稱。後面所有步驟都會用到這個變數。

---

## 第 2 步：更新系統 + 安裝基礎套件

```bash
sudo apt update && sudo apt upgrade -y
```

等它跑完。可能需要 1-5 分鐘。

**預期輸出：** 最後一行類似 `0 upgraded, 0 newly installed` 或 `XX upgraded, XX newly installed`

---

## 第 3 步：安裝 Xvfb（虛擬顯示器）

```bash
sudo apt install -y xvfb
```

**驗證：**
```bash
which Xvfb
```
**預期輸出：** `/usr/bin/Xvfb`

---

## 第 4 步：安裝 openbox（輕量視窗管理器）

```bash
sudo apt install -y openbox
```

**驗證：**
```bash
which openbox
```
**預期輸出：** `/usr/bin/openbox`

---

## 第 5 步：安裝 x11vnc

```bash
sudo apt install -y x11vnc
```

**驗證：**
```bash
which x11vnc
```
**預期輸出：** `/usr/bin/x11vnc`

---

## 第 6 步：安裝 noVNC + websockify

```bash
sudo apt install -y novnc websockify
```

**驗證：**
```bash
which websockify
ls /usr/share/novnc/vnc.html
```
**預期輸出：**
- `/usr/bin/websockify`
- `/usr/share/novnc/vnc.html`（檔案存在，沒有 `No such file`）

**如果 `vnc.html` 不存在：**
```bash
# 有些版本叫 vnc_lite.html
ls /usr/share/novnc/
# 記住實際的 html 檔名，後面會用到
```

---

## 第 7 步：安裝 Google Chrome

```bash
# 下載 Chrome .deb
wget -q -O /tmp/google-chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"

# 安裝（會自動處理相依套件）
sudo apt install -y /tmp/google-chrome.deb

# 如果上面失敗，執行這個修復相依
sudo apt --fix-broken install -y

# 清理
rm -f /tmp/google-chrome.deb
```

**驗證：**
```bash
google-chrome-stable --version
```
**預期輸出：** `Google Chrome XXX.X.XXXX.XX`（任何版本號都可以）

**⚠️ 如果是 ARM64（如 Oracle Cloud ARM）：** Chrome 沒有 ARM 版，改用 Chromium：
```bash
sudo apt install -y chromium-browser
# 後面所有 google-chrome-stable 替換成 chromium-browser
```

---

## 第 8 步：安裝 Node.js（如果還沒有）

```bash
# 檢查是否已安裝
node --version 2>/dev/null

# 如果沒有，安裝 Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 驗證
node --version
npm --version
```

**預期輸出：** `v22.x.x`（或任何 18+ 版本）

---

## 第 9 步：建立 Chrome user data 目錄

```bash
sudo -u $TARGET_USER mkdir -p /home/$TARGET_USER/.config/gchr-novnc
```

**驗證：**
```bash
ls -la /home/$TARGET_USER/.config/gchr-novnc/
```
**預期輸出：** 空目錄，擁有者是 `$TARGET_USER`

---

## 第 10 步：建立 systemd 服務

```bash
# 設定 CDP port（遠端偵錯用）
export CDP_PORT=19800
export VNC_PORT=5900
export NOVNC_PORT=6080
export DISPLAY_NUM=99

cat << SERVICEEOF | sudo tee /etc/systemd/system/xvfb-chrome.service
[Unit]
Description=Xvfb + Chrome + x11vnc + websockify on :${DISPLAY_NUM}
After=network.target

[Service]
Type=forking
User=${TARGET_USER}
Environment=DISPLAY=:${DISPLAY_NUM}
Environment=HOME=/home/${TARGET_USER}
ExecStartPre=/bin/bash -c 'unset WAYLAND_DISPLAY'
ExecStart=/bin/bash -c '\\
    Xvfb :${DISPLAY_NUM} -screen 0 1920x1080x24 -ac & sleep 1; \\
    DISPLAY=:${DISPLAY_NUM} openbox & sleep 1; \\
    unset WAYLAND_DISPLAY; x11vnc -display :${DISPLAY_NUM} -nopw -forever -shared -bg; \\
    websockify -D --web=/usr/share/novnc/ ${NOVNC_PORT} localhost:${VNC_PORT}; \\
    DISPLAY=:${DISPLAY_NUM} google-chrome-stable \\
        --no-first-run --no-default-browser-check \\
        --remote-debugging-port=${CDP_PORT} --remote-allow-origins=* \\
        --user-data-dir=/home/${TARGET_USER}/.config/gchr-novnc \\
        --ozone-platform=x11 \\
        --disable-gpu \\
        "about:blank" &'
ExecStop=/bin/bash -c 'pkill -f "chrome.*gchr-novnc" || true; pkill -f x11vnc || true; pkill -f websockify || true; pkill -f "Xvfb :${DISPLAY_NUM}" || true'
RemainAfterExit=yes
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICEEOF
```

**驗證：**
```bash
cat /etc/systemd/system/xvfb-chrome.service | head -5
```
**預期輸出：** 看到 `[Unit]` 和 `Description=Xvfb + Chrome...`

---

## 第 11 步：啟動服務

```bash
# 重新載入 systemd
sudo systemctl daemon-reload

# 啟用開機自啟
sudo systemctl enable xvfb-chrome.service

# 啟動服務
sudo systemctl start xvfb-chrome.service

# 等 5 秒讓所有元件啟動
sleep 5

# 檢查狀態
sudo systemctl status xvfb-chrome.service
```

**預期輸出：** 看到 `active (exited)` 或 `active (running)`
**如果看到 `failed`：** 執行 `journalctl -u xvfb-chrome.service -n 30` 看錯誤訊息

---

## 第 12 步：驗證所有元件

逐一檢查每個元件是否正常運行：

```bash
echo "=== 1. Xvfb ==="
ps aux | grep -v grep | grep "Xvfb :99" && echo "✅ Xvfb OK" || echo "❌ Xvfb FAILED"

echo ""
echo "=== 2. Chrome ==="
ps aux | grep -v grep | grep "chrome.*gchr-novnc" && echo "✅ Chrome OK" || echo "❌ Chrome FAILED"

echo ""
echo "=== 3. x11vnc ==="
ps aux | grep -v grep | grep x11vnc && echo "✅ x11vnc OK" || echo "❌ x11vnc FAILED"

echo ""
echo "=== 4. websockify ==="
ps aux | grep -v grep | grep websockify && echo "✅ websockify OK" || echo "❌ websockify FAILED"

echo ""
echo "=== 5. CDP (port 19800) ==="
curl -s http://127.0.0.1:19800/json/version | head -1 && echo "✅ CDP OK" || echo "❌ CDP FAILED"

echo ""
echo "=== 6. noVNC Web (port 6080) ==="
curl -sI http://127.0.0.1:6080/vnc.html | head -1 && echo "✅ noVNC OK" || echo "❌ noVNC FAILED"
```

**預期輸出：** 全部 6 個都是 ✅

**如果有 ❌：**
| 失敗元件 | 排查方式 |
|---------|---------|
| Xvfb | `sudo apt install -y xvfb` 重裝 |
| Chrome | `google-chrome-stable --version` 確認已安裝 |
| x11vnc | 檢查 `DISPLAY=:99 x11vnc -display :99 -nopw -forever` 手動啟動 |
| websockify | `which websockify` 確認存在 |
| CDP | Chrome 可能沒啟動，看 `ps aux \| grep chrome` |
| noVNC | websockify 可能沒啟動 |

---

## 第 13 步：設定 OpenClaw browser profile

在 OpenClaw 的 config 中加入 noVNC Chrome 的 CDP profile：

```yaml
# 在 gateway config 中加入
browser:
  profiles:
    novnc-chrome:
      cdpUrl: "http://127.0.0.1:19800"
```

或是告知用戶手動加入。

**驗證（用 browser tool）：**
```
browser action=status profile=novnc-chrome
```
預期：看到連線成功

---

## 第 14 步：停用 GDM（如果有的話）

如果系統有安裝桌面環境（GDM/LightDM），需要停用以免搶 display：

```bash
# 檢查是否有 GDM
systemctl is-active gdm 2>/dev/null
# 如果回傳 active，執行以下停用：
# sudo systemctl disable gdm
# sudo systemctl stop gdm
```

**⚠️ 僅在有 GDM 的情況下執行停用。LXC/最小安裝通常沒有。**

---

## 完成 ✅

安裝完成後你有：

| 元件 | Port | 用途 |
|------|------|------|
| Xvfb | — | 虛擬顯示器 :99 |
| Chrome | CDP 19800 | AI agent 透過 CDP 操控 |
| x11vnc | VNC 5900 | VNC 連線 |
| websockify + noVNC | 6080 | 瀏覽器遠端桌面 `http://<IP>:6080/vnc.html` |

### 下一步

安裝完成後，接著執行 **`gmail-login` skill** 來登入 Gmail。

---

## 故障排除

### Chrome 啟動失敗
```bash
# 手動啟動看錯誤訊息
DISPLAY=:99 google-chrome-stable \
    --no-first-run --no-default-browser-check \
    --remote-debugging-port=19800 --remote-allow-origins=* \
    --user-data-dir=/home/$TARGET_USER/.config/gchr-novnc \
    --ozone-platform=x11 \
    --disable-gpu \
    "about:blank" 2>&1 | head -20
```

### 常見錯誤
| 錯誤訊息 | 解法 |
|---------|------|
| `libatk-bridge-2.0.so.0: cannot open` | `sudo apt install -y libatk-bridge2.0-0` |
| `libnss3.so: cannot open` | `sudo apt install -y libnss3` |
| `libgbm.so.1: cannot open` | `sudo apt install -y libgbm1` |
| `No protocol specified` | 確認 `DISPLAY=:99` 有設定 |
| `chrome: error while loading shared libraries` | `sudo apt --fix-broken install -y` |
| 所有 lib 錯誤的萬能解法 | `sudo apt install -y libxss1 libappindicator3-1 libasound2t64 libatk-bridge2.0-0 libgtk-3-0` |

### 重啟所有服務
```bash
sudo systemctl restart xvfb-chrome.service
sleep 5
# 然後重新執行第 12 步驗證
```
