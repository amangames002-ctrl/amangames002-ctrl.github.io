#!/usr/bin/env python3
"""
Token Usage Collector - 全新版本
從 OpenClaw agent session jsonl 文件收集 token 使用量

使用方法：python3 collect-tokens.py
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict
import glob

WORKSPACE = Path.home() / ".openclaw" / "workspace"
TOKEN_FILE = WORKSPACE / "token-dashboard" / "data" / "tokens.json"

# 模型名稱標準化映射
MODEL_ALIASES = {
    # MiniMax
    'minimax/M2.5': 'MiniMax-M2.5',
    'minimax-portal/MiniMax-M2.5': 'MiniMax-M2.5',
    'minimax/MiniMax-M2.5': 'MiniMax-M2.5',
    'minimax-portal/minimax-m2.1': 'MiniMax-M2.1',
    'minimax/MiniMax-M2.1': 'MiniMax-M2.1',
    # GLM
    'z-ai/glm5': 'GLM-5',
    'nvidia/z-ai/glm5': 'GLM-5',
    'mydamo/glm-4.7': 'GLM-4.7',
    'nvidia/z-ai/glm4.7': 'GLM-4.7',
    # Claude (anyrouter)
    'anyrouter/claude-opus-4-6': 'Claude-Opus4.6',
    'anyrouter/claude-sonnet-4-6': 'Claude-Sonnet4.6',
    'anyrouter/claude-haiku-4-5': 'Claude-Haiku4.5',
    # Claude (penguin)
    'penguinsaichat/claude-opus-4-5': 'Claude-Opus4.5',
    'penguinsaichat/claude-sonnet-4-6': 'Claude-Sonnet4.6',
    'penguinsaichat/claude-haiku-4-5': 'Claude-Haiku4.5',
    # Llama
    'meta/llama-3.3-70b-instruct': 'Llama3.3-70B',
    'nvidia/meta/llama-3.3-70b-instruct': 'Llama3.3-70B',
    # Qwen
    'qwen/qwen3.5-397b-a17b': 'Qwen3.5-397B',
    'ollama/qwen3.5:cloud': 'Qwen3.5-Cloud',
    # GPT (anyrouter)
    'anyrouter/gpt-5-codex': 'GPT-5-Codex',
    'anyrouter/gpt-5.2-codex': 'GPT-5.2-Codex',
    'anyrouter/gpt-5.3-codex': 'GPT-5.3-Codex',
    # GPT (penguin)
    'penguin-gpt/gpt-5.2-codex': 'GPT-5.2-Codex',
    'penguin-gpt/gpt-5.3-codex': 'GPT-5.3-Codex',
}

def normalize_model(model_name):
    """標準化模型名稱"""
    if not model_name:
        return None
    
    model_lower = model_name.lower().strip()
    
    # 檢查別名映射（精確匹配）
    if model_name in MODEL_ALIASES:
        return MODEL_ALIASES[model_name]
    
    # 模糊匹配
    for alias, normalized in MODEL_ALIASES.items():
        alias_lower = alias.lower()
        # 完全包含
        if alias_lower in model_lower or model_lower in alias_lower:
            return normalized
        # 部分匹配
        if any(p in alias_lower or alias_lower in p for p in model_lower.split('-')):
            return normalized
    
    # 處理 provider/model 格式
    if '/' in model_name:
        parts = model_name.split('/')
        short_name = parts[-1].strip()
        # 進一步處理，如 "claude-opus-4-6" -> "Claude-Opus4.6"
        if 'claude' in short_name.lower():
            # 轉換格式
            return short_name.replace('-', ' ').title().replace(' ', '-')
        if 'gpt' in short_name.lower():
            return short_name.replace('.', '-').upper()
        return short_name.title()
    
    # 返回標題格式
    return model_name.replace('-', ' ').title().replace(' ', '-')

def collect_token_usage():
    """從所有 session jsonl 文件收集 token 使用量"""
    agents_dir = Path.home() / ".openclaw" / "agents"
    
    # 過去 30 天
    today = datetime.now(timezone.utc)
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 按 (日期, 模型) 聚合
    usage_data = defaultdict(lambda: {"input": 0, "output": 0, "total": 0})
    all_models = set()
    
    # 遍歷所有 agent 的 sessions
    if not agents_dir.exists():
        print("❌ agents 目錄不存在")
        return {}, set()
    
    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.exists():
            continue
        
        # 找到所有 jsonl 文件
        jsonl_files = list(sessions_dir.glob("*.jsonl"))
        print(f"📂 {agent_dir.name}: {len(jsonl_files)} sessions")
        
        for session_file in jsonl_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            
                            # 只處理 message 類型
                            if entry.get("type") != "message":
                                continue
                            
                            msg = entry.get("message", {})
                            usage = msg.get("usage", {})
                            
                            # 必須有 usage 數據
                            if not usage:
                                continue
                            
                            total_tokens = usage.get("totalTokens", 0)
                            if total_tokens == 0:
                                continue
                            
                            # 提取日期
                            timestamp = entry.get("timestamp", "")
                            if not timestamp or timestamp < start_date:
                                continue
                            
                            date = timestamp[:10]  # YYYY-MM-DD
                            
                            # 提取模型名稱
                            model = msg.get("model")
                            if not model:
                                continue
                            
                            # 標準化
                            model = normalize_model(model)
                            if not model:
                                continue
                            
                            all_models.add(model)
                            
                            # 累加
                            key = (date, model)
                            usage_data[key]["input"] += usage.get("input", 0)
                            usage_data[key]["output"] += usage.get("output", 0)
                            usage_data[key]["total"] += total_tokens
                            
                        except (json.JSONDecodeError, KeyError):
                            continue
            except Exception as e:
                print(f"   ⚠️ 讀取錯誤: {e}")
                continue
    
    return usage_data, all_models

def generate_stats(usage_data, all_models):
    """生成統計數據"""
    # 按日期排序
    daily_usage = []
    for (date, model), data in sorted(usage_data.items(), key=lambda x: x[0]):
        daily_usage.append({
            "date": date,
            "model": model,
            "input": data["input"],
            "output": data["output"],
            "total": data["total"]
        })
    
    # 模型統計
    model_stats = defaultdict(lambda: {"totalInput": 0, "totalOutput": 0})
    for entry in daily_usage:
        model_stats[entry["model"]]["totalInput"] += entry["input"]
        model_stats[entry["model"]]["totalOutput"] += entry["output"]
    
    model_stats_list = [
        {
            "model": model,
            "totalInput": data["totalInput"],
            "totalOutput": data["totalOutput"],
            "total": data["totalInput"] + data["totalOutput"]
        }
        for model, data in model_stats.items()
    ]
    model_stats_list.sort(key=lambda x: x["total"], reverse=True)
    
    return {
        "dailyUsage": daily_usage,
        "modelStats": model_stats_list,
        "allModels": sorted(list(all_models))
    }

def main():
    print("=" * 50)
    print("🔢 Token Usage Collector - 全新版本")
    print("=" * 50)
    print()
    
    # 確保目錄存在
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 收集數據
    print("🔍 掃描 session 文件...")
    usage_data, all_models = collect_token_usage()
    
    print(f"\n📊 找到 {len(usage_data)} 條記錄")
    print(f"📋 發現 {len(all_models)} 個模型: {', '.join(sorted(all_models))}")
    
    if not usage_data:
        print("❌ 沒有找到任何 token 使用數據")
        return
    
    # 生成統計
    stats = generate_stats(usage_data, all_models)
    
    # 讀取現有數據（只保留非每日用量的部分）
    existing = {}
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE) as f:
                existing = json.load(f)
        except:
            pass
    
    # 合併
    result = {
        "updated": datetime.now().isoformat(),
        "sessionStart": existing.get("sessionStart", {"estimatedTokens": 7000}),
        "cronJobs": existing.get("cronJobs", []),
        "dailyUsage": stats["dailyUsage"],
        "modelStats": stats["modelStats"],
        "allModels": stats["allModels"]
    }
    
    # 寫入
    with open(TOKEN_FILE, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已更新 tokens.json")
    
    # 顯示統計
    print("\n📈 模型使用排名:")
    for i, m in enumerate(result["modelStats"][:10], 1):
        print(f"   {i}. {m['model']}: {m['total']/1000:.1f}K tokens")
    
    print("\n✅ 完成!")

if __name__ == "__main__":
    main()
