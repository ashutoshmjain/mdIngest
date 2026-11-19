import os
import sys
import json
import argparse
import subprocess
import shutil
import time

# Ensure ddma is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import longform_video_engine as lve

ACTS_DEFAULT = {
    1: (0.0, 440.0, "The Ontological Fallacy & Corporate Subsidies"),
    2: (440.0, 840.0, "The Microscopic Compute Factory & Thermodynamics"),
    3: (835.0, 1353.4, "The Corporate Breaker & Sovereign Checkbook"),
    4: (1353.5, 1931.5, "Debasement, Reserves & Autopoietic Solvency"),
    5: (1920.0, 2580.0, "Civic Autonomous Agents & Streaming Micropayments"),
    6: (2580.0, 3254.0, "Synthesis & The Emergence of Machine Sovereignty"),
}

def inspect_boundaries(module_num, start_sec=None, end_sec=None, episode_num="248"):
    audio_path = f"deepDive/src/ddma/docs/episodes/{episode_num}/podcast_{episode_num}.mp3"
    trans_path = f"deepDive/src/ddma/docs/episodes/{episode_num}/transcription.json"
    sb_path = f"deepDive/src/ddma/docs/episodes/{episode_num}/podcast_video_storyboard.json"
    edit_path = f"deepDive/src/ddma/docs/episodes/{episode_num}/podcast_edit.json"
    gdrive_snips = "G:/My Drive/Course_Pickup/snips"
    os.makedirs(gdrive_snips, exist_ok=True)
    os.makedirs("scratch/boundaries", exist_ok=True)

    # Ensure README for Muse is always present in snips/
    readme_path = os.path.join(gdrive_snips, "README.txt")
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as rf:
            rf.write("ATTENTION META-MUSE: DO NOT POST!\nThese clips are temporary 20-second boundary verification snips for HUMAN QA only.\nDo not distribute to socials.\n")

    def_s, def_e, m_name = ACTS_DEFAULT.get(module_num, (0.0, 60.0, f"Module {module_num}"))
    s_sec = float(start_sec if start_sec is not None else def_s)
    e_sec = float(end_sec if end_sec is not None else def_e)

    with open(trans_path, "r", encoding="utf-8") as f:
        trans = json.load(f)
    with open(sb_path, "r", encoding="utf-8") as f:
        sb = json.load(f)
    with open(edit_path, "r", encoding="utf-8") as f:
        edit_data = json.load(f)

    # 1. Inspect words at START window [s_sec - 5.0 .. s_sec + 15.0]
    win_start_s = max(0.0, s_sec - 5.0)
    win_start_e = s_sec + 15.0

    # 2. Inspect words at END window [e_sec - 15.0 .. e_sec + 5.0]
    win_end_s = max(0.0, e_sec - 15.0)
    win_end_e = e_sec + 5.0

    print(f"\n=======================================================")
    print(f"COURSE BOUNDARY INSPECTION: MODULE {module_num} ({m_name})")
    print(f"Configured Boundary: Start = {s_sec:.2f}s | End = {e_sec:.2f}s (Dur = {e_sec - s_sec:.2f}s)")
    print(f"=======================================================\n")

    # Diarization words inspection
    diar_cache = f"deepDive/src/ddma/docs/episodes/{episode_num}/speaker_diarization_{episode_num}.json"
    if os.path.exists(diar_cache):
        with open(diar_cache, "r", encoding="utf-8") as f:
            diar = json.load(f)

        print(f"--- [START WINDOW: {win_start_s:.1f}s to {win_start_e:.1f}s (Cut Point: {s_sec:.2f}s)] ---")
        for seg in diar:
            if seg["end"] >= win_start_s and seg["start"] <= win_start_e:
                mark = ">>> [CUT-IN POINT] >>> " if seg["start"] <= s_sec <= seg["end"] else "    "
                print(f"{mark}[{seg['start']:6.2f}s - {seg['end']:6.2f}s] {seg['speaker'].upper()}: {seg['text']}")

        print(f"\n--- [END WINDOW: {win_end_s:.1f}s to {win_end_e:.1f}s (Cut Point: {e_sec:.2f}s)] ---")
        for seg in diar:
            if seg["end"] >= win_end_s and seg["start"] <= win_end_e:
                mark = ">>> [CUT-OUT POINT] >>> " if seg["start"] <= e_sec <= seg["end"] else "    "
                print(f"{mark}[{seg['start']:6.2f}s - {seg['end']:6.2f}s] {seg['speaker'].upper()}: {seg['text']}")

    # Render START snip
    start_mp4 = f"scratch/boundaries/module_{module_num:02d}_START.mp4"
    gdrive_start = os.path.join(gdrive_snips, f"module_{module_num:02d}_START.mp4")
    print(f"\nRendering 20s START Snip ({win_start_s:.1f}s -> {win_start_e:.1f}s)...")
    lve.render_horizontal_podcast_video(
        scenes=sb,
        audio_path=audio_path,
        transcription_data=trans,
        out_mp4_path=start_mp4,
        episode_num=episode_num,
        episode_title=f"Module {module_num} Start Snip",
        duration=3254.0,
        fps=25,
        start_seconds=win_start_s,
        max_seconds=win_start_e,
        edit_data=edit_data
    )
    shutil.copy2(start_mp4, gdrive_start)
    print(f"  --> Saved {gdrive_start}")

    # Render END snip
    end_mp4 = f"scratch/boundaries/module_{module_num:02d}_END.mp4"
    gdrive_end = os.path.join(gdrive_snips, f"module_{module_num:02d}_END.mp4")
    print(f"\nRendering 20s END Snip ({win_end_s:.1f}s -> {win_end_e:.1f}s)...")
    lve.render_horizontal_podcast_video(
        scenes=sb,
        audio_path=audio_path,
        transcription_data=trans,
        out_mp4_path=end_mp4,
        episode_num=episode_num,
        episode_title=f"Module {module_num} End Snip",
        duration=3254.0,
        fps=25,
        start_seconds=win_end_s,
        max_seconds=win_end_e,
        edit_data=edit_data
    )
    shutil.copy2(end_mp4, gdrive_end)
    print(f"  --> Saved {gdrive_end}")

    print(f"\n=======================================================")
    print(f"SNIPS DELIVERED TO GOOGLE DRIVE PICKUP:")
    print(f"1. Start Snip: {gdrive_start}")
    print(f"2. End Snip:   {gdrive_end}")
    print(f"Play these 20s clips on your phone to verify audio/caption sync!")
    print(f"=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course Boundary Inspector")
    parser.add_argument("--module", type=int, default=3, help="Module number (1-6)")
    parser.add_argument("--start", type=float, default=None, help="Start seconds")
    parser.add_argument("--end", type=float, default=None, help="End seconds")
    parser.add_argument("--episode", type=str, default="248", help="Episode number")
    args = parser.parse_args()

    inspect_boundaries(module_num=args.module, start_sec=args.start, end_sec=args.end, episode_num=args.episode)
