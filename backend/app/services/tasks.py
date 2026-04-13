def calculate_progress(current: int, total: int) -> float:
    percent = int(current / total * 100) if total > 0 else 0
    return {
        "current": current,
        "total": total,
        "percent": percent,
    }
