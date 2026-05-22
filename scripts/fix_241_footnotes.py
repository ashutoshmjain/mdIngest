import re
import sys

def fix_footnotes(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize header
    content = re.sub(r'## Bibliography', '#### **Works cited**', content, flags=re.IGNORECASE)

    # Split into body and references
    parts = re.split(r'#### \*\*Works cited\*\*', content, flags=re.IGNORECASE)
    if len(parts) < 2:
        print("Works cited section not found.")
        return

    body = parts[0]
    refs_raw = parts[1]

    # Parse existing references
    # Pattern to match: *  **[1]** text OR *  **** text
    # We'll use a more flexible regex
    ref_pattern = re.compile(r'^\*?\s*(\*\*\[?(\d+)\]?\*\*|\*\*\*\*)\s*', re.MULTILINE)
    
    matches = list(ref_pattern.finditer(refs_raw))
    ref_entries = []
    for i, match in enumerate(matches):
        num = match.group(2) # None if ****
        start = match.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(refs_raw)
        text = refs_raw[start:end].strip()
        ref_entries.append({'old_num': num, 'text': text})

    if not ref_entries:
        print("No references found in raw text.")
        return

    # Find all citation markers in the body: [1], [1, 2], [5, 17]
    marker_pattern = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')
    
    unique_old_nums = []
    def collect_nums(match):
        nums = [n.strip() for n in match.group(1).split(',')]
        for n in nums:
            if n not in unique_old_nums:
                unique_old_nums.append(n)
        return match.group(0)

    marker_pattern.sub(collect_nums, body)

    # Create mapping from old_num to new_num
    old_to_new = {}
    new_refs = []
    
    # Track used references to avoid duplicates
    unprocessed_star_refs = [r for r in ref_entries if r['old_num'] is None]
    
    for old_num in unique_old_nums:
        # Find the reference text for this old_num
        ref = next((r for r in ref_entries if r['old_num'] == old_num and not r.get('processed')), None)
        if ref:
            new_num = str(len(new_refs) + 1)
            old_to_new[old_num] = new_num
            new_refs.append(ref['text'])
            ref['processed'] = True
        else:
            # Check if there are any **** entries we can consume
            if unprocessed_star_refs:
                unprocessed_star = unprocessed_star_refs.pop(0)
                new_num = str(len(new_refs) + 1)
                old_to_new[old_num] = new_num
                new_refs.append(unprocessed_star['text'])
                unprocessed_star['processed'] = True
            else:
                new_num = str(len(new_refs) + 1)
                old_to_new[old_num] = new_num
                new_refs.append(f"Missing citation for index {old_num}")

    # Add remaining references that weren't cited in the body
    for ref in ref_entries:
        if not ref.get('processed'):
            new_refs.append(ref['text'])

    # Update body markers
    def replace_nums(match):
        nums = [n.strip() for n in match.group(1).split(',')]
        new_nums = [old_to_new.get(n, n) for n in nums]
        return "".join([f"[^{n}]" for n in new_nums]) 

    new_body = marker_pattern.sub(replace_nums, body)
    
    # Reconstruct the file
    new_content = new_body.strip() + "\n\n#### **Works cited**\n\n"
    for i, text in enumerate(new_refs):
        new_content += f"[^{i+1}]: {text}\n"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    fix_footnotes(sys.argv[1])
