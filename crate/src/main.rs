//! # md-publish (The Ingestion Layer)
//!
//! A professional, modular asset ingestion bridge for `mdbook`. This crate serves 
//! as the **Ingestion Layer** within an autonomous **Research-to-Publish Workflow**.

mod sanitizer;

use anyhow::{Result};
use glob::glob;
use std::path::PathBuf;
use std::process::Command;
use serde::{Deserialize};
use std::collections::BTreeMap;

#[derive(Debug, Deserialize)]
struct IngestConfig {
    downloads_path: Option<String>,
    text_source: Option<String>,
    image_source: Option<String>,
    video_source: Option<String>,
    lightning_address: Option<String>,
    title_word_limit: Option<usize>,
    recent_window_size: Option<usize>,
    podcast_html: Option<String>,
    visual_html: Option<String>,
}

#[derive(Debug, Deserialize)]
struct BookConfig {
    wip_threshold: Option<u32>, // The episode number that ends Block 1
    preprocessor: Option<PreprocessorConfig>,
}

#[derive(Debug, Deserialize)]
struct PreprocessorConfig {
    ingest: Option<IngestConfig>,
}

#[derive(Debug, Clone)]
struct EpisodeEntry {
    number: Option<u32>,
    filename: String,
    title: String,
    mtime: std::time::SystemTime,
}

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() > 1 && args[1] == "supports" { return Ok(()); }
    if args.len() > 1 && args[1] == "doctor" { return run_doctor(); }

    let config_content = std::fs::read_to_string("book.toml").unwrap_or_default();
    let book_config: BookConfig = toml::from_str(&config_content).unwrap_or(BookConfig { wip_threshold: Some(240), preprocessor: None });
    let ingest_config = book_config.preprocessor.and_then(|p| p.ingest).unwrap_or(IngestConfig {
        downloads_path: Some("/mnt/c/Users/ashut/Downloads".to_string()),
        text_source: None,
        image_source: None,
        video_source: None,
        lightning_address: Some("shutosha@primal.net".to_string()),
        title_word_limit: Some(5),
        recent_window_size: Some(21),
        podcast_html: None,
        visual_html: None,
    });

    let mut number = None;
    let mut do_text = false;
    let mut do_image = false;
    let mut do_video = false;
    let mut do_park = None;
    let mut do_unpark = None;
    let mut do_list_parked = false;
    let mut title_override = None;
    let mut source = ingest_config.downloads_path.clone().unwrap_or_else(|| "/mnt/c/Users/ashut/Downloads".to_string());

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--text" => do_text = true,
            "--image" => do_image = true,
            "--video" => do_video = true,
            "--park" => { if i + 1 < args.len() { do_park = Some(args[i+1].clone()); i += 1; } },
            "--unpark" => { if i + 2 < args.len() { do_unpark = Some((args[i+1].clone(), args[i+2].clone())); i += 2; } },
            "--list-parked" => do_list_parked = true,
            "-t" | "--title" => { if i + 1 < args.len() { title_override = Some(args[i+1].as_str()); i += 1; } },
            "-s" | "--source" => { if i + 1 < args.len() { source = args[i+1].to_string(); i += 1; } },
            num if num.chars().all(|c| c.is_digit(10)) => number = Some(num.to_string()),
            _ => {}
        }
        i += 1;
    }

    if do_list_parked { return list_parked(); }
    if let Some(num) = do_park { return park_episode(&num, &ingest_config); }
    if let Some((old_num, new_num)) = do_unpark { return unpark_episode(&old_num, &new_num, &ingest_config); }

    if let Some(num) = number {
        if do_text { 
            let text_src = ingest_config.text_source.clone().unwrap_or(source.clone());
            ingest_text(&num, &text_src, title_override, &ingest_config)?; 
        }
        if do_image { 
            let image_src = ingest_config.image_source.clone().unwrap_or(source.clone());
            ingest_image(&num, &image_src, &ingest_config)?; 
        }
        if do_video { 
            let video_src = ingest_config.video_source.clone().unwrap_or(source.clone());
            ingest_video(&num, &video_src, &ingest_config)?; 
        }
        update_summary(&ingest_config)?;
    } else {
        let mut input = String::new();
        std::io::Read::read_to_string(&mut std::io::stdin(), &mut input)?;
        let (_ctx, book) = mdbook_preprocessor::parse_input(input.as_bytes())?;
        let output_json = serde_json::to_string(&book)?;
        print!("{}", output_json);
    }
    Ok(())
}

fn ingest_text(number: &str, source: &str, title: Option<&str>, config: &IngestConfig) -> Result<()> {
    eprintln!("📖 Ingesting text for episode {}...", number);
    let mut files: Vec<PathBuf> = Vec::new();
    for ext in &["json", "rs", "md"] {
        let pattern = format!("{}/*.{}", source, ext);
        if let Ok(paths) = glob(&pattern) {
            for path in paths.filter_map(Result::ok) {
                let filename = path.file_name().unwrap().to_str().unwrap();
                if !["SUMMARY.md", "cover.md"].contains(&filename) { files.push(path); }
            }
        }
    }
    files.sort_by(|a, b| std::fs::metadata(b).unwrap().modified().unwrap().cmp(&std::fs::metadata(a).unwrap().modified().unwrap()));
    if let Some(path) = files.first() {
        eprintln!("📄 Found source: {}", path.display());
        let content = std::fs::read_to_string(path)?;
        let hardened = sanitizer::process_content(content, number, title, config.title_word_limit.unwrap_or(5));
        std::fs::write(format!("src/{}.md", number), hardened)?;
        eprintln!("✅ Ingested text to src/{}.md", number);
    }
    Ok(())
}

fn update_summary(config: &IngestConfig) -> Result<()> {
    let summary_path = "src/SUMMARY.md";
    
    // Pivot and Block Size logic
    let pivot = 220;
    let block_size = 21;
    
    let mut all_files = Vec::new();
    let mut wip_parked = Vec::new();
    
    let pattern = "src/*.md";
    for entry in glob(pattern)? {
        if let Ok(path) = entry {
            let filename = path.file_name().unwrap().to_str().unwrap();
            if ["SUMMARY.md", "cover.md", "archive.md", "parked.md", "vault.md", "mempool.md", "github.md", "current.md"].contains(&filename) { continue; }
            let base = filename.trim_end_matches(".md").trim();
            let md_content = std::fs::read_to_string(&path)?;
            let h1_regex = regex::Regex::new(r"(?m)^#\s+(?:(?:\d+)\s*[:\s]*)?\s*(.*)$").unwrap();
            let title = if let Some(caps) = h1_regex.captures(&md_content) {
                caps.get(1).unwrap().as_str().trim().to_string()
            } else { "Untitled".to_string() };
            let mtime = std::fs::metadata(&path)?.modified()?;
            let number = base.parse::<u32>().ok();
            
            if filename.starts_with('_') {
                wip_parked.push(EpisodeEntry { number: base.trim_start_matches('_').parse().ok(), filename: base.to_string(), title, mtime });
            } else {
                all_files.push(EpisodeEntry { number, filename: base.to_string(), title, mtime });
            }
        }
    }

    // Sort WIP
    wip_parked.sort_by(|a, b| b.mtime.cmp(&a.mtime));

    // Calculate Blocks
    // Current Block = Max Block ID
    // All others = Deep Storage
    let mut block_map: BTreeMap<i32, Vec<EpisodeEntry>> = BTreeMap::new();
    let mut thematic_episodes = Vec::new();

    for ep in all_files {
        if let Some(num) = ep.number {
            let block_id = ((num as i32 - pivot) / block_size) + 1;
            block_map.entry(block_id).or_insert_with(Vec::new).push(ep);
        } else {
            thematic_episodes.push(ep);
        }
    }

    let current_block_id = block_map.keys().last().cloned().unwrap_or(2);
    let mut blocks: Vec<_> = block_map.into_iter().collect();
    blocks.sort_by(|a, b| b.0.cmp(&a.0));

    eprintln!("𓄊 Indexer: Current Block ID: {}, Blocks found: {}", current_block_id, blocks.len());

    let original_content = std::fs::read_to_string(summary_path)?;
    let mut final_lines = Vec::new();
    
    for line in original_content.lines() {
        if line.contains("- [The Mempool") || line.contains("- [Current Block") || line.contains("- [Deep Storage") || line.contains("<!-- RECENT_START -->") { break; }
        final_lines.push(line.to_string());
    }

    // 1. Section: The Mempool
    final_lines.push("\n- [mempool](mempool.md)".to_string());
    if wip_parked.is_empty() {
        final_lines.push("    - [None at this moment. Join us on GitHub!](github.md)".to_string());
    } else {
        for ep in wip_parked {
            let display_num = ep.number.map(|n| n.to_string()).unwrap_or_else(|| ep.filename.clone());
            final_lines.push(format!("    - [{} : {}]({}.md)", display_num, ep.title, ep.filename));
        }
    }

    // 2. Section: Current Block
    final_lines.push("\n<!-- RECENT_START -->".to_string());
    final_lines.push("- [block template](current.md)".to_string());
    if let Some((id, eps)) = blocks.iter_mut().find(|(id, _)| *id == current_block_id) {
        eps.sort_by(|a, b| b.number.unwrap().cmp(&a.number.unwrap()));
        for ep in eps {
            final_lines.push(format!("    - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }
    final_lines.push("<!-- RECENT_END -->".to_string());

    // 3. Section: Deep Storage
    final_lines.push("\n- [chain](archive.md)".to_string());
    for (id, mut eps) in blocks {
        if id == current_block_id { continue; }
        final_lines.push(format!("    - [block {}]()", id));
        eps.sort_by(|a, b| b.number.unwrap().cmp(&a.number.unwrap()));
        for ep in eps {
            final_lines.push(format!("        - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }

    // 4. Append Thematic Heritage
    let mut in_thematic_zone = false;
    let mut thematic_buffer = Vec::new();
    let num_regex = regex::Regex::new(r"\d+\.md").unwrap();
    let skip_strings = ["# WIP", "# Archive", "# Repository", "parked.md", "mempool.md", "Deep Storage", "The Network", "Verified Blocks", "Older Episodes", "github.md", "# Recent Blocks", "# The Mempool", "- [The Mempool", "Current Block", "current.md", "- [The Archive", "Block ", "- [Deep Storage"];
    
    for line in original_content.lines() {
        if line.contains("<!-- RECENT_END -->") { in_thematic_zone = true; continue; }
        if in_thematic_zone {
            let mut skip = false;
            for s in &skip_strings {
                if line.contains(s) { skip = true; break; }
            }
            if skip { continue; }
            if num_regex.is_match(line) { continue; }
            
            // Normalize indentation
            let mut mod_line = line.to_string();
            if mod_line.starts_with("  - [") && !mod_line.starts_with("    - [") {
                mod_line = mod_line.replacen("  - [", "    - [", 1);
            }
            if mod_line.starts_with("      - [") && !mod_line.starts_with("        - [") {
                mod_line = mod_line.replacen("      - [", "        - [", 1);
            }
            
            if thematic_buffer.is_empty() && mod_line.trim().is_empty() { continue; }
            thematic_buffer.push(mod_line);
        }
    }
    final_lines.extend(thematic_buffer);
    std::fs::write(summary_path, final_lines.join("\n"))?;
    
    // Create core pages
    let mempool_content = format!("# The Mempool (Unconfirmed Research)\n\nIn a blockchain, the mempool is where transactions wait to be verified. Here, the Mempool contains our raw, unconfirmed ideas. These episodes are currently being researched, debated, and refined. We invite you to act as a validating node—review the research on our GitHub and email your consensus or objections to amj@shutri.com before we mine the next block.\n\n### Offline Access & Contribution\nTo work on these episodes locally, clone the repository:\n\n```bash\ngit clone https://github.com/ashutoshmjain/deepDive.git\n```\n");
    std::fs::write("src/mempool.md", mempool_content)?;

    let archive_content = format!("# Deep Storage (The Immutable Ledger)\n\nEverything here is organized in Deep Storage. This ledger contains our complete, immutable history. You can expand the folders in the sidebar to browse older **Verified Blocks**, or explore the unnumbered **Genesis Concepts** that built the foundation of our current research framework.\n\n### Collaboration & Offline Access\nFor full offline access to the entire history, or to collaborate on research, please clone our GitHub repository:\n\n```bash\ngit clone https://github.com/ashutoshmjain/deepDive.git\n```\n");
    std::fs::write("src/archive.md", archive_content)?;
    
    let current_content = format!("# Current Block\n\nThis block contains the active research episodes, instantly available for offline reading in the Progressive Web App. Once this block reaches 21 episodes, it is mined and moved to Deep Storage.\n");
    std::fs::write("src/current.md", current_content)?;

    std::fs::write("src/github.md", "# Join us on GitHub\n\n[Click here to visit the repository](https://github.com/ashutoshmjain/deepDive)")?;
    Ok(())
}

fn ingest_image(number: &str, source: &str, _config: &IngestConfig) -> Result<()> {
    eprintln!("🎨 Ingesting image for episode {}...", number);
    let img_dir = "src/img";
    std::fs::create_dir_all(img_dir)?;
    let mut images: Vec<PathBuf> = glob(&format!("{}/*{}*.png", source, number))?.filter_map(Result::ok).collect();
    images.sort_by(|a, b| std::fs::metadata(b).unwrap().modified().unwrap().cmp(&std::fs::metadata(a).unwrap().modified().unwrap()));
    if let Some(path) = images.first() {
        let dest = format!("{}/{}.png", img_dir, number);
        if path.as_path() != std::path::Path::new(&dest) { std::fs::copy(path, &dest)?; }
    }
    Ok(())
}

fn ingest_video(number: &str, source: &str, _config: &IngestConfig) -> Result<()> {
    eprintln!("🎬 Ingesting video for episode {}...", number);
    let vid_dir = "src/vid";
    std::fs::create_dir_all(vid_dir)?;
    let pattern = format!("{}/*{}*.mp4", source, number);
    if let Ok(paths) = glob(&pattern) {
        for path in paths.filter_map(Result::ok) {
            let filename = path.file_name().unwrap().to_str().unwrap();
            std::fs::copy(&path, format!("{}/{}", vid_dir, filename))?;
        }
    }
    Ok(())
}

fn run_doctor() -> Result<()> {
    if let Ok(out) = Command::new("mdbook").arg("--version").output() { eprintln!("✅ mdbook: {}", String::from_utf8_lossy(&out.stdout).trim()); }
    Ok(())
}

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
    if !videos.is_empty() { anyhow::bail!("Episode is immutable"); }
    let src = format!("src/{}.md", number);
    if std::path::Path::new(&src).exists() {
        std::fs::rename(&src, format!("src/_{}.md", number))?;
        update_summary(config)?; 
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