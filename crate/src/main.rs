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

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    
    if args.len() > 1 && args[1] == "supports" {
        return Ok(());
    }

    if args.len() > 1 && args[1] == "doctor" {
        return run_doctor();
    }

    // Load config from book.toml
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
            "--park" => {
                if i + 1 < args.len() {
                    do_park = Some(args[i+1].clone());
                    i += 1;
                }
            },
            "--unpark" => {
                if i + 2 < args.len() {
                    do_unpark = Some((args[i+1].clone(), args[i+2].clone()));
                    i += 2;
                }
            },
            "--list-parked" => do_list_parked = true,
            "-t" | "--title" => {
                if i + 1 < args.len() {
                    title_override = Some(args[i+1].as_str());
                    i += 1;
                }
            },
            "-s" | "--source" => {
                if i + 1 < args.len() {
                    source = args[i+1].to_string();
                    i += 1;
                }
            },
            num if num.chars().all(|c| c.is_digit(10)) => number = Some(num.to_string()),
            _ => {}
        }
        i += 1;
    }

    if do_list_parked {
        return list_parked();
    }

    if let Some(num) = do_park {
        return park_episode(&num, &ingest_config);
    }

    if let Some((old_num, new_num)) = do_unpark {
        return unpark_episode(&old_num, &new_num, &ingest_config);
    }

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
    } else {
        // Standard preprocessor mode
        let mut input = String::new();
        std::io::Read::read_to_string(&mut std::io::stdin(), &mut input)?;
        
        // Use the mdbook_preprocessor crate to parse correctly for 0.5.x
        let (_ctx, book) = mdbook_preprocessor::parse_input(input.as_bytes())?;
        
        // Serialize and output the Book object
        let output_json = serde_json::to_string(&book)?;
        print!("{}", output_json);
    }

    Ok(())
}

fn ingest_text(number: &str, source: &str, title: Option<&str>, config: &IngestConfig) -> Result<()> {
    eprintln!("📖 Ingesting text for episode {}...", number);
    let mut files: Vec<PathBuf> = Vec::new();
    
    // Support .json, .rs, and .md
    for ext in &["json", "rs", "md"] {
        let pattern = format!("{}/*.{}", source, ext);
        if let Ok(paths) = glob(&pattern) {
            for path in paths.filter_map(Result::ok) {
                let filename = path.file_name().unwrap().to_str().unwrap();
                if !["SUMMARY.md", "cover.md"].contains(&filename) {
                    files.push(path);
                }
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
        
        // Sync SUMMARY.md
        if let Err(e) = update_summary(config) {
            eprintln!("⚠️ Failed to update SUMMARY.md: {}", e);
        } else {
            eprintln!("✅ Synchronized SUMMARY.md");
        }
    }
    Ok(())
}

#[derive(Debug, Clone)]
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
        final_lines.push("- [None at this moment. Join us on GitHub!](github.md)".to_string());
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

fn ingest_image(number: &str, source: &str, _config: &IngestConfig) -> Result<()> {
    eprintln!("🎨 Ingesting image for episode {}...", number);
    let img_dir = "src/img";
    std::fs::create_dir_all(img_dir)?;
    let mut images: Vec<PathBuf> = glob(&format!("{}/*{}*.png", source, number))?.filter_map(Result::ok).collect();
    images.sort_by(|a, b| std::fs::metadata(b).unwrap().modified().unwrap().cmp(&std::fs::metadata(a).unwrap().modified().unwrap()));

    if let Some(path) = images.first() {
        let dest = format!("{}/{}.png", img_dir, number);
        // Avoid truncating if copying from within the same folder (redundant check but safe)
        if path.as_path() != std::path::Path::new(&dest) {
            std::fs::copy(path, &dest)?;
        }
        eprintln!("✅ Ingested cover art to {} (archived, no Markdown injection)", dest);
    }
    Ok(())
}

fn ingest_video(number: &str, source: &str, _config: &IngestConfig) -> Result<()> {
    eprintln!("🎬 Ingesting video for episode {}...", number);
    
    let vid_dir = "src/vid";
    std::fs::create_dir_all(vid_dir)?;

    // 1. Migration from Downloads
    let pattern = format!("{}/*{}*.mp4", source, number);
    if let Ok(paths) = glob(&pattern) {
        for path in paths.filter_map(Result::ok) {
            let filename = path.file_name().unwrap().to_str().unwrap();
            let dest = format!("{}/{}", vid_dir, filename);
            std::fs::copy(&path, &dest)?;
            eprintln!("✅ Migrated: {}", filename);
        }
    }

    // 2. Discover LOCAL videos for this episode only
    let mut local_vids = Vec::new();
    if let Ok(paths) = glob(&format!("{}/{}*.mp4", vid_dir, number)) {
        for path in paths.filter_map(Result::ok) {
            local_vids.push(path);
        }
    }

    // Intelligent Sequence Sorting (Bucket Logic):
    // Priority 0: Base episode or Intro (241.mp4, 241-Intro.mp4)
    // Priority 1: All indexed files sorted as strings (241-2, 241-21, 241-3)
    local_vids.sort_by(|a, b| {
        let get_prio_and_key = |path: &std::path::PathBuf| -> (i32, String) {
            let filename = path.file_name().unwrap().to_str().unwrap().to_lowercase();
            let base = filename.strip_suffix(".mp4").unwrap_or(&filename);
            
            let suffix = if base.starts_with(number) {
                &base[number.len()..]
            } else {
                base
            };

            if suffix.is_empty() || suffix == "-intro" || suffix == "-0" {
                (0, filename)
            } else {
                // Return Priority 1 and the suffix itself for string-based bucket sorting
                (1, filename)
            }
        };

        let val_a = get_prio_and_key(a);
        let val_b = get_prio_and_key(b);
        val_a.cmp(&val_b)
    });

    if local_vids.is_empty() {
        eprintln!("⚠️ No videos found for episode {}", number);
        return Ok(());
    }

    // 3. Generate HTML (Visual Socials BELOW scroll)
    let visual_links = r#"
<center><a href="https://www.tiktok.com/@shutoshabot" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">▶ TikTok ◀</a><a href="https://www.instagram.com/shutoshabot/" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">◈ Instagram ◈</a><a href="https://www.youtube.com/playlist?list=PLIX4sFsmu37q8rU8HKTLhdLPZQadcvx-K" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">⫸ YouTube ⫷</a></center>
"#;

    let mut html = String::new();
    html.push_str("\n<!-- VIDEO_STRIP_START -->\n");
    
    if local_vids.len() == 1 {
        let path = &local_vids[0];
        let filename = path.file_name().unwrap().to_str().unwrap();
        html.push_str("<div class=\"video-single-container\" style=\"display: flex; justify-content: center; width: 100%; margin: 20px 0;\">\n");
        html.push_str(&format!(
            r#"  <div style="width: 100%; max-width: 1000px; position: relative; border-radius: 12px; overflow: hidden; background: #000; aspect-ratio: 16/9; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
    <video src="vid/{}" style="width: 100%; height: 100%; object-fit: contain;" playsinline loop preload="auto" muted autoplay></video>
    <button class="vid-toggle" onclick="window.oph_play_toggle(this)" style="position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.8); color: white; border: 2px solid white; border-radius: 50%; width: 50px; height: 50px; cursor: pointer; font-size: 24px; z-index: 100; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1.0)'">🔇</button>
  </div>
"#, filename));
        html.push_str("</div>\n");
    } else {
        html.push_str("<div class=\"video-carousel-container\" style=\"display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 15px; padding: 20px 0; scroll-behavior: smooth;\">\n");
        for path in local_vids.iter() {
            let filename = path.file_name().unwrap().to_str().unwrap();
            html.push_str(&format!(
                r#"  <div style="flex: 0 0 60%; scroll-snap-align: center; position: relative; border-radius: 12px; overflow: hidden; background: #000; aspect-ratio: 1/1; display: flex; flex-direction: column; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    <video src="vid/{}" style="width: 100%; height: 85%; object-fit: contain;" playsinline loop preload="auto" muted autoplay></video>
    <div style="height: 15%; background: #1a1a1a; color: #ccc; display: flex; align-items: center; justify-content: center; font-family: monospace; font-size: 12px; border-top: 1px solid #333;">{}</div>
    <button class="vid-toggle" onclick="window.oph_play_toggle(this)" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; border: 2px solid white; border-radius: 50%; width: 45px; height: 45px; cursor: pointer; font-size: 22px; z-index: 100;">🔇</button>
  </div>
"#, filename, filename.trim_end_matches(".mp4")));
        }
        html.push_str("</div>\n");
    }
    html.push_str(&format!("{}\n", visual_links));

    html.push_str(r#"<script>
window.oph_play_toggle = function(btn) {
  const parent = btn.parentElement;
  const vid = parent.querySelector('video');
  const container = btn.closest('.video-carousel-container, .video-single-container');
  
  if (vid.muted || vid.paused) {
    if (container) {
      container.querySelectorAll('video').forEach(v => {
        if (v !== vid) {
          v.pause();
          v.muted = true;
          const otherBtn = v.parentElement.querySelector('.vid-toggle');
          if (otherBtn) otherBtn.innerText = '🔇';
        }
      });
    }
    vid.muted = false;
    vid.volume = 1.0;
    vid.play().then(() => { btn.innerText = '🔊'; }).catch(e => console.error('Play failed:', e));
  } else {
    vid.pause();
    vid.muted = true;
    btn.innerText = '🔇';
  }
};

(function() {
  const init = () => {
    const vids = document.querySelectorAll('.video-carousel-container video, .video-single-container video');
    vids.forEach(v => { 
      v.muted = true; 
      v.play().catch(() => {}); 
    });
  };
  if (document.readyState === 'complete') { init(); }
  else { window.addEventListener('load', init); }
})();
</script>
"#);

    html.push_str("<!-- VIDEO_STRIP_END -->\n\n");

    // 4. Inject into THIS file only
    let path = format!("src/{}.md", number);
    let content = std::fs::read_to_string(&path)?;
    
    // Always strip existing block to ensure clean re-placement at the top
    let clean_content = if let (Some(s), Some(e)) = (content.find("<!-- VIDEO_STRIP_START -->"), content.find("<!-- VIDEO_STRIP_END -->")) {
        let mut c = String::new();
        c.push_str(&content[..s]);
        c.push_str(&content[e + "<!-- VIDEO_STRIP_END -->".len()..]);
        c
    } else {
        content.clone()
    };

    // Always insert after H1
    let mut final_content = String::new();
    if let Some(h1_end) = clean_content.find('\n').map(|i| i + 1) {
        final_content.push_str(&clean_content[..h1_end]);
        final_content.push_str(&html);
        final_content.push_str(&clean_content[h1_end..]);
    } else {
        final_content.push_str(&html);
        final_content.push_str(&clean_content);
    }

    std::fs::write(&path, final_content)?;
    eprintln!("✅ Updated infographic scroll in {}", path);

    Ok(())
}

fn run_doctor() -> Result<()> {
    match Command::new("mdbook").arg("--version").output() {
        Ok(out) => eprintln!("✅ mdbook: {}", String::from_utf8_lossy(&out.stdout).trim()),
        Err(_) => eprintln!("❌ mdbook: Not found"),
    }
    match Command::new("mdbook-katex").arg("--version").output() {
        Ok(out) => eprintln!("✅ mdbook-katex: {}", String::from_utf8_lossy(&out.stdout).trim()),
        Err(_) => eprintln!("❌ mdbook-katex: Not found"),
    }
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
