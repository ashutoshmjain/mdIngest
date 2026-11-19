"""
Test script to run manim_infographic_engine on Episode 248 Clip 1
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import manim_infographic_engine

def main():
    plan_path = "projects/episode_248/plan.json"
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    clip = plan[0]
    audio_path = "clips/248-1-Ai Autonomy.mp3"
    out_mp4 = "clips/test_248_1_manim_infographic.mp4"
    body_dur = clip.get("audio_duration") or 125.76

    print(f"Generating pedagogical storyboard for Clip {clip['num']}: {clip['title']} ({body_dur:.2f}s)...")
    scenes = manim_infographic_engine.generate_pedagogical_storyboard(
        clip, body_duration=body_dur, force_regenerate=True
    )
    print(f"Generated {len(scenes)} scenes:")
    for s in scenes:
        print(f"  [{s['start']:.1f}s - {s['end']:.1f}s] {s['title']} ({s['archetype']}): {s.get('metaphor')}")

    print("\nRendering 1080x1080 Manim video...")
    res = manim_infographic_engine.render_manim_infographic_mp4(
        scenes, audio_path, out_mp4, duration=body_dur
    )
    print("Render complete! Output:", res)

if __name__ == "__main__":
    main()
