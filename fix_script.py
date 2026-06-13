import re

with open("crate/src/main.rs", "r") as f:
    content = f.read()

config_pattern = re.compile(r"title_word_limit: Option<usize>,.*?podcast_html", re.DOTALL)
content = config_pattern.sub(r"title_word_limit: Option<usize>,\n    recent_window_size: Option<usize>,\n    podcast_html", content)

config_default_pattern = re.compile(r"title_word_limit: Some\(5\),.*?podcast_html", re.DOTALL)
content = config_default_pattern.sub(r"title_word_limit: Some(5),\n        recent_window_size: Some(21),\n        podcast_html", content)

var_pattern = re.compile(r"let mut do_video = false;\s*let mut title_override")
new_vars = "let mut do_video = false;\n    let mut do_park = None;\n    let mut do_unpark = None;\n    let mut do_list_parked = false;\n    let mut title_override"
content = var_pattern.sub(new_vars, content)

arg_pattern = re.compile(r"\"--video\" => do_video = true,\s*\"-t\" \| \"--title\"")
new_args = "\"--video\" => do_video = true,\n            \"--park\" => {\n                if i + 1 < args.len() {\n                    do_park = Some(args[i+1].clone());\n                    i += 1;\n                }\n            },\n            \"--unpark\" => {\n                if i + 2 < args.len() {\n                    do_unpark = Some((args[i+1].clone(), args[i+2].clone()));\n                    i += 2;\n                }\n            },\n            \"--list-parked\" => do_list_parked = true,\n            \"-t\" | \"--title\""
content = arg_pattern.sub(new_args, content)

exec_pattern = re.compile(r"i \+= 1;\n    \}\n\n    if let Some\(num\) = number \{")
new_exec = "i += 1;\n    }\n\n    if do_list_parked {\n        return list_parked();\n    }\n\n    if let Some(num) = do_park {\n        return park_episode(&num, &ingest_config);\n    }\n\n    if let Some((old_num, new_num)) = do_unpark {\n        return unpark_episode(&old_num, &new_num, &ingest_config);\n    }\n\n    if let Some(num) = number {"
content = exec_pattern.sub(new_exec, content)

ingest_pattern = re.compile(r"if let Err\(e\) = update_summary\(number\) \{")
content = ingest_pattern.sub(r"if let Err(e) = update_summary(&ingest_config) {", content)

summary_func_pattern = re.compile(r"fn update_summary\(number: &str\) -> Result<\(\)> \{.*?\n\}\n", re.DOTALL)
new_summary_func = r"""#[derive(Debug, Clone)]
struct EpisodeEntry {
    number: Option<u32>,
    filename: String,
    title: String,
    mtime: std::time::SystemTime,
}

fn update_summary(config: &IngestConfig) -> Result<()> {
    let summary_path = "src/SUMMARY.md";
    let window_size = config.recent_window_size.unwrap_or(21);
    
    let mut all_files = Vec::new();
    let pattern = "src/*.md";
    for entry in glob(pattern)? {
        if let Ok(path) = entry {
            let filename = path.file_name().unwrap().to_str().unwrap();
            if ["SUMMARY.md", "cover.md"].contains(&filename) { continue; }
            let base = filename.trim_end_matches(".md").trim();
            let md_content = std::fs::read_to_string(&path)?;
            let h1_regex = regex::Regex::new(r"(?m)^#\s+(?:(?:\d+)\s*[:\s]*)?\s*(.*)$").unwrap();
            let title = if let Some(caps) = h1_regex.captures(&md_content) {
                caps.get(1).unwrap().as_str().trim().to_string()
            } else { "Untitled".to_string() };
            let mtime = std::fs::metadata(&path)?.modified()?;
            let number = base.parse::<u32>().ok();
            all_files.push(EpisodeEntry { number, filename: base.to_string(), title, mtime });
        }
    }

    let mut numbered_active: Vec<_> = all_files.iter().filter(|e| e.number.is_some() && !e.filename.starts_with("_")).cloned().collect();
    let mut wip_parked: Vec<_> = all_files.iter().filter(|e| e.filename.starts_with("_")).cloned().collect();

    numbered_active.sort_by(|a, b| b.number.unwrap().cmp(&a.number.unwrap()));
    wip_parked.sort_by(|a, b| b.mtime.cmp(&a.mtime));

    let recents: Vec<_> = numbered_active.iter().take(window_size).collect();
    let overflow_numbered: Vec<_> = numbered_active.iter().skip(window_size).cloned().collect();

    eprintln!("📊 Indexer: {} Recents, {} WIP", recents.len(), wip_parked.len());
    
    let original_content = std::fs::read_to_string(summary_path)?;
    let mut final_lines = Vec::new();
    
    for line in original_content.lines() {
        if line.contains("# Recent") || line.contains("<!-- RECENT_START -->") { break; }
        final_lines.push(line.to_string());
    }

    final_lines.push("\n# Recent ..".to_string());
    final_lines.push("<!-- RECENT_START -->".to_string());
    for ep in recents { final_lines.push(format!("- [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename)); }
    final_lines.push("<!-- RECENT_END -->".to_string());

    final_lines.push("\n# WIP / Parked".to_string());
    if wip_parked.is_empty() {
        final_lines.push("- [None at this moment. Join us on GitHub!](https://github.com/ashutoshmjain/deepDive)".to_string());
    } else {
        for ep in wip_parked {
            let display_num = ep.filename.trim_start_matches('_');
            final_lines.push(format!("- [{} : {}]({}.md)", display_num, ep.title, ep.filename));
        }
    }

    final_lines.push("\n# Archive".to_string());
    if !overflow_numbered.is_empty() {
        final_lines.push("## Older Episodes".to_string());
        for ep in overflow_numbered {
            final_lines.push(format!("- [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }

    let mut in_thematic_zone = false;
    let mut thematic_buffer = Vec::new();
    let num_regex = regex::Regex::new(r"\d+\.md").unwrap();
    for line in original_content.lines() {
        if line.contains("<!-- RECENT_END -->") { in_thematic_zone = true; continue; }
        if in_thematic_zone {
            if line.contains("# Recent") || line.contains("# WIP") || line.contains("# Archive") || line.contains("# Repository") { continue; }
            if num_regex.is_match(line) { continue; }
            if thematic_buffer.is_empty() && line.trim().is_empty() { continue; }
            thematic_buffer.push(line.to_string());
        }
    }
    final_lines.extend(thematic_buffer);
    std::fs::write(summary_path, final_lines.join("\n"))?;
    Ok(())
}
"""

def repl_func(match):
    return new_summary_func

content = summary_func_pattern.sub(repl_func, content)

new_funcs = r"""
fn list_parked() -> Result<()> {
    eprintln!("🅿️  Currently Parked Episodes:");
    for entry in glob("src/_[0-9]*.md")? {
        if let Ok(path) = entry {
            let filename = path.file_name().unwrap().to_str().unwrap();
            let base = filename.trim_end_matches(".md");
            let content = std::fs::read_to_string(&path)?;
            let h1_regex = regex::Regex::new(r"(?m)^#\s+(?:(?:\d+)\s*[:\s]*)?\s*(.*)$").unwrap();
            let title = if let Some(caps) = h1_regex.captures(&content) { caps.get(1).unwrap().as_str().trim() } else { "Untitled" };
            println!("  [{}] : {}", &base[1..], title);
        }
    }
    Ok(())
}

fn park_episode(number: &str, config: &IngestConfig) -> Result<()> {
    let videos: Vec<_> = glob(&format!("src/vid/{}*.mp4", number))?.filter_map(Result::ok).collect();
    if !videos.is_empty() {
        eprintln!("❌ Cannot park episode {}: It has infographic videos and is 'cast in stone'.", number);
        anyhow::bail!("Episode is immutable");
    }
    let src = format!("src/{}.md", number);
    let dest = format!("src/_{}.md", number);
    if std::path::Path::new(&src).exists() {
        std::fs::rename(&src, &dest)?;
        eprintln!("✅ Parked episode {} -> {}", src, dest);
        update_summary(config)?; 
    } else {
        eprintln!("⚠️ Episode {} not found in src/", number);
    }
    Ok(())
}

fn unpark_episode(old_number: &str, new_number: &str, config: &IngestConfig) -> Result<()> {
    let src = format!("src/_{}.md", old_number);
    let dest = format!("src/{}.md", new_number);
    if !std::path::Path::new(&src).exists() { anyhow::bail!("Source not found"); }
    std::fs::rename(&src, &dest)?;
    let mut content = std::fs::read_to_string(&dest)?;
    content = content.replace(&format!("# {}", old_number), &format!("# {}", new_number));
    std::fs::write(&dest, content)?;
    update_summary(config)?;
    Ok(())
}
"""
content += new_funcs

with open("crate/src/main.rs", "w") as f:
    f.write(content)

