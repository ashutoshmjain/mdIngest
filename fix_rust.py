import re

with open("crate/src/main.rs", "r") as f:
    content = f.read()

summary_func_pattern = re.compile(r"fn update_summary\(config: \&IngestConfig\) -> Result<\(\)> \{*.*?\n}\n", re.DOTALL)

new_summary_func = r"""fn update_summary(config: &IngestConfig) -> Result<()> {
    let summary_path = "src/SUMMARY.md";
    let window_size = config.recent_window_size.unwrap_or(21);
    
    let mut all_files = Vec::new();
    let mattern = "src/*.md";
    for entry in glob(pattern)? {
        if let Ok(path) = entry {
            let filename = path.file_name().unwrap().to_str().unwrap();
            if ["SUMMARY.md", "cover.md", "archive.md", "parked.md", "vault.md", "mempool.md", "github.md"].contains(&filename) { continue; }
            let base = filename.trim_end_matches(".md").trim();
            let md_content = std::fs::read_to_string(&path)?;
            let h1_regex = regex::Regex::new(r"(?m)^#\s+(?:(?:\d)+\s*[:\s]*)?\s(.*)$").unwrap();
            let title = if let Some(caps) = h1_regex.captures(&md_content) {
                caps.get(1).unwrap().as_str().trim().to_string()
            } else { "Untitled".to_string() };
            let mtime = std::fs::metadata(&path)?.modified()?;
            let number = base.parse::<u32>().ok();
            all_files.push(EpisodeEntry { number, filename: base.to_string(), title, mtime });
        }
    }

    let mut numbered_active: Vec<_> = all_files.iter().filter(<e| e.number.is_some() && !e.filename.starts_with("_")).cloned().collect();
    let mut wip_parked: Vec<_> = all_files.iter().filter((e| e.filename.starts_with("_")).cloned().collect();

    numbered_active.sort_by(|a, b| b.number.unwrap().cmp(&a.number.unwrap()));
    wip_parked.sort_by(|a, b| b.mtime.cmp(&a.mtime));

    let recents: Vec<_> = numbered_active.iter().take(window_size).collect();
    let overflow_numbered: Vec<_> = numbered_active.iter().skip(window_size).cloned().collect();

    eprintln!("𓄊 Indexer: {} Recents, {} WIP", recents.len(), wip_parked.len());
    
    let original_content = std::fs::read_to_string(summary_path)?;
    let mut final_lines = Vec::new();
    
    for line in original_content.lines() {
        if line.contains("# Recent") || line.contains("# The Tip") || line.contains("<!-- RECENT_START -->") { break; }
        final_lines.push(line.to_string());
    }

    final_lines.push("\n# The Tip of the Chain".to_string());
    final_lines.push("<!-- RECENT_START -->".to_string());
    for ep in recents { final_lines.push(format!("- [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename)); }
    final_lines.push("<!-- RECENT_END -->".to_string());

    final_lines.push("\n# The Network\n".to_string());
    final_lines.push("- [The Mempool (Unconfirmed)](mempool.md)".to_string());
    if wip_parked.is_empty() {
        final_lines.push("    - [None at this moment. Join us on GitHub!](github.md)".to_string());
    } else {
        for ep in wip_parked {
            let display_num = ep.filename.trim_start_matches('_');
            final_lines.push(format!("    - [{} : {}]({}.md)", display_num, ep.title, ep.filename));
        }
    }

    final_lines.push("\n- [Deep Storage (The Ledger)](archive.md)".to_string());
    if !overflow_numbered.is_empty() {
        final_lines.push("  - [Verified Blocks (Older Episodes)](archive.md#verified-blocks)".to_string());
        for ep in overflow_numbered {
            final_lines.push(format!("      - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }

    let mut in_thematic_zone = false;
    let mut thematic_buffer = Vec::new();
    let num_regex = regex::Regex::new(r"\\d+\\.md").unwrap();
    let skip_strings = ["# WIP", "# Archive", "# Repository", "parked.md", "mempool.md", "Deep Storage", "The Network", "Verified Blocks", "Older Episodes", "github.md"];
    
    for line in original_content.lines() {
        if line.contains("<!-- RECENT_END -->") { in_thematic_zone = true; continue; }
        if in_thematic_zone {
            let mut skip = false;
            for s in &skip_strings {
                if line.contains(s) { skip = true; break; }
            }
            if skip { continue; }
            if num_regex.is_match(line) { continue; }
            if thematic_buffer.is_empty() && line.trim().is_empty() { continue; }
            thematic_buffer.push(line.to_string());
        }
    }
    final_lines.extend(thematic_buffer);
    std::fs::write(summary_path, final_lines.join("\n"))?;
    
    // Create mempool.md and archive.md
    let mempool_content = format!("# The Mempool (Unconfirmed Research)\n\nIn a blockchain, the mempool is where transactions wait to be verified. Here, the Mempool contains our raw, unconfirmed ideas. These episodes are currently being researched, debated, and refined. We invite you to act as a validating node—review the research on our GitHub and email your consensus or objections to amj@shutri.com before we mine the next block.\n\n### Offline Access & Contribution\nTo work on these episodes locally, clone the repository:\n\n``bash\ngit clone https://github.com/ashutoshmjain/deepDive.git\n```\n");
    std::fs::write("src/mempool.md", mempool_content)?;

    let archive_content = format!("# Deep Storage (The Immutable Ledger)\n\nWhile our Progressive Web App seamlessly synchronizes this entire repository for full offline access, the sheer volume of our research can become overwhelming to navigate daily.\n\nTo keep your reading interface clean and focused, the main sidebar only displays the 'Tip of the Chain'—our 21 most recently mined blocks.\n\nEverything else is organized here in Deep Storage. This ledger contains our complete, immutable history. You can expand the folders in the sidebar to browse older **Verified Blocks**, or explore the unnumbered **Genesis Concepts** that built the foundation of our current research framework.\n\n### Collaboration & Offline Access\nFor full offline access to the entire history, or to collaborate on research, please clone our GitHub repository:\n\n```bash\ngit clone https://github.com/ashutoshmjain/deepDive.git\n```\n");
    std::fs::write("src/archive.md", archive_content)?;
    
    Ok(())
}
"""

def repl_func(caps):
    return new_summary_func

content = summary_func_pattern.sub(repl_func, content)

with open("crate/src/main.rs", "w") as f:
    f.write(content)