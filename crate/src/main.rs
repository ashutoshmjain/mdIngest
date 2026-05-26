//! # mdbook-ingest (The Ingestion Layer)
//!
//! A professional, modular asset ingestion bridge for `mdbook`. This crate serves 
//! as the **Ingestion Layer** within an autonomous **Research-to-Publish Workflow**.
//!
//! ## Agentic Architecture
//! `mdbook-ingest` is designed to operate as a standalone module that can be 
//! triggered by a Research Agent. It handles:
//! 1. **Sanitization**: Transforming raw AI output into hardened Markdown.
//! 2. **Media Management**: Migrating and renaming assets based on a **Master Key** (Episode Number).
//! 3. **Indexing**: Maintaining the book's structure and social/monetization widgets.
//!
//! Currently, the tool includes specialized logic for **Google Gemini Pro** 
//! (Shielded Output stripping), with future support planned for other LLMs 
//! like ChatGPT and Claude.

mod sanitizer;

use clap::{Parser, Subcommand};
use std::process::Command;
use anyhow::{Result, Context};
use glob::glob;
use regex::Regex;
use std::path::PathBuf;
use serde::Deserialize;

#[derive(Deserialize, Default)]
struct BookToml {
    preprocessor: Option<PreprocessorSection>,
}

#[derive(Deserialize, Default)]
struct PreprocessorSection {
    ingest: Option<IngestConfig>,
}

/// Configuration options loaded from `book.toml` under `[preprocessor.ingest]`
#[derive(Deserialize, Default, Clone)]
pub struct IngestConfig {
    pub downloads_path: Option<String>,
    pub lightning_address: Option<String>,
    pub podcast_html: Option<String>,
    pub title_word_limit: Option<usize>,
}

impl IngestConfig {
    pub fn load() -> Self {
        if let Ok(content) = std::fs::read_to_string("book.toml") {
            if let Ok(toml) = toml::from_str::<BookToml>(&content) {
                if let Some(prep) = toml.preprocessor {
                    if let Some(ingest) = prep.ingest {
                        return ingest;
                    }
                }
            }
        }
        Self::default()
    }
}

/// CLI Configuration and Arguments
#[derive(Parser)]
#[command(author, version, about, long_about = None)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Ingest as text (AI-generated Markdown)
    #[arg(long)]
    text: bool,

    /// Ingest as image (Cover Art)
    #[arg(long)]
    image: bool,

    /// Ingest as video (Cinematic Scroll Strip)
    #[arg(long)]
    video: bool,

    /// Episode number (the Master Key)
    #[arg(short, long)]
    number: Option<String>,

    /// Source directory for exports (e.g., Downloads folder)
    #[arg(short, long, default_value = "/mnt/c/Users/ashut/Downloads")]
    source: String,

    /// Title override
    #[arg(short, long)]
    title: Option<String>,
}

/// Available Subcommands
#[derive(Subcommand)]
enum Commands {
    /// Standard mdbook preprocessor handshake
    Supports { renderer: String },
    /// Check system dependencies (mdbook, mdbook-katex, etc.)
    Doctor,
}

fn main() -> Result<()> {
    // 1. Run "Doctor" checks implicitly on every run (except doctor itself)
    let cli = Cli::parse();
    let config = IngestConfig::load();
    
    match &cli.command {
        Some(Commands::Doctor) => {
            return run_doctor();
        }
        _ => {
            // Implicit check: only warn, don't block yet, to allow installation
            if let Err(e) = check_dependencies() {
                eprintln!("⚠️  Dependency Warning: {}", e);
            }
        }
    }

    // 2. Handle Subcommands
    if let Some(command) = cli.command {
        match command {
            Commands::Supports { renderer } => {
                if renderer == "html" {
                    std::process::exit(0);
                } else {
                    std::process::exit(1);
                }
            }
            _ => {}
        }
    }

    let mut source = cli.source.clone();
    
    if let Some(config_path) = &config.downloads_path {
        if cli.source == "/mnt/c/Users/ashut/Downloads" {
            source = config_path.clone();
            eprintln!("📂 Using source from book.toml: {}", source);
        } else {
            eprintln!("💡 Overriding book.toml source with CLI flag: {}", source);
        }
    } else if cli.source != "/mnt/c/Users/ashut/Downloads" {
        eprintln!("📂 Using source from CLI flag: {}", source);
    }

    // 3. Handle Ingestion
    if cli.text {
        if let Some(number) = cli.number {
            ingest_text(&number, &source, cli.title.as_deref(), &config)?;
        } else {
            anyhow::bail!("❌ Error: Episode number (-n, --number) is required.");
        }
    } else if cli.image {
        if let Some(number) = cli.number {
            ingest_image(&number, &source, &config)?;
        } else {
            anyhow::bail!("❌ Error: Episode number (-n, --number) is required.");
        }
    } else if cli.video {
        if let Some(number) = cli.number {
            ingest_video(&number, &source, &config)?;
        } else {
            anyhow::bail!("❌ Error: Episode number (-n, --number) is required.");
        }
    } else if cli.number.is_some() {
        eprintln!("ℹ️  Please specify asset type (e.g., --text or --image)");
    } else {
        // Standard mdbook preprocessor handshake
        let (_ctx, book) = mdbook::preprocess::CmdPreprocessor::parse_input(std::io::stdin())?;
        let json = serde_json::to_string(&book)?;
        print!("{}", json);
    }

    Ok(())
}

/// Orchestrates the ingestion of video assets and generates the Cinematic Scroll Strip.
fn ingest_video(number: &str, source: &str, _config: &IngestConfig) -> Result<()> {
    eprintln!("🎬 Ingesting video for episode {}...", number);
    
    // 1. Discovery & Migration
    let vid_dir = "src/vid";
    std::fs::create_dir_all(vid_dir)?;

    let epi_regex = Regex::new(r"^\d{3}-").unwrap();

    let pattern = format!("{}/*{}*.mp4", source, number);
    if let Ok(paths) = glob(&pattern) {
        for path in paths.filter_map(Result::ok) {
            let filename = path.file_name().unwrap().to_str().unwrap();
            // Strictly enforce ###- pattern for migration
            if epi_regex.is_match(filename) {
                let dest = format!("{}/{}", vid_dir, filename);
                std::fs::copy(&path, &dest)?;
                eprintln!("✅ Migrated: {}", filename);
            }
        }
    }

    // 2. Build the Global Carousel List
    let mut all_vids = Vec::new();
    if let Ok(paths) = glob(&format!("{}/*.mp4", vid_dir)) {
        for path in paths.filter_map(Result::ok) {
            let filename = path.file_name().unwrap().to_str().unwrap();
            // Strictly enforce ###- pattern for the carousel
            if epi_regex.is_match(filename) {
                all_vids.push(path);
            }
        }
    }

    // Sort by episode number (descending)
    all_vids.sort_by(|a, b| {
        let name_a = a.file_name().unwrap().to_str().unwrap();
        let name_b = b.file_name().unwrap().to_str().unwrap();
        name_b.cmp(name_a)
    });

    // 3. Generate HTML Cinematic Scroll Strip
    let mut html = String::new();
    html.push_str("\n<!-- VIDEO_STRIP_START -->\n");
    html.push_str("\n---\n\n### Info Graphics feed from Mosaic.SO\n\n");
    
    // Global Script and Styles
    html.push_str(r#"<style>
  .video-carousel-container video { pointer-events: none; }
  .vid-toggle { z-index: 100 !important; transition: transform 0.1s; }
  .vid-toggle:active { transform: scale(0.9); }
</style>
<script>
  window.oph_toggle = function(btn) {
    const parent = btn.parentElement;
    const vid = parent.querySelector('video');
    const container = btn.closest('.video-carousel-container');
    
    if (vid.paused) {
      container.querySelectorAll('video').forEach(v => {
        v.pause();
        v.muted = true;
        const b = v.parentElement.querySelector('.vid-toggle');
        if (b) b.innerText = '🔇';
      });
      vid.muted = false;
      vid.play();
      btn.innerText = '🔊';
    } else {
      vid.pause();
      vid.muted = true;
      btn.innerText = '🔇';
    }
  };
</script>
"#);

    html.push_str("<div class=\"video-carousel-container\" style=\"display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 15px; padding: 20px 0; scroll-behavior: smooth;\">\n");

    let mut focus_id = None;

    for (i, path) in all_vids.iter().enumerate() {
        let filename = path.file_name().unwrap().to_str().unwrap();
        let is_current = filename.starts_with(number);
        let id = format!("vid-{}", i);
        if is_current && focus_id.is_none() {
            focus_id = Some(id.clone());
        }

        html.push_str(&format!(
            r#"  <div id="{}" style="flex: 0 0 35%; scroll-snap-align: center; position: relative; border-radius: 12px; overflow: hidden; background: #000; aspect-ratio: 1/1; display: flex; flex-direction: column;">
    <video src="vid/{}" style="width: 100%; height: 85%; object-fit: contain; pointer-events: none;" playsinline loop preload="auto"></video>
    <div style="height: 15%; background: #1a1a1a; color: #ccc; display: flex; align-items: center; justify-content: center; font-family: monospace; font-size: 12px; border-top: 1px solid #333;">{}</div>
    <button class="vid-toggle" onclick="oph_toggle(this)" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; border: 2px solid white; border-radius: 50%; width: 35px; height: 35px; cursor: pointer; font-size: 18px; z-index: 100;">🔇</button>
  </div>
"#, id, filename, filename.replace(".mp4", "")));
    }

    html.push_str("</div>\n");

    // Add Scroll-to-Focus and Init Script
    html.push_str(r#"<script>
  window.oph_toggle = function(btn) {
    const parent = btn.parentElement;
    const vid = parent.querySelector('video');
    const container = btn.closest('.video-carousel-container');
    
    if (vid.paused) {
      // 1. Stop and mute all others
      container.querySelectorAll('video').forEach(v => {
        if (v !== vid) {
          v.pause();
          v.muted = true;
          const otherBtn = v.parentElement.querySelector('.vid-toggle');
          if (otherBtn) otherBtn.innerText = '🔇';
        }
      });
      
      // 2. Play and unmute this one
      vid.muted = false;
      vid.volume = 1.0;
      vid.play();
      btn.innerText = '🔊';
    } else {
      vid.pause();
      vid.muted = true;
      btn.innerText = '🔇';
    }
  };

  window.addEventListener('load', () => {
    const container = document.querySelector('.video-carousel-container');
    if (container) {
      container.querySelectorAll('video').forEach(v => { 
        v.muted = true; 
        v.pause(); 
      });
    }
"#);

    if let Some(id) = focus_id {
        html.push_str(&format!(
            r#"    const el = document.getElementById('{}');
"#, "vid-focus-placeholder"));
    }
    
    html.push_str(r#"    if (container && el) {
      const offset = el.offsetLeft - (container.offsetWidth / 2) + (el.offsetWidth / 2);
      container.scrollTo({ left: offset, behavior: 'smooth' });
    }
  });
</script>
"#);
    html.push_str("<!-- VIDEO_STRIP_END -->\n\n");

    // 4. Global Refresh: Inject into ALL Markdown files that have a strip marker
    if let Ok(paths) = glob("src/*.md") {
        for path in paths.filter_map(Result::ok) {
            let mut content = std::fs::read_to_string(&path)?;
            
            if content.contains("<!-- VIDEO_STRIP_START -->") {
                let current_file_num = path.file_stem().unwrap().to_str().unwrap();
                
                // 4.1 Update the Focus for THIS specific file
                let mut local_html = html.clone();
                
                // Find the first video ID for this episode number
                let mut local_focus_id = String::from("vid-0");
                for (i, p) in all_vids.iter().enumerate() {
                    if p.file_name().unwrap().to_str().unwrap().starts_with(current_file_num) {
                        local_focus_id = format!("vid-{}", i);
                        break;
                    }
                }
                local_html = local_html.replace("'vid-focus-placeholder'", &format!("'{}'", local_focus_id));

                // 4.2 Replace the existing strip
                let start_marker = "<!-- VIDEO_STRIP_START -->";
                let end_marker = "<!-- VIDEO_STRIP_END -->";
                if let (Some(s), Some(e)) = (content.find(start_marker), content.find(end_marker)) {
                    content.replace_range(s..e + end_marker.len(), &local_html);
                }

                std::fs::write(&path, content)?;
                eprintln!("✅ Synchronized Global Strip in {}", path.display());
            }
        }
    }

    Ok(())
}

/// Checks if required external tools are available in the PATH.
fn check_dependencies() -> Result<()> {
    // Check mdbook
    let _ = Command::new("mdbook")
        .arg("--version")
        .output()
        .context("mdbook not found in PATH")?;

    // Check mdbook-katex
    let _ = Command::new("mdbook-katex")
        .arg("--version")
        .output()
        .context("mdbook-katex not found in PATH. Please install it with 'cargo install mdbook-katex'")?;

    Ok(())
}

/// Performs a diagnostic check of the local environment and book configuration.
fn run_doctor() -> Result<()> {
    eprintln!("🔍 Checking environment...");

    match Command::new("mdbook").arg("--version").output() {
        Ok(out) => eprintln!("✅ mdbook: {}", String::from_utf8_lossy(&out.stdout).trim()),
        Err(_) => eprintln!("❌ mdbook: Not found"),
    }

    match Command::new("mdbook-katex").arg("--version").output() {
        Ok(out) => eprintln!("✅ mdbook-katex: {}", String::from_utf8_lossy(&out.stdout).trim()),
        Err(_) => eprintln!("❌ mdbook-katex: Not found (Install with 'cargo install mdbook-katex')"),
    }

    if std::path::Path::new("book.toml").exists() {
        if let Ok(toml) = std::fs::read_to_string("book.toml") {
            if toml.contains("preprocessor.ingest") {
                eprintln!("✅ book.toml: Ingestion configured");
            } else {
                eprintln!("⚠️  book.toml: [preprocessor.ingest] section missing");
            }
        }
    }

    Ok(())
}

/// Orchestrates the ingestion of text-based research assets.
fn ingest_text(number: &str, source: &str, title: Option<&str>, config: &IngestConfig) -> Result<()> {
    eprintln!("📖 Ingesting text for episode {}...", number);
    
    // Find the latest .md, .zip, or .rs file
    let md_pattern = format!("{}/*.md", source);
    let zip_pattern = format!("{}/*.zip", source);
    let rs_pattern = format!("{}/*.rs", source);
    
    let mut md_files: Vec<PathBuf> = glob(&md_pattern)?.filter_map(Result::ok)
        .filter(|p| {
            let filename = p.file_name().unwrap().to_str().unwrap();
            !["SUMMARY.md", "cover.md", "README.md"].contains(&filename)
        }).collect();
        
    let mut zip_files: Vec<PathBuf> = glob(&zip_pattern)?.filter_map(Result::ok).collect();
    let mut rs_files: Vec<PathBuf> = glob(&rs_pattern)?.filter_map(Result::ok).collect();
    
    let mut all_files = Vec::new();
    all_files.append(&mut md_files);
    all_files.append(&mut zip_files);
    all_files.append(&mut rs_files);

    all_files.sort_by(|a, b| {
        let metadata_a = std::fs::metadata(a).unwrap();
        let metadata_b = std::fs::metadata(b).unwrap();
        metadata_b.modified().unwrap().cmp(&metadata_a.modified().unwrap())
    });

    let latest_file = all_files.first().context(format!("❌ No .md, .zip, or .rs files found in {}", source))?;
    eprintln!("📄 Found export: {:?}", latest_file.file_name().unwrap());

    let content = if latest_file.extension().unwrap() == "zip" {
        extract_html_from_zip(latest_file)?
    } else {
        std::fs::read_to_string(latest_file)?
    };

    let processed = sanitizer::process_content(content, number, title, config.title_word_limit.unwrap_or(5));

    let dest_path = format!("src/{}.md", number);
    std::fs::write(&dest_path, processed)?;
    eprintln!("✅ Saved text to: {}", dest_path);

    update_summary(number, &dest_path)?;
    
    Ok(())
}

/// Legacy/Fallback: Extracts HTML from ZIP.
fn extract_html_from_zip(zip_path: &PathBuf) -> Result<String> {
    let file = std::fs::File::open(zip_path)?;
    let mut archive = zip::ZipArchive::new(file)?;
    
    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        if file.name().ends_with(".html") {
            let mut html_content = String::new();
            use std::io::Read;
            file.read_to_string(&mut html_content)?;
            
            let eq_regex = regex::Regex::new(r#"<img[^>]*class="[^"]*Math[^"]*"[^>]*title="([^"]*)"[^>]*>"#).unwrap();
            let preprocessed_html = eq_regex.replace_all(&html_content, |caps: &regex::Captures| {
                format!(" ${}$ ", caps.get(1).unwrap().as_str())
            }).to_string();

            return Ok(html2md::parse_html(&preprocessed_html));
        }
    }
    anyhow::bail!("❌ No HTML file found in ZIP archive")
}

/// Orchestrates the ingestion of image assets and social widgets.
fn ingest_image(number: &str, source: &str, config: &IngestConfig) -> Result<()> {
    eprintln!("🖼️  Ingesting image for episode {}...", number);
    
    // 1. Find the latest image
    let img_extensions = ["png", "jpg", "jpeg", "webp"];
    let mut all_images = Vec::new();
    
    for ext in img_extensions {
        let pattern = format!("{}/*.{}", source, ext);
        if let Ok(paths) = glob(&pattern) {
            for path in paths.filter_map(Result::ok) {
                all_images.push(path);
            }
        }
    }

    all_images.sort_by(|a, b| {
        let metadata_a = std::fs::metadata(a).unwrap();
        let metadata_b = std::fs::metadata(b).unwrap();
        metadata_b.modified().unwrap().cmp(&metadata_a.modified().unwrap())
    });

    let latest_img = all_images.first().context(format!("❌ No image files found in {}", source))?;
    let ext = latest_img.extension().unwrap().to_str().unwrap();
    eprintln!("📸 Found image: {:?}", latest_img.file_name().unwrap());

    // 2. Prepare destination
    let img_dir = "src/img";
    std::fs::create_dir_all(img_dir)?;
    let dest_path = format!("{}/{}.{}", img_dir, number, ext);
    
    // Move/Copy image
    std::fs::copy(latest_img, &dest_path)?;
    eprintln!("✅ Saved image to: {}", dest_path);

    // 3. Update the Markdown file
    let md_path = format!("src/{}.md", number);
    if std::path::Path::new(&md_path).exists() {
        let content = std::fs::read_to_string(&md_path)?;
        let mut lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
        
        let mut h1_idx = None;
        for (i, line) in lines.iter().enumerate() {
            if line.starts_with("# ") {
                h1_idx = Some(i);
                break;
            }
        }

        if let Some(idx) = h1_idx {
            let relative_img_path = format!("img/{}.{}", number, ext);
            let img_tag = format!("\n![Cover Image]({})\n", relative_img_path);
            
            let default_podcast_links = r#"
<center><a href="https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Spotify</a><a href="https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Apple Podcasts</a><a href="https://music.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe&si=o534zFZsc7p5XA9Q" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">YouTube Music</a><a href="https://www.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">YouTube</a><a href="https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">Fountain.fm</a></center>
"#;
            let podcast_links = config.podcast_html.as_deref().unwrap_or(default_podcast_links);

            let default_lightning_address = "shutosha@primal.net";
            let lightning_address = config.lightning_address.as_deref().unwrap_or(default_lightning_address);

            let wallet_widget = format!(r##"
<!-- WALLET_START -->
---

### Tips and Donations

If you enjoyed this deep dive, consider supporting the project with a tip in **Sats**. It's a simple, global way to support independent research.

<lightning-widget
  name="Thanks for supporting the publication"
  accent="#f9ce00"
  to="{}"
  image="https://nostrcheck.me/me/media/5af0794606a15b5641e25aa23d04af4cb0d7d5e68b11cacb47e56a4698fca8c4/49ff6d00cb5bc819cd19f77783d4815fbd46a5b99b6fbdead1eaecfab798187b.webp"
/>
<script src="https://embed.twentyuno.net/js/app.js"></script>

To send Sats, you'll need a [lightning wallet](https://lightningaddress.com/). 

---
<!-- WALLET_END -->
"##, lightning_address);

            let mut content = std::fs::read_to_string(&md_path)?;
            
            // 3.1 Update Cover and Podcast Links
            let h1_regex = regex::Regex::new(r"(?m)^#\s.*$").unwrap();
            if let Some(m) = h1_regex.find(&content) {
                let end = m.end();
                // Clean existing cover/podcast
                let pod_marker = "Fountain.fm</a></center>";
                let mut search_area = &content[end..];
                if let Some(pod_end) = search_area.find(pod_marker) {
                    content.replace_range(end..end + pod_end + pod_marker.len(), "");
                }
                content.insert_str(end, &format!("\n{}\n{}", img_tag, podcast_links));
            }

            // 3.2 Update Wallet
            let w_start = "<!-- WALLET_START -->";
            let w_end = "<!-- WALLET_END -->";
            if let (Some(s), Some(e)) = (content.find(w_start), content.find(w_end)) {
                content.replace_range(s..e + w_end.len(), "");
            }

            let ref_regex = regex::Regex::new(r"(?i)#### \*\*Works cited\*\*|#### \*\*References\*\*|## Bibliography|## References or Bibliography").unwrap();
            if let Some(m) = ref_regex.find(&content) {
                content.insert_str(m.start(), &wallet_widget);
            } else {
                content.push_str(&wallet_widget);
            }
            
            std::fs::write(&md_path, content)?;
            eprintln!("✅ Updated Markdown with cover and snippets.");
            
            update_summary(number, &md_path)?;
        }
    } else {
        eprintln!("⚠️  Markdown file {} not found. Snippets not injected.", md_path);
    }

    Ok(())
}

/// Updates the `SUMMARY.md` file to include the newly ingested episode.
fn update_summary(number: &str, file_path: &str) -> Result<()> {
    let summary_path = "src/SUMMARY.md";
    if !std::path::Path::new(summary_path).exists() { return Ok(()); }

    let mut summary_content = std::fs::read_to_string(summary_path)?;
    let content = std::fs::read_to_string(file_path)?;
    let title_line = content.lines()
        .find(|line| line.starts_with("# "))
        .map(|line| line.trim_start_matches("# ").trim())
        .unwrap_or("Untitled");

    let mut title = title_line.replace("**", "").trim().to_string();
    if let Some(pos) = title.find(':') {
        title = title[pos + 1..].trim().to_string();
    }

    let new_entry = format!("- [{} : {}]({}.md)", number, title, number);
    let start_marker = "<!-- RECENT_START -->";
    let end_marker = "<!-- RECENT_END -->";

    if let (Some(start_idx), Some(end_idx)) = (summary_content.find(start_marker), summary_content.find(end_marker)) {
        let insert_pos = start_idx + start_marker.len();
        let recent_section = &summary_content[insert_pos..end_idx];
        let mut entries: Vec<String> = recent_section.trim().lines().map(|l| l.to_string()).filter(|l| !l.is_empty()).collect();
        entries.retain(|l| !l.contains(&format!("({}.md)", number)));
        entries.insert(0, new_entry);
        let new_recent_content = format!("\n{}\n", entries.join("\n"));
        summary_content.replace_range(insert_pos..end_idx, &new_recent_content);
        std::fs::write(summary_path, summary_content)?;
        eprintln!("📑 Updated SUMMARY.md");
    }

    Ok(())
}
