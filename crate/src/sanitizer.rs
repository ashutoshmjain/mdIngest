//! # Sanitizer Module (Gemini-to-mdbook)
//! 
//! This module provides the core transformation logic for converting 
//! "shielded" Gemini Pro outputs into production-ready mdbook content.
//! 
//! It is specifically designed to handle the constraints of the **Master Prompt**, 
//! including the removal of Rust-style raw string literals (`r#" ... "#`) and 
//! the enforcement of research-tier formatting.

use regex::Regex;
use std::collections::HashMap;
use html_escape::decode_html_entities;

/// The primary entry point for the Gemini-to-mdbook transformation.
/// 
/// This function executes a multi-stage sanitization pipeline:
/// 1. Decodes HTML entities (to handle web-pasted content).
/// 2. **Shield Stripping**: Removes the `r#"` and `"#` wrappers and Gemini backticks.
/// 3. Title Sync: Enforces a word limit for H1 headers.
/// 4. Unicode Sanitization: Strips invisible control characters and hidden artifacts.
/// 5. Structural Wrapping: Detects ASCII tables/diagrams and applies correct Markdown formatting.
/// 6. Footnote Hardening: Re-indexes and formats bibliography sections for KaTeX compatibility.
pub fn process_content(mut content: String, ep_num: &str, title_override: Option<&str>, word_limit: usize) -> String {
    // 0. Decode HTML Entities early
    content = decode_html_entities(&content).to_string();

    // 0.1 Strip Rust raw string artifacts and Gemini markdown markers (The "Shield")
    content = content.trim().to_string();
    if content.starts_with("Rustr#\"") {
        content = content[7..].to_string();
    } else if content.starts_with("r#\"") {
        content = content[3..].to_string();
    }

    if content.ends_with("\"#") {
        content = content[..content.len()-2].to_string();
    } else if content.ends_with("\"#\n") {
        content = content[..content.len()-3].to_string();
    }

    let gemini_artifacts = Regex::new(r"(?m)^```(text|markdown|rust)?\s*$").unwrap();
    content = gemini_artifacts.replace_all(&content, "").to_string();
    
    // Final trim to handle any leftover backticks at top/bottom
    content = content.trim_matches('`').trim().to_string();

    // 0.2 Strip orphaned base64 images early to prevent interference with diagram wrapping
    let image_def_regex = Regex::new(r"(?m)^\[image\d+\]: <data:image/.*?>\s*$").unwrap();
    content = image_def_regex.replace_all(&content, "").to_string();

    // 1. Title Sync - Handle "XXX : Title" format and enforce word limit
    let h1_regex = Regex::new(r"(?m)^#\s(?:\d+\s*:\s*)?\s*(.*)$").unwrap();
    
    let display_title = if let Some(t) = title_override {
        t.to_string()
    } else if let Some(caps) = h1_regex.captures(&content) {
        let raw_title = caps.get(1).unwrap().as_str().trim();
        let clean_title = raw_title.trim_matches('*').trim();
        
        // Enforce word limit based on config
        let words: Vec<&str> = clean_title.split_whitespace().collect();
        if words.len() > word_limit {
            let mut truncated = words[..word_limit].join(" ");
            let stop_words = vec!["of", "the", "in", "and", "on", "a", "an", "with", "for", "to", "at", "by", "from"];
            if let Some(last_word) = words[..word_limit].last() {
                if stop_words.contains(&last_word.to_lowercase().as_str()) {
                    truncated = words[..word_limit-1].join(" ");
                }
            }
            truncated
        } else {
            clean_title.to_string()
        }
    } else {
        "Untitled".to_string()
    };
    
    let new_h1 = format!("# {} : {}", ep_num, display_title);
    if h1_regex.is_match(&content) {
        content = h1_regex.replace(&content, new_h1.as_str()).to_string();
    } else {
        content = format!("{}\n\n{}", new_h1, content);
    }

    // 2. Invisible Character Sanitization
    content = content.replace('\u{0332}', "");
    let control_chars = Regex::new(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]").unwrap();
    content = control_chars.replace_all(&content, "").to_string();

    // 3. Convert ASCII Tables to Markdown Tables (DO THIS BEFORE DIAGRAMS)
    content = convert_ascii_tables(content);

    // 4. Wrap ASCII Diagrams in code blocks
    content = wrap_ascii_diagrams(content);

    // 5. Backslash cleanup (Surgical - only common AI escapes)
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

    // 9. Clean any remaining image tags if they exist
    let image_tag_regex = Regex::new(r"!\[\]\[image\d+\]").unwrap();
    temp_content = image_tag_regex.replace_all(&temp_content, "").to_string();

    // 10. Restore Math Blocks
    for (idx, block) in math_blocks.iter().enumerate() {
        let placeholder = format!("__MATH_BLOCK_{}__", idx);
        temp_content = temp_content.replace(&placeholder, block);
    }

    temp_content.trim().to_string()
}

/// Identifies and wraps ASCII-based diagrams in code blocks.
/// 
/// Logic detects common diagram markers like `===>`, `|`, and `v` while 
/// ignoring standard citations or Markdown lists.
fn wrap_ascii_diagrams(content: String) -> String {
    let mut result = String::new();
    let lines: Vec<&str> = content.lines().collect();
    let mut i = 0;
    
    let is_diag_line = |s: &str| -> bool {
        let t = s.trim();
        if t.is_empty() { return false; }
        if t == "v" || t == "|" || t == "^" || t == "v |" { return true; }
        if t.starts_with("v ") || t.starts_with("| ") { return true; }
        if t.contains("===>") || t.contains("<===") || t.contains("<====") { return true; }
        if t.starts_with('[') && t.contains(']') && !t.contains("](") { 
            let citation_regex = Regex::new(r"^\[\d+\]").unwrap();
            if citation_regex.is_match(t) { return false; }
            return true; 
        }
        if t.starts_with("**<---") || t.starts_with("--->**") { return true; }
        if t.starts_with("**") && (t.ends_with("v**") || t.ends_with("|**")) { return true; }
        if t.starts_with("+---") && t.ends_with("+") { return true; }
        if t.contains("|") && (t.contains("+--->") || t.contains("ALGEBRAIC ASCENT")) { return true; }
        if t.starts_with("=====") { return true; }
        if t.contains("<====") { return true; }
        if t.contains("+---") && t.contains("+") { return true; }
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
            let contains_arrows = lines[i].contains("===>") || lines[i].contains("<===") || lines[i].contains("<====") || lines[i].starts_with("=====");
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

/// Standardizes and re-indexes footnotes.
/// 
/// This function:
/// - Extracts the "Works cited" or "References" section.
/// - Re-numbers inline citations `[n]` to `[^n]`.
/// - Re-numbers the reference list sequentially.
/// - Ensures URLs are properly hyperlinked in the bibliography.
fn fix_footnotes(content: String) -> String {
    let header_regex = Regex::new(r"(?i)#### \*\*Works cited\*\*|#### \*\*References\*\*|## Bibliography|## References or Bibliography|## References").unwrap();
    let parts: Vec<&str> = header_regex.split(&content).collect();
    if parts.len() < 2 { return content; }

    let body = parts[0];
    let refs_raw = parts[1];
    let header = "#### **Works cited**";

    let ref_pattern = Regex::new(r"(?m)^\*?\s*(\*\*\[?(\d+)\]?\*\*|\*\*\*\*|\[(\d+)\])\s*").unwrap();
    
    let mut ref_entries = Vec::new();
    let matches: Vec<_> = ref_pattern.find_iter(refs_raw).collect();
    
    for (i, m) in matches.iter().enumerate() {
        let caps = ref_pattern.captures(m.as_str()).unwrap();
        let old_num = caps.get(2).map(|n| n.as_str().to_string())
            .or_else(|| caps.get(3).map(|n| n.as_str().to_string()));
        
        let start = m.end();
        let end = if i + 1 < matches.len() {
            matches[i+1].start()
        } else {
            refs_raw.len()
        };
        
        let text = refs_raw[start..end].trim().to_string();
        ref_entries.push(RefEntry { old_num, text, processed: false });
    }

    if ref_entries.is_empty() { return content; }

    let marker_pattern = Regex::new(r"\[(\d+(?:\s*,\s*\d+)*)\]").unwrap();
    let mut unique_old_nums = Vec::new();
    
    for caps in marker_pattern.captures_iter(body) {
        let nums_str = caps.get(1).unwrap().as_str();
        for n in nums_str.split(',') {
            let n_trimmed = n.trim().to_string();
            if !unique_old_nums.contains(&n_trimmed) {
                unique_old_nums.push(n_trimmed);
            }
        }
    }

    let mut old_to_new = HashMap::new();
    let mut new_refs = Vec::new();
    let url_regex = Regex::new(r"(https?://[^\s)\]]+[^.\s)\]])").unwrap();
    
    for old_num in unique_old_nums {
        let mut aggregated_text = String::new();
        let mut found = false;
        
        while let Some(ref_entry) = ref_entries.iter_mut().find(|r| r.old_num.as_ref() == Some(&old_num) && !r.processed) {
            if found { aggregated_text.push_str(" | "); }
            
            let entry_text_clean = ref_entry.text.replace("`", "");
            let processed_text = url_regex.replace_all(&entry_text_clean, |caps: &regex::Captures| {
                let url = caps.get(1).unwrap().as_str();
                format!("[{}]({})", url, url)
            }).to_string();
            
            aggregated_text.push_str(&processed_text);
            ref_entry.processed = true;
            found = true;
        }

        if found {
            let new_num = (new_refs.len() + 1).to_string();
            old_to_new.insert(old_num, new_num);
            new_refs.push(aggregated_text);
        } else if let Some(unprocessed_star) = ref_entries.iter_mut().find(|r| r.old_num.is_none() && !r.processed) {
            let new_num = (new_refs.len() + 1).to_string();
            old_to_new.insert(old_num, new_num);
            
            let processed_text = url_regex.replace_all(&unprocessed_star.text, |caps: &regex::Captures| {
                let url = caps.get(1).unwrap().as_str();
                format!("[{}]({})", url, url)
            }).to_string();
            
            new_refs.push(processed_text);
            unprocessed_star.processed = true;
        } else {
            let new_num = (new_refs.len() + 1).to_string();
            old_to_new.insert(old_num.clone(), new_num);
            new_refs.push(format!("**TODO: Missing citation for index {}**", old_num));
        }
    }

    let final_body = marker_pattern.replace_all(body, |caps: &regex::Captures| {
        let nums_str = caps.get(1).unwrap().as_str();
        let mut new_markers: Vec<String> = nums_str.split(',')
            .map(|n| {
                let n_trimmed = n.trim();
                format!("[^{}]", old_to_new.get(n_trimmed).unwrap_or(&n_trimmed.to_string()))
            }).collect();
        new_markers.dedup();
        new_markers.join(" ") 
    });

    let mut result = final_body.to_string();
    result.push_str("\n\n");
    result.push_str(header);
    result.push_str("\n\n");
    
    for (i, text) in new_refs.iter().enumerate() {
        result.push_str(&format!("[^{}]: {}\n\n", i + 1, text));
    }
    result
}

struct RefEntry {
    old_num: Option<String>,
    text: String,
    processed: bool,
}

/// Identifies and converts ASCII grid tables to standard Markdown tables.
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
                // Check if it's REALLY a table or a diagram part of a table-like structure
                let is_diagram = md_rows.iter().any(|row| row.iter().any(|cell| cell.contains("ALGEBRAIC ASCENT") || cell.contains("+--->")));
                if is_diagram {
                    for row in md_rows {
                        result.push_str(&format!("| {} |\n", row.join(" | ")));
                    }
                    continue;
                }

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
