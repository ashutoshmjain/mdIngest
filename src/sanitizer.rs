use regex::Regex;
use once_cell::sync::Lazy;
use std::collections::HashMap;

static KATEX_MAP: Lazy<HashMap<&'static str, &'static str>> = Lazy::new(|| {
    let mut m = HashMap::new();
    m.insert("![][image1]", r"$10^{500}$");
    m.insert("![][image2]", r"$\mathbb{O}$");
    m.insert("![][image3]", r"$\mathbb{H}$");
    m.insert("![][image4]", r"$\mathbb{C}$");
    m.insert("![][image5]", r"$\mathbb{R}$");
    m.insert("![][image7]", r"$(SU(3) \times SU(2) \times U(1))$");
    m.insert("![][image8]", r"$\mathbb{O}$");
    m.insert("![][image9]", r"$SL(2, \mathbb{C})$");
    m.insert("![][image10]", r"$SO(3,1)$");
    m.insert("![][image11]", r"$10^{120}$");
    m.insert("![][image12]", r"$T_{\mu\nu} l^\mu l^\nu = 0$");
    m.insert("![][image13]", r"$T_{\mu\nu} l^\mu l^\nu \neq 0$");
    m.insert("![][image14]", r"$z$");
    m.insert("![][image15]", r"$\bar{z}$");
    m.insert("![][image16]", r"**Associativity, Commutativity, and Strict Linear Order.**");
    m.insert("![][image17]", r"$a > b$");
    m.insert("![][image18]", r"$a < b$");
    m.insert("![][image19]", r"$1$");
    m.insert("![][image20]", r"$0$");
    m
});

pub fn process_content(mut content: String, ep_num: &str) -> String {
    // 0. Strip orphaned base64 images early to prevent interference with diagram wrapping
    let image_def_regex = Regex::new(r"(?m)^\[image\d+\]: <data:image/.*?>\s*$").unwrap();
    content = image_def_regex.replace_all(&content, "").to_string();

    // 1. Title Sync
    let h1_regex = Regex::new(r"(?m)^#\s(?:\d+\s*:\s*)?\s*(.*)$").unwrap();
    if let Some(caps) = h1_regex.captures(&content) {
        let raw_title = caps.get(1).unwrap().as_str().trim();
        let clean_title = raw_title.trim_matches('*').trim();
        let new_h1 = format!("# {} : {}", ep_num, clean_title);
        content = h1_regex.replace(&content, new_h1.as_str()).to_string();
    }

    // 2. Invisible Character Sanitization
    content = content.replace('\u{0332}', "");
    let control_chars = Regex::new(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]").unwrap();
    content = control_chars.replace_all(&content, "").to_string();
    
    // 3. Convert ASCII Tables to Markdown Tables (DO THIS BEFORE DIAGRAMS)
    content = convert_ascii_tables(content);

    // 4. Wrap ASCII Diagrams in code blocks
    content = wrap_ascii_diagrams(content);

    // 5. Backslash cleanup (Surgical - only common GDocs escapes)
    let backslash_cleanup = Regex::new(r"\\([_.\-+!|>\[\]=])").unwrap();
    content = backslash_cleanup.replace_all(&content, "$1").to_string();

    // 6. Preserve Math Blocks
    let math_block_regex = Regex::new(r"(?s)\$\$.*?\$\$").unwrap();
    let inline_math_regex = Regex::new(r"\$.*?\$").unwrap();
    let mut math_blocks = Vec::new();
    let content_with_placeholders = math_block_regex.replace_all(&content, |caps: &regex::Captures| {
        let placeholder = format!("__MATH_BLOCK_{}__", math_blocks.len());
        math_blocks.push(caps.get(0).unwrap().as_str().to_string());
        placeholder
    }).to_string();
    let content_with_all_placeholders = inline_math_regex.replace_all(&content_with_placeholders, |caps: &regex::Captures| {
        let placeholder = format!("__MATH_BLOCK_{}__", math_blocks.len());
        math_blocks.push(caps.get(0).unwrap().as_str().to_string());
        placeholder
    }).to_string();

    let mut temp_content = content_with_all_placeholders;

    // 7. Fix Footnotes
    temp_content = fix_footnotes(temp_content);

    // 8. Currency and Dollar Escaping
    let currency_regex = Regex::new(r"(?i)\$([\d\.,]+)\s*(million|billion|trillion|k|m|b|t)?").unwrap();
    temp_content = currency_regex.replace_all(&temp_content, "$1 $2 USD ").to_string();
    temp_content = temp_content.replace("  ", " ");
    temp_content = temp_content.replace("$", r"\$");

    // 9. Apply KaTeX placeholders
    temp_content = temp_content.replace("![][image6]", "");
    for (placeholder, symbol) in KATEX_MAP.iter() {
        let escaped_placeholder = regex::escape(placeholder);
        let re = Regex::new(&format!(r"{}(.)?", escaped_placeholder)).unwrap();
        temp_content = re.replace_all(&temp_content, |caps: &regex::Captures| {
            let next_char = caps.get(1).map(|m| m.as_str()).unwrap_or("");
            if !next_char.is_empty() && next_char.chars().next().unwrap().is_alphanumeric() {
                format!("{} {}", symbol, next_char)
            } else {
                format!("{}{}", symbol, next_char)
            }
        }).to_string();
    }
    
    temp_content = temp_content.replace("  ", " ");

    // 10. Restore Math Blocks
    for (idx, block) in math_blocks.iter().enumerate() {
        let placeholder = format!("__MATH_BLOCK_{}__", idx);
        temp_content = temp_content.replace(&placeholder, block);
    }

    temp_content.trim().to_string()
}

fn wrap_ascii_diagrams(content: String) -> String {
    let mut result = String::new();
    let lines: Vec<&str> = content.lines().collect();
    let mut i = 0;
    
    let is_diag_line = |s: &str| -> bool {
        let t = s.trim();
        if t.is_empty() { return false; }
        if t == "v" || t == "|" || t == "^" { return true; }
        if t.starts_with("v ") || t.starts_with("| ") { return true; }
        if t.contains("===>") || t.contains("<===") { return true; }
        if t.starts_with('[') && t.contains(']') && !t.contains("](") { return true; }
        if t.starts_with("**") && (t.ends_with("v**") || t.ends_with("|**")) { return true; }
        false
    };

    while i < lines.len() {
        if is_diag_line(lines[i]) {
            let mut last_diag_idx = i;
            let mut j = i + 1;
            
            while j < lines.len() {
                let t = lines[j].trim();
                if is_diag_line(lines[j]) {
                    last_diag_idx = j;
                } else if !t.is_empty() {
                    // It's a non-empty, non-diag line.
                    // Keep it in the block only if it's indented and sandwiched between diag lines
                    let is_indented = lines[j].starts_with("  ");
                    let mut next_is_diag = false;
                    for k in 1..=3 {
                        if j + k < lines.len() && is_diag_line(lines[j + k]) {
                            next_is_diag = true;
                            break;
                        }
                    }
                    if !is_indented || !next_is_diag {
                        break;
                    }
                }
                j += 1;
            }
            
            let is_multi_line = last_diag_idx > i;
            let contains_arrows = lines[i].contains("===>") || lines[i].contains("<===");
            let has_table_separator = (i..=last_diag_idx).any(|k| lines[k].contains("--- |") || lines[k].contains("| ---"));
            
            if (is_multi_line || contains_arrows) && !has_table_separator {
                result.push_str("\n```text\n");
                for k in i..=last_diag_idx {
                    result.push_str(lines[k]);
                    result.push('\n');
                }
                result.push_str("```\n");
            } else {
                for k in i..=last_diag_idx {
                    result.push_str(lines[k]);
                    result.push('\n');
                }
            }
            
            i = last_diag_idx + 1;
        } else {
            result.push_str(lines[i]);
            result.push('\n');
            i += 1;
        }
    }
    result
}

fn fix_footnotes(content: String) -> String {
    let parts: Vec<&str> = Regex::new(r"(?i)#### \*\*Works cited\*\*|#### \*\*References\*\*").unwrap().split(&content).collect();
    if parts.len() < 2 { return content; }

    let body = parts[0];
    let refs_raw = parts[1];
    let header = "#### **Works cited**";

    let mut ref_list = Vec::new();
    let mut ref_map = HashMap::new();
    let entry_regex = Regex::new(r"^\s*(?:\[?\^?(\d+)\]?[:.]?)\s*(.*)").unwrap();
    
    let mut current_entry = String::new();
    let mut entries = Vec::new();

    for line in refs_raw.lines() {
        if Regex::new(r"^(\d+\.\s+|\[\^\d+\]:\s+)").unwrap().is_match(line) {
            if !current_entry.is_empty() { entries.push(current_entry.clone()); }
            current_entry = line.to_string();
        } else if !current_entry.is_empty() {
            current_entry.push('\n');
            current_entry.push_str(line);
        }
    }
    if !current_entry.is_empty() { entries.push(current_entry); }
    
    for entry in entries {
        if let Some(caps) = entry_regex.captures(&entry) {
            let num = caps.get(1).unwrap().as_str().to_string();
            let text = caps.get(2).unwrap().as_str().trim().to_string();
            if !ref_map.contains_key(&num) {
                ref_map.insert(num.clone(), text.clone());
                ref_list.push((num, text));
            }
        }
    }

    if ref_map.is_empty() { return content; }

    let marker_regex = Regex::new(r"([.,;'\x22)\]])(\d+(?:[\s,]+\d+)*)(.)?").unwrap();
    let mut body_with_markers = String::new();
    let mut last_end = 0;

    for caps in marker_regex.captures_iter(body) {
        let full_match = caps.get(0).unwrap();
        let punct = caps.get(1).unwrap().as_str();
        let nums_str = caps.get(2).unwrap().as_str();
        let next_char = caps.get(3).map(|m| m.as_str()).unwrap_or("");

        if !next_char.is_empty() && (next_char.chars().next().unwrap().is_ascii_digit() || next_char == ".") {
            continue;
        }

        body_with_markers.push_str(&body[last_end..full_match.start()]);
        let markers: Vec<String> = nums_str.split(|c: char| c.is_whitespace() || c == ',').filter(|s| !s.is_empty()).map(|s| format!("[^{}]", s)).collect();
        body_with_markers.push_str(punct);
        body_with_markers.push_str(&markers.join(""));
        body_with_markers.push_str(next_char);
        last_end = full_match.end();
    }
    body_with_markers.push_str(&body[last_end..]);

    let used_marker_regex = Regex::new(r"\[\^(\d+)\]").unwrap();
    let mut unique_used = Vec::new();
    for caps in used_marker_regex.captures_iter(&body_with_markers) {
        let m = caps.get(1).unwrap().as_str().to_string();
        if !unique_used.contains(&m) { unique_used.push(m); }
    }

    if unique_used.is_empty() { return body.to_string() + "\n\n" + header + "\n" + refs_raw; }

    let mut final_map = HashMap::new();
    let mut final_refs = Vec::new();
    let mut available_defs: Vec<String> = ref_list.iter().map(|(_, t)| t.clone()).collect();

    for (i, old_num) in unique_used.iter().enumerate() {
        let new_num = (i + 1).to_string();
        let text = if let Some(t) = ref_map.get(old_num) {
            let t_clone = t.clone();
            available_defs.retain(|x| x != &t_clone);
            t_clone
        } else if i < available_defs.len() {
            available_defs.remove(0)
        } else {
            "Missing citation".to_string()
        };
        final_map.insert(old_num.clone(), (new_num.clone(), text.clone()));
        final_refs.push((new_num, text));
    }

    let final_body = used_marker_regex.replace_all(&body_with_markers, |caps: &regex::Captures| {
        let old_num = caps.get(1).unwrap().as_str();
        format!("[^{}]", final_map.get(old_num).map(|(n, _)| n).unwrap_or(&old_num.to_string()))
    });

    let mut result = final_body.to_string();
    result.push_str("\n\n");
    result.push_str(header);
    result.push('\n');
    for (num, text) in final_refs { result.push_str(&format!("[^{}]: {}\n", num, text)); }
    for (i, text) in available_defs.iter().enumerate() { result.push_str(&format!("{}. {}\n", unique_used.len() + i + 1, text)); }
    result
}

fn convert_ascii_tables(content: String) -> String {
    let mut result = String::new();
    let mut lines = content.lines().peekable();

    while let Some(line) = lines.next() {
        let trimmed = line.trim();
        let is_table_start = (trimmed.contains("+---") && trimmed.ends_with('+')) || 
                             (trimmed.starts_with('|') && trimmed.ends_with('|')) ||
                             (trimmed.starts_with("![][image") && trimmed.contains("+---"));
        
        if is_table_start {
            let mut table_data = Vec::new();
            table_data.push(line);
            while let Some(next) = lines.peek() {
                let nt = next.trim();
                if nt.starts_with('|') || (nt.contains("+---") && nt.ends_with('+')) || nt.is_empty() {
                    table_data.push(lines.next().unwrap());
                } else {
                    break;
                }
            }
            let mut md_rows = Vec::new();
            for row in table_data {
                let mut r = row.trim().to_string();
                if r.starts_with("![][image") {
                    if let Some(pos) = r.find('+') { r = r[pos..].to_string(); }
                    else if let Some(pos) = r.find('|') { r = r[pos..].to_string(); }
                }
                if r.starts_with('|') {
                    let cells: Vec<String> = r.split('|').map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect();
                    if !cells.is_empty() { md_rows.push(cells); }
                }
            }
            if !md_rows.is_empty() {
                result.push('\n');
                let mut start_idx = 0;
                if md_rows[0].len() == 1 {
                    result.push_str(&format!("**{}**\n\n", md_rows[0][0]));
                    start_idx = 1;
                }
                if md_rows.len() > start_idx {
                    for (i, row) in md_rows[start_idx..].iter().enumerate() {
                        result.push_str(&format!("| {} |\n", row.join(" | ")));
                        if i == 0 {
                            let sep: Vec<String> = row.iter().map(|_| "---".to_string()).collect();
                            result.push_str(&format!("| {} |\n", sep.join(" | ")));
                        }
                    }
                }
                result.push('\n');
            }
        } else {
            result.push_str(line);
            result.push('\n');
        }
    }
    result
}
