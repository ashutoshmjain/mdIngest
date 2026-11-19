import json
import os

plan_paths = [
    "projects/episode_247/plan.json",
    "plan.json",
    "docs/plan.json",
    "docs/episodes/247/plan.json"
]

def calculate_clip_audio_duration(clip):
    total = 0.0
    segs = clip.get("segments", [])
    if segs:
        for idx, seg in enumerate(segs):
            total += float(seg.get("duration", 0.0))
            if idx < len(segs) - 1:
                total -= float(seg.get("crossfade", 0.0))
    else:
        total = float(clip.get("end", 0.0)) - float(clip.get("start", 0.0))
    return max(0.0, total)

for p in plan_paths:
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        clips = json.load(f)
    
    modified_count = 0
    for c in clips:
        num = c.get("num")
        segs = c.get("segments", [])
        if num >= 4 and segs and segs[0].get("type") == "music":
            # Remove leading music segment
            removed = segs.pop(0)
            
            # If the new first segment is audio, update clip start
            audio_segs = [s for s in segs if s.get("type") == "audio"]
            if audio_segs:
                c["start"] = audio_segs[0]["start"]
            
            # Recalculate duration
            c["duration"] = round(calculate_clip_audio_duration(c), 2)
            modified_count += 1
            
    with open(p, "w", encoding="utf-8") as f:
        json.dump(clips, f, indent=2)
    print(f"Updated {p}: modified {modified_count} clips.")
