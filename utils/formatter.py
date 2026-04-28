def human_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.1f} {units[i]}"


def human_speed(speed_bytes_per_sec: float) -> str:
    if speed_bytes_per_sec <= 0:
        return "0 B/s"
    return human_size(int(speed_bytes_per_sec)) + "/s"


def human_eta(seconds: float) -> str:
    if seconds <= 0 or seconds > 1e6:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    return f"{s}s"