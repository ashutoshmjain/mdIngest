//! # Sanitizer Module (Gemini-to-mdbook)
//! 
//! This module provides the core transformation logic for converting 
//! "shielded" Gemini Pro outputs into production-ready mdbook content.

use regex::Regex;
use std::collections::HashMap;
use html_escape::decode_html_entities;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct GeminiCapsule {
    title: String,
    body: String,
    references: Vec<GeminiReference>,
}

#[derive(Debug, Deserialize)]
struct GeminiReference {
    id: usize,
    text: String,
}

/// The primary entry point for the Gemini-to-mdbook transformation.
pub fn process_content(mut content: String, ep_num: &str, _title_override: Option<&str>, word_limit: usize) -> String {
    // 0. Decode HTML Entities early
    content = decode_html_entities(&content).to_string();

    // 0.0 Detect JSON Capsule
    let mut json_title = None;
    let mut json_body = None;
    let mut json_refs = None;
    let mut is_json_capsule = false;

    // Try parsing as pure JSON first
    if let Ok(capsule) = serde_json::from_str::<GeminiCapsule>(&content) {
        json_title = Some(capsule.title);
        json_body = Some(capsule.body);
        json_refs = Some(capsule.references);
        is_json_capsule = true;
    } else {
        // Fallback to regex for code block if LLM was "helpful"
        let json_regex = Regex::new(r"(?s)```json\s*(\{.*?\})\s*```").unwrap();
        if let Some(caps) = json_regex.captures(&content) {
            let json_raw = caps.get(1).unwrap().as_str();
            if let Ok(capsule) = serde_json::from_str::<GeminiCapsule>(json_raw) {
                json_title = Some(capsule.title);
                json_body = Some(capsule.body);
                json_refs = Some(capsule.references);
                is_json_capsule = true;
            }
        }
    }

    // Prepare content for standard sanitization
    if is_json_capsule {
        content = json_body.unwrap();
    } else {
        // 0.1 Strip Rust shields (if any) for non-JSON content
        content = content.trim().to_string();
        let prefix_regex = Regex::new(r"^(?:Rust)?r(#+)\x22").unwrap();
        if let Some(caps) = prefix_regex.captures(&content) {
            let hash_count = caps.get(1).unwrap().as_str().len();
            content = prefix_regex.replace(&content, "").to_string();
            let suffix_pattern = format!(r"\x22{}", "#".repeat(hash_count));
            if content.ends_with(&suffix_pattern) {
                content = content[..content.len() - suffix_pattern.len()].to_string();
            } else if content.ends_with(&format!("{}\n", suffix_pattern)) {
                content = content[..content.len() - suffix_pattern.len() - 1].to_string();
            }
        }
        let gemini_artifacts = Regex::new(r"(?m)^```(text|markdown|rust)?\s*$").unwrap();
        content = gemini_artifacts.replace_all(&content, "").to_string();
        content = content.trim_matches('`').trim().to_string();
    }

    // 1. Title Processing
    let h1_regex_full = Regex::new(r"(?m)^#\s(?:\d+\s*:\s*)?\s*(.*)$").unwrap();
    let mut h1_title = if let Some(t) = json_title {
        t
    } else if let Some(caps) = h1_regex_full.captures(&content) {
        caps.get(1).unwrap().as_str().trim().trim_matches('*').to_string()
    } else {
        String::from("Untitled")
    };

    content = h1_regex_full.replace(&content, "").to_string().trim().to_string();

    let words: Vec<&str> = h1_title.split_whitespace().collect();
    if words.len() > word_limit {
        h1_title = words[..word_limit].join(" ");
    }

    // 2. Sanitization Pipeline
    content = content.replace('\u{0332}', "");
    let control_chars = Regex::new(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]").unwrap();
    content = control_chars.replace_all(&content, "").to_string();

    content = convert_ascii_tables(content);
    content = wrap_ascii_diagrams(content);

    let backslash_cleanup = Regex::new(r"\\([_.\-+!|>\[\]=])").unwrap();
    content = backslash_cleanup.replace_all(&content, "$1").to_string();

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

    // 3. Socials & References Construction
    let podcast_links = r#"
<center><a href="https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Spotify</a><a href="https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Apple Podcasts</a><a href="https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">Fountain.fm</a></center>
"#;

    let lightning_widget = r#"
<div style="text-align: center; margin: 25px 0;">
    <a href="lightning:shutosha@primal.net" style="background-color: #F7931A; color: white; padding: 14px 28px; text-align: center; text-decoration: none; display: inline-block; border-radius: 10px; font-weight: 900; font-family: sans-serif; border: 3px solid #E87F0E; box-shadow: 0 4px 10px rgba(0,0,0,0.2); font-size: 1.1em; letter-spacing: 0.5px;">⚡ ZAP WITH LIGHTNING</a>
</div>
"#;

    let social_block = format!("\n\n<!-- SOCIALS_START -->\n{}{}\n<!-- SOCIALS_END -->\n", podcast_links, lightning_widget);

    let mut refs_section = String::from("\n\n#### **Works cited**\n\n");
    if is_json_capsule {
        if let Some(refs) = json_refs {
            let mut markers_found = false;
            for r in &refs {
                let marker = format!("[{}]", r.id);
                if temp_content.contains(&marker) { markers_found = true; break; }
            }

            for r in refs {
                let mut ref_text = r.text.clone();
                let url_regex = Regex::new(r"(https?://[^\s)\]]+[^.\s)\]])").unwrap();
                ref_text = url_regex.replace_all(&ref_text, |c: &regex::Captures| {
                    let u = c.get(1).unwrap().as_str();
                    format!("[{}]({})", u, u)
                }).to_string();

                if markers_found {
                    let marker = format!("[{}]", r.id);
                    let foot_marker = format!("[^{}]", r.id);
                    temp_content = temp_content.replace(&marker, &foot_marker);
                    refs_section.push_str(&format!("{}: {}\n\n", foot_marker, ref_text));
                } else {
                    refs_section.push_str(&format!("{}. {}\n\n", r.id, ref_text));
                }
            }
        }
    } else {
        temp_content = fix_footnotes(temp_content);
        refs_section = String::new(); 
    }

    // 4. Currency and Dollar Escaping
    let currency_regex = Regex::new(r"(?i)\$([\d\.,]+)\s*(million|billion|trillion|k|m|b|t)?").unwrap();
    temp_content = currency_regex.replace_all(&temp_content, "$1 $2 USD ").to_string();
    temp_content = temp_content.replace("  ", " ");
    temp_content = temp_content.replace("$", r"\$");

    // 5. Restore Math Blocks
    for (idx, block) in math_blocks.iter().enumerate() {
        let placeholder = format!("__MATH_BLOCK_{}__", idx);
        temp_content = temp_content.replace(&placeholder, block);
    }

    // 6. Final Assembly
    format!("# {} : {}\n\n{}{}{}{}", ep_num, h1_title, temp_content.trim(), social_block, refs_section, "\n").trim().to_string()
}

pub fn find_first_substantial_paragraph(content: &str) -> Option<usize> {
    let mut in_code_block = false;
    let mut current_pos = 0;
    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("```") {
            in_code_block = !in_code_block;
            current_pos += line.len() + 1;
            continue;
        }
        if !in_code_block && !trimmed.is_empty() {
            let is_header = trimmed.starts_with('#');
            let is_list = trimmed.starts_with('*') || trimmed.starts_with('-') || (trimmed.len() > 2 && trimmed.chars().next().unwrap().is_digit(10) && trimmed.contains(". "));
            let is_html = trimmed.starts_with('<');
            if !is_header && !is_list && !is_html && trimmed.len() > 100 {
                return Some(current_pos + line.len());
            }
        }
        current_pos += line.len() + 1;
    }
    None
}

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
                    if !is_indented || !next_is_diag { break; }
                }
                j += 1;
            }
            let is_multi_line = last_diag_idx > i;
            let contains_arrows = lines[i].contains("===>") || lines[i].contains("<===") || lines[i].contains("<====") || lines[i].starts_with("=====");
            let has_table_separator = (i..=last_diag_idx).any(|k| lines[k].contains("--- |") || lines[k].contains("| ---") || (lines[k].contains('|') && lines[k].contains('-')));
            
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
    let header_regex = Regex::new(r"(?im)^#+\s+(\*\*Works cited\*\*|Works cited|References|Bibliography|References or Bibliography)").unwrap();
    let parts: Vec<&str> = header_regex.split(&content).collect();
    if parts.len() < 2 { return content; }

    let body = parts[0];
    let refs_raw = parts[1];
    let header = "#### **Works cited**";

    let ref_pattern = Regex::new(r"(?m)^(\*?\s*(\*\*\[?(\d+)\]?\*\*|\[(\d+)\])\s*|\s*$)").unwrap();
    let mut ref_entries = Vec::new();
    let matches: Vec<_> = ref_pattern.find_iter(refs_raw).collect();
    for (i, m) in matches.iter().enumerate() {
        let caps = ref_pattern.captures(m.as_str()).unwrap();
        let old_num = caps.get(2).map(|n| n.as_str().to_string())
            .or_else(|| caps.get(3).map(|n| n.as_str().to_string()));
        let start = m.end();
        let end = if i + 1 < matches.len() { matches[i+1].start() } else { refs_raw.len() };
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
            if !unique_old_nums.contains(&n_trimmed) { unique_old_nums.push(n_trimmed); }
        }
    }

    let mut old_to_new = HashMap::new();
    let mut new_refs = Vec::new();
    let url_regex = Regex::new(r"(https?://[^\s)\]]+[^.\s)\]])").unwrap();
    for old_num in unique_old_nums {
        let mut aggregated_text = String::new();
        let mut found = false;
        while let Some(ref_entry) = ref_entries.iter_mut().find(|r| r.old_num.as_ref() == Some(&old_num) && !r.processed) {
            if found { aggregated_text.push_str("\n\n"); }
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

fn convert_ascii_tables(content: String) -> String {
    let mut result = String::new();
    let mut lines = content.lines().peekable();
    while let Some(line) = lines.next() {
        let trimmed = line.trim();
        let is_table_start = (trimmed.contains("+---") && trimmed.ends_with('+')) || (trimmed.starts_with('|') && (trimmed.ends_with('|') || trimmed.contains(" --- ")));
        if is_table_start {
            let mut table_data = Vec::new();
            table_data.push(line);
            while let Some(next) = lines.peek() {
                let nt = next.trim();
                if nt.starts_with('|') || (nt.contains("+---") && nt.ends_with('+')) || nt.contains(" --- ") || nt.is_empty() {
                    table_data.push(lines.next().unwrap());
                } else { break; }
            }
            let mut md_rows = Vec::new();
            for row in table_data {
                let r = row.trim();
                if r.starts_with('|') {
                    let cells: Vec<String> = r.split('|').map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect();
                    if !cells.is_empty() { md_rows.push(cells); }
                }
            }
            if !md_rows.is_empty() {
                result.push('\n');
                let mut start_idx = 0;
                if md_rows[0].len() == 1 && md_rows.len() > 1 {
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
