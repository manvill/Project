import time

def time_ago(timestamp):
    delta = time.time() - timestamp
    if delta < 60:
        return f"{int(delta)}s ago"
    elif delta < 3600:
        return f"{int(delta // 60)}m ago"
    elif delta < 86400:
        return f"{int(delta // 3600)}h ago"
    else:
        return f"{int(delta // 86400)}d ago"