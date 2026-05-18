import re
import os
import sys

VIDEO_TEMPLATE = """
<center>
<div style="position: relative; max-width: 800px; margin: 20px 0;">
  <video width="100%" height="auto" autoplay loop muted playsinline style="border-radius: 10px; display: block; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    <source src="vid/{filename}" type="video/mp4">
  </video>
  <button onclick="var v = this.previousElementSibling; v.muted = !v.muted; this.querySelector('i').className = v.muted ? 'fa fa-volume-off' : 'fa fa-volume-up';" 
          style="position: absolute; bottom: 15px; right: 15px; background: rgba(46, 46, 46, 0.7); border: none; color: white; border-radius: 5px; padding: 5px 10px; cursor: pointer; z-index: 10;"
          title="Toggle Mute">
    <i class="fa fa-volume-off"></i>
  </button>
</div>
</center>
"""

def process_vids(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match [vid: filename.mp4] or [vid:filename.mp4]
    def video_replacer(match):
        filename = match.group(1).strip()
        # Ensure it has .mp4 extension if not provided
        if not filename.endswith('.mp4'):
            filename += '.mp4'
        return VIDEO_TEMPLATE.format(filename=filename)

    new_content = re.sub(r'\[vid:\s*(.*?)\]', video_replacer, content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Expanded video markers in {file_path}")
    else:
        print(f"No video markers found in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_vids.py <episode_number_or_file_path>")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    # If it's a number, resolve to src/[number].md
    if input_arg.isdigit():
        file_path = f"src/{input_arg}.md"
        # If running from the root of the project, check if deepDive/src exists
        if not os.path.exists(file_path) and os.path.exists(f"deepDive/src/{input_arg}.md"):
            file_path = f"deepDive/src/{input_arg}.md"
    else:
        file_path = input_arg
        
    process_vids(file_path)
