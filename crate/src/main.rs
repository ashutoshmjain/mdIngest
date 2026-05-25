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
            println!("📂 Using source from book.toml: {}", source);
        } else {
            println!("💡 Overriding book.toml source with CLI flag: {}", source);
        }
    } else if cli.source != "/mnt/c/Users/ashut/Downloads" {
        println!("📂 Using source from CLI flag: {}", source);
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
    } else if cli.number.is_some() {
        println!("ℹ️  Please specify asset type (e.g., --text or --image)");
    } else {
        let (_ctx, book) = mdbook::preprocess::CmdPreprocessor::parse_input(std::io::stdin())?;
        serde_json::to_writer(std::io::stdout(), &book)?;
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
    println!("🔍 Checking environment...");

    match Command::new("mdbook").arg("--version").output() {
        Ok(out) => println!("✅ mdbook: {}", String::from_utf8_lossy(&out.stdout).trim()),
        Err(_) => println!("❌ mdbook: Not found"),
    }

    match Command::new("mdbook-katex").arg("--version").output() {
        Ok(out) => println!("✅ mdbook-katex: {}", String::from_utf8_lossy(&out.stdout).trim()),
        Err(_) => println!("❌ mdbook-katex: Not found (Install with 'cargo install mdbook-katex')"),
    }

    if std::path::Path::new("book.toml").exists() {
        if let Ok(toml) = std::fs::read_to_string("book.toml") {
            if toml.contains("preprocessor.ingest") {
                println!("✅ book.toml: Ingestion configured");
            } else {
                println!("⚠️  book.toml: [preprocessor.ingest] section missing");
            }
        }
    }

    Ok(())
}

/// Orchestrates the ingestion of text-based research assets.
fn ingest_text(number: &str, source: &str, title: Option<&str>, config: &IngestConfig) -> Result<()> {
    println!("📖 Ingesting text for episode {}...", number);
    
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
    println!("📄 Found export: {:?}", latest_file.file_name().unwrap());

    let content = if latest_file.extension().unwrap() == "zip" {
        extract_html_from_zip(latest_file)?
    } else {
        std::fs::read_to_string(latest_file)?
    };

    let processed = sanitizer::process_content(content, number, title, config.title_word_limit.unwrap_or(5));

    let dest_path = format!("src/{}.md", number);
    std::fs::write(&dest_path, processed)?;
    println!("✅ Saved text to: {}", dest_path);

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
    println!("🖼️  Ingesting image for episode {}...", number);
    
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
    println!("📸 Found image: {:?}", latest_img.file_name().unwrap());

    // 2. Prepare destination
    let img_dir = "src/img";
    std::fs::create_dir_all(img_dir)?;
    let dest_path = format!("{}/{}.{}", img_dir, number, ext);
    
    // Move/Copy image
    std::fs::copy(latest_img, &dest_path)?;
    println!("✅ Saved image to: {}", dest_path);

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
"##, lightning_address);

            lines.insert(idx + 1, format!("{}\n{}", img_tag, podcast_links));
            
            let ref_regex = regex::Regex::new(r"(?i)#### \*\*Works cited\*\*|#### \*\*References\*\*|## Bibliography|## References or Bibliography").unwrap();
            let mut ref_idx = None;
            for (i, line) in lines.iter().enumerate() {
                if ref_regex.is_match(line) {
                    ref_idx = Some(i);
                    break;
                }
            }

            if let Some(r_idx) = ref_idx {
                lines.insert(r_idx, wallet_widget.to_string());
            } else {
                lines.push(wallet_widget.to_string());
            }
            
            std::fs::write(&md_path, lines.join("\n"))?;
            println!("✅ Updated Markdown with cover and snippets.");
            
            update_summary(number, &md_path)?;
        }
    } else {
        println!("⚠️  Markdown file {} not found. Snippets not injected.", md_path);
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
        println!("📑 Updated SUMMARY.md");
    }

    Ok(())
}
