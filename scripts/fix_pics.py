import re
import os
import sys

PODCAST_LINKS = '<center><a href="https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Spotify</a><a href="https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Apple Podcasts</a><a href="https://music.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe&si=o534zFZsc7p5XA9Q" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">YouTube Music</a><a href="https://www.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">YouTube</a><a href="https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">Fountain.fm</a></center>'

def extract_episode(filename):
    m = re.match(r'^(\d+)\.md$', filename)
    if m:
        val = int(m.group(1))
        if val < 1000: return str(val)
    return None

def extract_title(file_path):
    if not os.path.exists(file_path): return os.path.basename(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^#{1,2}\s+(?:\d+\s*[:\-]\s*)?(.*?)$', line.strip())
            if m: return m.group(1).strip().replace('**', '')
    return os.path.basename(file_path)

def update_summary(target_file_path):
    summary_path = 'src/SUMMARY.md'
    if not os.path.exists(summary_path): return
    with open(summary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    all_src_files = [f for f in os.listdir('src') if f.endswith('.md') and f not in ['SUMMARY.md', 'cover.md']]
    file_to_info = {}
    for fname in all_src_files:
        title = extract_title(os.path.join('src', fname))
        ep = extract_episode(fname)
        file_to_info[fname] = {"title": title, "ep": ep}

    new_lines = ["# Summary\n", "\n", "- [Deep Dive with Gemini](./cover.md)\n", "\n", "# Recent ..\n"]
    numbered = sorted([f for f in file_to_info if file_to_info[f]["ep"]], key=lambda x: int(file_to_info[x]["ep"]), reverse=True)
    for f in numbered:
        new_lines.append(f"- [{file_to_info[f]['ep']} : {file_to_info[f]['title']}](././{f})\n")
    
    categories = {}
    current_cat = None
    for line in lines:
        if line.startswith("# ") and "Summary" not in line and "Recent .." not in line:
            current_cat = line.strip()
            if current_cat not in categories: categories[current_cat] = []
        elif line.strip().startswith("- [") and current_cat:
            m = re.search(r'\[(.*?)\]\(\.\/(.*?)\)', line)
            if m:
                fname = m.group(2).replace("./", "")
                if fname in file_to_info and not file_to_info[fname]["ep"]:
                    if line.strip() not in categories[current_cat]:
                        categories[current_cat].append(line.strip())

    for cat in ["# The Bitcoin Standard & Sovereign Assets", "# The AI Revolution & Machine Intelligence", 
                "# Digital Credit & The STRC Bridge", "# Economics, Capital & The Global Shift", 
                "# Philosophy, Science & The Nature of Reality", "# Social, Culture & Digital Sovereignty"]:
        if cat in categories and categories[cat]:
            new_lines.append(f"\n{cat}\n")
            for item in categories[cat]:
                new_lines.append(f"{item}\n")
            del categories[cat]
            
    for cat, items in categories.items():
        if items:
            new_lines.append(f"\n{cat}\n")
            for item in items:
                new_lines.append(f"{item}\n")

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("".join(new_lines))

def process_pics(file_path, title_override=None):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    filename = os.path.basename(file_path)
    ep_num = extract_episode(filename)
    if not ep_num:
        print(f"Skipping {file_path}: No episode number found in filename.")
        return

    title = ""
    for i, line in enumerate(lines):
        m = re.match(r'^(#{1,2})\s+(?:\d+\s*[:\-]\s*)?(.*?)$', line.strip())
        if m:
            if title_override:
                if not re.match(r'^\d+\s*[:\-]', title_override):
                    full_title = f"{ep_num} : {title_override}"
                else:
                    full_title = title_override
                title = re.sub(r'^\d+\s*[:\-]\s*', '', full_title).strip()
            else:
                raw_title = m.group(2).strip().replace('**', '')
                words = raw_title.split()
                limit = 5
                while limit > 1 and words[limit-1].lower() in ['the', 'of', 'a', 'an', 'in', 'on', 'at', 'by', 'for', 'with', 'about', 'to']:
                    limit -= 1
                title = " ".join(words[:limit])
                full_title = f"{ep_num} : {title}"
            
            lines[i] = f"# {full_title}\n"
            image_path = f"img/{ep_num}.png"
            new_header = [lines[i], "\n", f"![{title}]({image_path})\n", "\n", PODCAST_LINKS, "\n\n"]
            
            # Text before the header
            pre_header_text = lines[:i]
            
            j = i + 1
            while j < len(lines) and (lines[j].strip() == "" or lines[j].startswith('![') or '<center>' in lines[j]):
                j += 1
            
            # Combine everything: New header at top, then pre-header text, then the rest
            lines = new_header + pre_header_text + lines[j:]
            break

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    update_summary(file_path)
    print(f"Processed pics and updated summary for {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_pics.py <episode_number_or_file_path> [--title 'Title']")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    if input_arg.isdigit():
        file_path = f"src/{input_arg}.md"
        if not os.path.exists(file_path) and os.path.exists(f"deepDive/src/{input_arg}.md"):
            file_path = f"deepDive/src/{input_arg}.md"
    else:
        file_path = input_arg
    
    override = None
    if "--title" in sys.argv:
        idx = sys.argv.index("--title")
        if idx + 1 < len(sys.argv):
            override = sys.argv[idx+1]
            
    process_pics(file_path, title_override=override)
