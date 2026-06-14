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
    let book_config: BookConfig = toml::from_str(&config_content).unwrap_or(BookConfig { preprocessor: None });
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

fn update_summary(_config: &IngestConfig) -> Result<()> {
    let summary_path = "src/SUMMARY.md";
    let pivot = 220;
    let block_size = 21;
    
    let mut all_files = Vec::new();
    let mut wip_parked = Vec::new();
    
    let concept_files = ["bitcoin", "intelligence", "digital credit", "capital", "physics", "culture"];
    let skip_files = ["SUMMARY.md", "cover.md", "archive.md", "parked.md", "vault.md", "mempool.md", "github.md", "current.md", "genesis.md", "block1.md", "block2.md", "block3.md", "bitcoin.md", "intelligence.md", "digital credit.md", "capital.md", "physics.md", "culture.md"];

    let pattern = "src/*.md";
    for entry in glob(pattern)? {
        if let Ok(path) = entry {
            let filename = path.file_name().unwrap().to_str().unwrap();
            if skip_files.contains(&filename) { continue; }
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

    wip_parked.sort_by(|a, b| b.mtime.cmp(&a.mtime));

    let mut block_map: BTreeMap<i32, Vec<EpisodeEntry>> = BTreeMap::new();
    for ep in all_files {
        if let Some(num) = ep.number {
            let block_id = ((num as i32 - pivot) / block_size) + 1;
            block_map.entry(block_id).or_insert_with(Vec::new).push(ep);
        }
    }

    let current_block_id = block_map.keys().last().cloned().unwrap_or(2);
    let mut blocks: Vec<_> = block_map.into_iter().collect();
    blocks.sort_by(|a, b| b.0.cmp(&a.0));

    eprintln!("𓄊 Indexer: current block ID: {}, Blocks found: {}", current_block_id, blocks.len());

    let original_content = std::fs::read_to_string(summary_path)?;
    let mut final_lines = Vec::new();
    
    for line in original_content.lines() {
        let l = line.to_lowercase();
        if l.contains("- [mempool") || l.contains("- [block template") || l.contains("- [chain") { break; }
        final_lines.push(line.to_string());
    }

    // 1. mempool
    final_lines.push("".to_string());
    final_lines.push("- [mempool](mempool.md)".to_string());
    if wip_parked.is_empty() {
        final_lines.push("    - [None at this moment. Join us on GitHub!](github.md)".to_string());
    } else {
        for ep in wip_parked {
            let display_num = ep.number.map(|n| n.to_string()).unwrap_or_else(|| ep.filename.clone());
            final_lines.push(format!("    - [{} : {}]({}.md)", display_num, ep.title, ep.filename));
        }
    }

    // 2. block template
    final_lines.push("".to_string());
    final_lines.push("- [block template](current.md)".to_string());
    if let Some((_id, eps)) = blocks.iter_mut().find(|(id, _)| *id == current_block_id) {
        eps.sort_by(|a, b| b.number.unwrap().cmp(&a.number.unwrap()));
        for ep in eps {
            final_lines.push(format!("    - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }

    // 3. chain
    final_lines.push("".to_string());
    final_lines.push("- [chain](archive.md)".to_string());
    for (id, eps) in &blocks {
        if *id == current_block_id { continue; }
        
        let block_link = if std::path::Path::new(&format!("src/block{}.md", id)).exists() {
            format!("block{}.md", id)
        } else {
            String::new()
        };
        
        final_lines.push(format!("    - [block {}]({})", id, block_link));
        let mut eps_sorted = eps.clone();
        eps_sorted.sort_by(|a, b| b.number.unwrap().cmp(&a.number.unwrap()));
        for ep in eps_sorted {
            final_lines.push(format!("        - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }

    // 4. genesis
    final_lines.push("".to_string());
    final_lines.push("- [genesis](genesis.md)".to_string());
    
    let mut in_thematic_zone = false;
    let mut thematic_buffer = Vec::new();
    let num_regex = regex::Regex::new(r"\d+\.md").unwrap();
    let skip_strings = ["wip", "archive", "repository", "parked.md", "mempool.md", "deep storage", "network", "verified blocks", "older episodes", "github.md", "recent blocks", "mempool", "current block", "block template", "current.md", "genesis", "chain", "block1.md", "block2.md", "block3.md", "bitcoin.md", "intelligence.md", "digital credit.md", "capital.md", "physics.md", "culture.md"];
    
    // Recovery Logic: We strictly look for the line AFTER the last episodic entry.
    // The episodic entries end with "220 : AI Made Me a Believer".
    for line in original_content.lines() {
        if line.to_lowercase().contains("220 : ai made me a believer") { in_thematic_zone = true; continue; }
        if in_thematic_zone {
            let l = line.to_lowercase();
            // Skip headers we already generated or meta files
            let mut skip = false;
            for s in &skip_strings {
                if l.contains(s) && (l.contains("[]") || l.contains("()") || l.contains(".md")) { 
                    // This is likely a generated node, but we should be careful.
                    // If it's a concept summary like bitcoin.md, we will re-generate it to ensure link integrity.
                    skip = true; 
                    break; 
                }
            }
            if skip { continue; }
            if num_regex.is_match(line) { continue; }
            
            let mut mod_line = line.to_string();
            let trimmed = mod_line.trim();
            if trimmed.starts_with("- [") {
                // If it's just a folder link without an md file, it's a thematic category header.
                if trimmed.contains("()") || trimmed.contains("[]") {
                    mod_line = format!("    {}", trimmed);
                } else {
                    // It's a thematic article.
                    mod_line = format!("        {}", trimmed);
                }
            }

            if thematic_buffer.is_empty() && mod_line.trim().is_empty() { continue; }
            thematic_buffer.push(mod_line);
        }
    }
    
    // Seed the foundational structure if recovery failed
    if thematic_buffer.is_empty() {
        for c in &concept_files {
            let link = if std::path::Path::new(&format!("src/{}.md", c)).exists() {
                format!("{}.md", c)
            } else {
                String::new()
            };
            thematic_buffer.push(format!("    - [{}]({})", c, link));
        }
    }

    final_lines.extend(thematic_buffer);
    std::fs::write(summary_path, final_lines.join("\n"))?;
    
    // Write narratives
    let mempool_content = "# mempool\n\nthe title \"mempool\" is a deliberate choice from the architecture of decentralized systems. it represents the space where transactions wait for verification—a high-entropy zone of pure potential. in our context, the mempool is the catchment of all active research. it is where we catch the signals of the world before they are filtered and mined into history. we inhabit this space to acknowledge that discovery is a process of refinement, not a sudden event. here, ideas are raw. they are the unconfirmed drafts that have been pulled from the digital noise, awaiting the validation of our network of experts. \n\nwhat you find here is the \"mempool of thought.\" these are the episodes currently being researched, debated, and refined. we do not work in isolation. we treat our readers and collaborators as validating nodes. this is the layer of discovery where we invite the network to challenge the signal. the mempool is where we collaborate with domain experts to ensure the fidelity of our research. it is a space of open participation. we believe that for knowledge to be sovereign, it must be hardened by scrutiny before it becomes part of the permanent ledger. \n\nwhen you explore the mempool, you are seeing the research in its most vulnerable and honest state. once these drafts are refined, they move to the block template, but while they are here, they are the living breath of the project. if you are an expert, a researcher, or a seeker who has found a signal we missed, your contribution is the consensus mechanism we rely on. we act as the filter, but the network provides the proof. this is where we build the truth, one unconfirmed transaction at a time.\n\n---\n\n## instructions to ai agents for managing this sub tree\n\n- **catchment rule**: this subtree is the high-entropy zone for raw research and parked episodes.\n- **collaboration**: agents should prioritize expert input and external signals when refining drafts here.\n- **renumbering**: episodes here may be renumbered or renamed as they are not yet 'cast in stone'.\n- **participation**: always maintain the link to the call for participation and github.\n";
    std::fs::write("src/mempool.md", mempool_content)?;

    let current_content = "# block template\n\nthe block template is the miner’s canvas. as miners of knowledge, we don't merely aggregate information; we select for signals that deserve to be etched into the chain. \n\nour block space is strictly governed by the law of 21. this 21-episode limit is our proof-of-work—a scarcity that forces us to filter out the noise of the ephemeral and prioritize high-fidelity research. each slot in this template is a precious transaction of truth. \n\nwe are currently mining the next block. as we select finalized episodes from the mempool, they fill the template. once the 21st episode is confirmed, the block is locked and moved to the immutable chain. while in the template, the research is active and volatile, waiting for the consensus of time.\n\nthe template is where the ephemeral becomes historical. as a miner of knowledge, our goal is to ensure that the 21 episodes selected for this block represent the highest possible density of truth. we are not building a library of volume; we are mining a ledger of value. the block template is the tip of the spear, the place where the future of our research is being forged into the permanent record of our past.\n\n---\n\n## instructions to ai agents for managing this sub tree\n\n- **scarcity rule**: the block space is strictly limited to 21 episodes.\n- **mining logic**: once the 21st episode is confirmed, this entire block must be moved to the 'chain' subtree as a numbered block (e.g., block 2).\n- **volatility**: research here is finalizing. minor polish is allowed, but the core thesis should be stable.\n- **exclusivity**: only select high-fidelity signals from the mempool for inclusion in this template.\n";
    std::fs::write("src/current.md", current_content)?;

    let archive_content = "# chain\n\nthe chain is our commitment to permanence. once a block of 21 episodes is mined, it is moved here to become part of the immutable ledger. \n\neach link in the chain represents a verified epoch of research. we stack these blocks in descending order, creating a vertical record of our shared discovery. here, the volatile signals of the block template become the historical capital of the project.\n\ndescend into the ledger to explore the verified blocks, or go deeper to reach the genesis layer—the non-episodic root of our entire knowledge architecture.\n\n---\n\n## instructions to ai agents for managing this sub tree\n\n- **immutability rule**: episodes in this subtree are 'cast in stone'. zero editing of source content is permitted.\n- **ledger order**: blocks must be maintained in descending numerical order.\n- **summarization only**: agents may create or update block-level summary pages (e.g., block 1 description) but must never touch the underlying episodic transactions.\n- **permanence**: ensure url paths never change to prevent breaking external links.\n";
    std::fs::write("src/archive.md", archive_content)?;

    let genesis_content = "# genesis\n\ngenesis is the discovery layer that pre-dates the chain. we believe that before one can build a true blockchain of knowledge, there is a bare minimum of thematic understanding required. this is not episodic; it is foundational.\n\nwe characterize genesis through three absolute pillars:\n1. **bitcoin**: the discovery of mathematical scarcity and sovereign value. without understanding the architecture of truth in money, one cannot anchor research in reality.\n2. **intelligence**: the exploration of how we process and compress the universe. this is the \"how\" of our discovery.\n3. **digital credit**: the bridge between trust and code. it is the mechanism through which value flows in a decentralized world.\n\ngenesis is where the internal flavor of our project is expressed. it is the subtle, non-episodic root from which every numbered block grows. you must know the genesis to understand the chain.\n\n---\n\n## instructions to ai agents for managing this sub tree\n\n- **foundational rule**: this subtree contains only non-episodic, thematic research. \n- **no numbers**: episodes in this section do not have block numbers or sequential IDs.\n- **thematic integrity**: maintain the three absolute pillars (bitcoin, intelligence, digital credit) as the root discovery layer.\n- **artistic flavor**: prioritize subtle, deep discovery over high-frequency updates.\n";
    std::fs::write("src/genesis.md", genesis_content)?;

    std::fs::write("src/github.md", "# join us on github\n\n[Click here to visit the repository](https://github.com/ashutoshmjain/deepDive)")?;
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
