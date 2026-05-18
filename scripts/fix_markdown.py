import re
import os
import sys

LIGHTNING_WIDGET = """
---

### Tips and Donations

If you enjoyed this deep dive, consider supporting the project with a tip in **Sats**. It's a simple, global way to support independent research.

<lightning-widget
  name='Thanks for supporting the publication'
  accent='#f9ce00'
  to='shutosha@primal.net'
  image='https://nostrcheck.me/media/5af0794606a15b5641e25aa23d04af4cb0d7d5e68b11cacb47e56a4698fca8c4/49ff6d00cb5bc819cd19f77783d4815fbd46a5b99b6fbdead1eaecfab798187b.webp'
/>
<script src='https://embed.twentyuno.net/js/app.js'></script>

To send Sats, you'll need a [lightning wallet](https://lightningaddress.com/). 

---
"""

KATEX_MAP = {
    "![][image1]": r"$\mathcal{P} = (\mathcal{S}, \mathcal{A}, \rho, \mathcal{R})$",
    "![][image2]": r"$\mathcal{S}$",
    "![][image3]": r"$\mathcal{A}$",
    "![][image4]": r"$\rho$",
    "![][image5]": r"$\mathcal{R}$",
    "![][image6]": r"$G_N$",
    "![][image7]": r"$SU(3) \times SU(2) \times U(1)$",
    "![][image8]": r"$S^2$",
    "![][image9]": r"$SL(2, \mathbb{C})$",
    "![][image10]": r"$SO(3,1)$",
    "![][image11]": r"$10^{120}$",
    "![][image12]": r"$T_{\mu\nu} l^\mu l^\nu = 0$",
}

EPISODE_229_MAP = {
    "![][image1]": r"$E = mc^2$",
    "![][image2]": r"$10-15$",
    "![][image3]": r"$100$",
    "![][image4]": r"$500-1000$",
    "![][image5]": r"$I$",
    "![][image6]": r"$\eta$",
    "![][image7]": r"$E$",
    "![][image8]": r"$\Delta S$",
    "![][image9]": r"$$I = \eta \frac{\Delta S \cdot k_B T}{E}$$",
    "![][image10]": r"$\Delta S$",
    "![][image11]": r"$T$",
    "![][image12]": r"$W \ge k_B T \ln 2$",
    "![][image13]": r"$$T = \kappa E$$",
    "![][image14]": r"$\kappa$",
    "![][image15]": r"$E$",
    "![][image16]": r"$2E/\pi\hbar$",
    "![][image17]": r"$E = mc^2$",
    "![][image18]": r"$10^{50}$",
    "![][image19]": r"$L$",
    "![][image20]": r"$C$",
    "![][image21]": r"$N$",
    "![][image22]": r"$1/C^\alpha$",
    "![][image23]": r"$1/N^\beta$",
    "![][image24]": r"$1/D^\gamma$",
    "![][image25]": r"$\rho_s$",
    "![][image26]": r"$P_s$",
    "![][image27]": r"$\mathcal{M}$",
    "![][image28]": r"$G_{\mu\nu}$",
    "![][image29]": r"$$G_{\mu\nu} + \Lambda g_{\mu\nu} = \kappa T_{\mu\nu}$$",
    "![][image30]": r"$a$",
    "![][image31]": r"$\Phi$",
    "![][image32]": r"$4 \times 10^{26}$",
    "![][image33]": r"$$I \propto \frac{\Delta S}{E}$$"
}

EPISODE_230_MAP = {
    "![][image1]": r"$mNAV < 1$"
}

EPISODE_234_MAP = {
    "![][image1]": r"$P = F \left(1 - \frac{d \cdot t}{360}\right)$"
}

def extract_episode(filename):
    m = re.match(r'^(\d+)\.md$', filename)
    if m:
        val = int(m.group(1))
        if val < 1000: return str(val)
    return None

def fix_footnotes(content):
    # Split body and references
    parts = re.split(r'(#### \*\*Works cited\*\*|#### \*\*References\*\*)', content, flags=re.IGNORECASE)
    if len(parts) < 3: return content
    
    header = parts[1]
    refs_raw = parts[2]
    body = parts[0]
    
    # 1. Extract all existing definitions from the references section
    ref_list = [] # Keep order
    ref_map = {}
    
    # Match "1. Text" or "[^1]: Text"
    # We use a more careful extraction to preserve the full entry including sub-lines
    raw_entries = re.split(r'\n(?=\d+\.\s+|\[\^\d+\]:\s+)', refs_raw.strip())
    for entry in raw_entries:
        m = re.match(r'^(\[?\^?(\d+)\]?[:.]?)\s*(.*)', entry.strip(), re.DOTALL)
        if m:
            num = m.group(2)
            text = m.group(3).strip()
            if num not in ref_map:
                ref_map[num] = text
                ref_list.append((num, text))

    if not ref_map: return content
    
    # 2. Identify potential footnote markers in the body
    def marker_replacer(match):
        punct = match.group(1)
        nums_str = match.group(2)
        parts = re.split(r'[\s,]+', nums_str)
        markers = []
        for p in parts:
            if not p: continue
            markers.append(f"[^{p}]")
        return f"{punct}{''.join(markers)}"

    # Convert ".5" to ".[^5]"
    body = re.sub(r'([.,;")\]])(\d+(?:[\s,]+\d+)*)(?![.\d])', marker_replacer, body)
    
    # 3. Collect all markers used in the body
    used_markers = re.findall(r'\[\^(\d+)\]', body)
    unique_used = []
    for m in used_markers:
        if m not in unique_used:
            unique_used.append(m)
    
    # 4. Create a sequential mapping
    final_map = {} # old_num -> new_num
    final_refs = [] # (new_num, text)
    
    # First, map the ones actually used in the body
    for i, old_num in enumerate(unique_used):
        new_num = str(i + 1)
        # If we have a definition for this old_num, use it. 
        # Otherwise, if it's "5" and we have entry index 4, maybe use that?
        # For simplicity, if old_num in map, use it. 
        # If not, try to find an unused definition.
        if old_num in ref_map:
            text = ref_map[old_num]
        elif i < len(ref_list):
            text = ref_list[i][1]
        else:
            text = "Missing citation"
        
        final_map[old_num] = new_num
        final_refs.append((new_num, text))
        
        # Mark this definition as "accounted for"
        if old_num in ref_map:
            del ref_map[old_num]
        # Also remove from ref_list if possible
        ref_list = [item for item in ref_list if item[1] != text]

    # 5. Replace markers in body
    def final_body_repl(match):
        old_num = match.group(1)
        return f"[^{final_map.get(old_num, old_num)}]"
    
    body = re.sub(r'\[\^(\d+)\]', final_body_repl, body)

    # 6. Reconstruct references section, including leftovers
    new_refs = [f"\n\n{header}\n"]
    for num, text in final_refs:
        new_refs.append(f"[^{num}]: {text}\n")
    
    # Add leftovers that weren't referenced in body as a simple list to avoid warnings
    for i, (_, text) in enumerate(ref_list):
        new_refs.append(f"{len(final_refs) + i + 1}. {text}\n")

    return body + "".join(new_refs)

def process_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(file_path)
    ep_num = extract_episode(filename)
    
    # Ensure H1 title matches the episode number
    if ep_num:
        # Match any H1: '# Title', '# **Title**', '# 123 : Title', etc.
        # Group 1: Optional old number and colon
        # Group 2: The actual title text (potentially with bold markers)
        pattern = r'^#\s*(?:\d+\s*:\s*)?\s*(\*\*)?(.*?)\1\s*$'
        def title_repl(match):
            title_text = match.group(2).strip()
            return f'# {ep_num} : {title_text}'
        
        content = re.sub(pattern, title_repl, content, flags=re.MULTILINE)

    content = content.replace('\u0332', '')
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
    content = re.sub(r'(\\)([_.-])', r'\2', content)

    math_blocks = []
    def save_math(match):
        math_blocks.append(match.group(0))
        return f"__MATH_BLOCK_{len(math_blocks)-1}__"
    
    content = re.sub(r'\$\$.*?\$\$', save_math, content, flags=re.DOTALL)
    content = re.sub(r'\$.*?\$', save_math, content)
    
    content = fix_footnotes(content)

    content = re.sub(r'\$([\d\.,]+)\s*(million|billion|trillion|k|m|b|t)?(?=[^0-9\^]|$)', r'\1 \2 USD ', content, flags=re.IGNORECASE)
    content = content.replace('  ', ' ')
    content = content.replace('$', r'\$')
    
    cur_map = KATEX_MAP
    if ep_num == "229": cur_map = EPISODE_229_MAP
    elif ep_num == "230": cur_map = EPISODE_230_MAP
    elif ep_num == "234": cur_map = EPISODE_234_MAP
    for placeholder, symbol in cur_map.items():
        content = content.replace(placeholder, symbol)

    for idx, block in enumerate(math_blocks):
        content = content.replace(f"__MATH_BLOCK_{idx}__", block)

    if "lightning-widget" not in content:
        content = content.strip() + "\n" + LIGHTNING_WIDGET

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed markdown for {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_markdown.py <episode_number_or_file_path>")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    if input_arg.isdigit():
        file_path = f"src/{input_arg}.md"
        if not os.path.exists(file_path) and os.path.exists(f"deepDive/src/{input_arg}.md"):
            file_path = f"deepDive/src/{input_arg}.md"
    else:
        file_path = input_arg
        
    process_markdown(file_path)
