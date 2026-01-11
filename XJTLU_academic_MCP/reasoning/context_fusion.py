def fuse_contexts(memory_snapshot: dict) -> dict:
    fused = {}
    for agent, data in memory_snapshot.items():
        fused[agent] = data
    return fused
