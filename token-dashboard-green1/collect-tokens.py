#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone, timedelta

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
OUTPUT_DIR = Path.home() / ".openclaw" / "workspace" / "token-dashboard-green1" / "data"
LOOKBACK_DAYS = 3650


def iso_to_date(iso_str: str):
    if not iso_str or len(iso_str) < 10:
        return None
    return iso_str[:10]


def get_week_start(date_str: str):
    dt = datetime.fromisoformat(date_str)
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def get_month_key(date_str: str):
    return date_str[:7]


def blank_usage():
    return {"input": 0, "output": 0, "total": 0, "count": 0}


def add_usage(bucket, usage):
    bucket["input"] += int(usage.get("input", 0) or 0)
    bucket["output"] += int(usage.get("output", 0) or 0)
    bucket["total"] += int(usage.get("totalTokens", 0) or 0)
    bucket["count"] += 1


def collect():
    start_date = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    daily_total = defaultdict(blank_usage)
    weekly_total = defaultdict(blank_usage)
    monthly_total = defaultdict(blank_usage)

    daily_by_model = defaultdict(blank_usage)
    weekly_by_model = defaultdict(blank_usage)
    monthly_by_model = defaultdict(blank_usage)
    lifetime_by_model = defaultdict(blank_usage)
    lifetime_by_provider = defaultdict(blank_usage)

    total_sessions = 0
    total_messages = 0
    parse_errors = 0
    providers = set()
    models = set()

    session_files = sorted(SESSIONS_DIR.glob("*.jsonl"))
    total_sessions = len(session_files)

    for session_file in session_files:
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                    except Exception:
                        parse_errors += 1
                        continue

                    if entry.get("type") != "message":
                        continue

                    total_messages += 1
                    msg = entry.get("message", {})
                    usage = msg.get("usage", {})
                    total_tokens = int(usage.get("totalTokens", 0) or 0)
                    if total_tokens <= 0:
                        continue

                    provider = msg.get("provider") or "unknown"
                    model = msg.get("model") or "unknown"
                    date = iso_to_date(entry.get("timestamp", ""))
                    if not date or date < start_date:
                        continue

                    providers.add(provider)
                    models.add(f"{provider}/{model}")
                    model_key = (provider, model)

                    add_usage(daily_total[date], usage)
                    add_usage(weekly_total[get_week_start(date)], usage)
                    add_usage(monthly_total[get_month_key(date)], usage)

                    add_usage(daily_by_model[(date, *model_key)], usage)
                    add_usage(weekly_by_model[(get_week_start(date), *model_key)], usage)
                    add_usage(monthly_by_model[(get_month_key(date), *model_key)], usage)
                    add_usage(lifetime_by_model[model_key], usage)
                    add_usage(lifetime_by_provider[provider], usage)
        except Exception:
            parse_errors += 1
            continue

    def sort_period_dict(d):
        return [{"period": k, **v} for k, v in sorted(d.items(), key=lambda kv: kv[0], reverse=True)]

    def sort_model_period_dict(d):
        rows = []
        for (period, provider, model), values in d.items():
            rows.append({"period": period, "provider": provider, "model": model, "modelKey": f"{provider}/{model}", **values})
        rows.sort(key=lambda x: (x["period"], x["total"], x["modelKey"]), reverse=True)
        return rows

    model_rows = []
    for (provider, model), values in lifetime_by_model.items():
        model_rows.append({"provider": provider, "model": model, "modelKey": f"{provider}/{model}", **values})
    model_rows.sort(key=lambda x: (x["total"], x["count"], x["modelKey"]), reverse=True)

    provider_rows = []
    for provider, values in lifetime_by_provider.items():
        provider_rows.append({"provider": provider, **values})
    provider_rows.sort(key=lambda x: (x["total"], x["provider"]), reverse=True)

    grand_total = sum(x["total"] for x in model_rows)
    grand_input = sum(x["input"] for x in model_rows)
    grand_output = sum(x["output"] for x in model_rows)
    active_days = len(daily_total)

    result = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "agent": "main",
            "label": "小綠1號",
            "source": str(SESSIONS_DIR),
            "lookbackDays": LOOKBACK_DAYS,
            "note": "Read-only analysis of main session JSONL logs."
        },
        "summary": {
            "grandTotal": grand_total,
            "grandInput": grand_input,
            "grandOutput": grand_output,
            "totalSessions": total_sessions,
            "totalMessages": total_messages,
            "uniqueProviders": len(providers),
            "uniqueModels": len(model_rows),
            "activeDays": active_days,
            "parseErrors": parse_errors
        },
        "daily": {
            "total": sort_period_dict(daily_total),
            "byModel": sort_model_period_dict(daily_by_model)
        },
        "weekly": {
            "total": sort_period_dict(weekly_total),
            "byModel": sort_model_period_dict(weekly_by_model)
        },
        "monthly": {
            "total": sort_period_dict(monthly_total),
            "byModel": sort_model_period_dict(monthly_by_model)
        },
        "models": model_rows,
        "providers": provider_rows
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "tokens.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"wrote {OUTPUT_DIR / 'tokens.json'}")
    print(f"models={len(model_rows)} providers={len(provider_rows)} total={grand_total}")


if __name__ == "__main__":
    collect()
