//! # md-publish (The Ingestion Layer)
//!
//! A professional, modular asset ingestion bridge for `mdbook`. This crate serves 
//! as the **Ingestion Layer** within an autonomous **Research-to-Publish Workflow**.

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

#[derive(Deserialize, Default, Clone)]
pub struct IngestConfig {
    pub downloads_path: Option<String>,
    pub lightning_address: Option<String>,
    pub podcast_html: Option<String>,
    pub visual_html: Option<String>,
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

#[derive(Parser)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
    #[arg(long)]
    text: bool,
    #[arg(long)]
    image: bool,
    #[arg(long)]
    video: bool,
    number: Option<String>,
    #[arg(short, long, default_value = "/mnt/c/Users/ashut/Downloads")]
    source: String,
    #[arg(short, long)]
    title: Option<String>,
}

#[derive(Subcommand)]
enum Commands {
    Supports { renderer: String },
    Doctor,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let config = IngestConfig::load();
    let source = cli.source.clone();

    if let Some(command) = cli.command {
        match command {
            Commands::Supports { renderer } => {
                if renderer != "not-supported" { std::process::exit(0); } else { std::process::exit(1); }
            }
            Commands::Doctor => { run_doctor()?; }
        }
    } else if cli.text {
        if let Some(number) = cli.number { ingest_text(&number, &source, cli.title.as_deref(), &config)?; }
        else { anyhow::bail!("Episode number required"); }
    } else if cli.image {
        if let Some(number) = cli.number { ingest_image(&number, &source)?; }
        else { anyhow::bail!("Episode number required"); }
    } else if cli.video {
        if let Some(number) = cli.number { ingest_video(&number, &source, &config)?; }
        else { anyhow::bail!("Episode number required"); }
    } else {
        let (_ctx, book) = mdbook::preprocess::CmdPreprocessor::parse_input(std::io::stdin())?;
        print!("{}", serde_json::to_string(&book)?);
    }
    Ok(())
}

fn ingest_video(number: &str, source: &str, config: &IngestConfig) -> Result<()> {
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
    local_vids.sort(); // Consistent order

    if local_vids.is_empty() {
        eprintln!("⚠️ No videos found for episode {}", number);
        return Ok(());
    }

    // 3. Generate HTML
    let default_visual_links = r#"
<center><a href="https://www.tiktok.com/@shutoshabot" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">TikTok</a><a href="https://www.instagram.com/shutoshabot/" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Instagram</a><a href="https://www.youtube.com/playlist?list=PLIX4sFsmu37q8rU8HKTLhdLPZQadcvx-K" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">YouTube</a><a href="https://open.spotify.com/show/07r9EZMLpFC7qwZwxsJ5P9" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">Spotify</a></center>
"#;
    let visual_links = config.visual_html.as_deref().unwrap_or(default_visual_links);

    let mut html = String::new();
    html.push_str("\n<!-- VIDEO_STRIP_START -->\n");
    html.push_str(&format!("\n<center><h3>Info Graphics feed from <a href=\"https://mosaic.so\" target=\"_blank\" style=\"text-decoration: none; color: inherit; border-bottom: 1px solid #555;\">Mosaic.SO</a></h3></center>\n{}\n", visual_links));
    
    html.push_str("<div class=\"video-carousel-container\" style=\"display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 15px; padding: 20px 0; scroll-behavior: smooth;\">\n");

    for (i, path) in local_vids.iter().enumerate() {
        let filename = path.file_name().unwrap().to_str().unwrap();
        html.push_str(&format!(
            r#"  <div style="flex: 0 0 60%; scroll-snap-align: center; position: relative; border-radius: 12px; overflow: hidden; background: #000; aspect-ratio: 1/1; display: flex; flex-direction: column;">
    <video src="vid/{}" style="width: 100%; height: 85%; object-fit: contain;" playsinline loop preload="auto" muted autoplay></video>
    <div style="height: 15%; background: #1a1a1a; color: #ccc; display: flex; align-items: center; justify-content: center; font-family: monospace; font-size: 12px; border-top: 1px solid #333;">{}</div>
    <button class="vid-toggle" onclick="window.oph_play_toggle(this)" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; border: 2px solid white; border-radius: 50%; width: 45px; height: 45px; cursor: pointer; font-size: 22px; z-index: 100;">🔇</button>
  </div>
"#, filename, filename.trim_end_matches(".mp4")));
    }
    html.push_str("</div>\n");

    html.push_str(r#"<script>
  window.oph_play_toggle = window.oph_play_toggle || function(btn) {
    const parent = btn.parentElement;
    const vid = parent.querySelector('video');
    const container = btn.closest('.video-carousel-container');
    if (vid.paused || vid.muted) {
      container.querySelectorAll('video').forEach(v => { v.pause(); v.muted = true; v.parentElement.querySelector('.vid-toggle').innerText = '🔇'; });
      vid.muted = false; vid.volume = 1.0;
      vid.play().then(() => { btn.innerText = '🔊'; }).catch(e => console.error(e));
    } else {
      vid.pause(); vid.muted = true; btn.innerText = '🔇';
    }
  };
  (function() {
    const init = () => {
      const vids = document.querySelectorAll('.video-carousel-container video');
      vids.forEach(v => { 
        v.muted = true; 
        v.play().catch(() => {}); 
      });
    };
    setTimeout(init, 500);
  })();
</script>
"#);
    html.push_str("<!-- VIDEO_STRIP_END -->\n\n");

    // 4. Inject into THIS file only
    let path = format!("src/{}.md", number);
    let content = std::fs::read_to_string(&path)?;
    if let (Some(s), Some(e)) = (content.find("<!-- VIDEO_STRIP_START -->"), content.find("<!-- VIDEO_STRIP_END -->")) {
        let mut new_content = String::new();
        new_content.push_str(&content[..s]);
        new_content.push_str(&html);
        new_content.push_str(&content[e + "<!-- VIDEO_STRIP_END -->".len()..]);
        std::fs::write(&path, new_content)?;
        eprintln!("✅ Updated infographic scroll in {}", path);
    } else {
        eprintln!("⚠️ No strip markers found in {}", path);
    }

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

fn ingest_text(number: &str, source: &str, title: Option<&str>, config: &IngestConfig) -> Result<()> {
    eprintln!("📖 Ingesting text for episode {}...", number);
    let mut files: Vec<PathBuf> = glob(&format!("{}/*.md", source))?.filter_map(Result::ok)
        .filter(|p| !["SUMMARY.md", "cover.md"].contains(&p.file_name().unwrap().to_str().unwrap())).collect();
    files.sort_by(|a, b| std::fs::metadata(b).unwrap().modified().unwrap().cmp(&std::fs::metadata(a).unwrap().modified().unwrap()));

    if let Some(path) = files.first() {
        let content = std::fs::read_to_string(path)?;
        let hardened = sanitizer::process_content(content, number, title, config.title_word_limit.unwrap_or(5));
        std::fs::write(format!("src/{}.md", number), hardened)?;
        eprintln!("✅ Ingested text to src/{}.md", number);
    }
    Ok(())
}

fn ingest_image(number: &str, source: &str) -> Result<()> {
    eprintln!("🎨 Ingesting image for episode {}...", number);
    let img_dir = "src/img";
    std::fs::create_dir_all(img_dir)?;
    let mut images: Vec<PathBuf> = glob(&format!("{}/*{}*.png", source, number))?.filter_map(Result::ok).collect();
    images.sort_by(|a, b| std::fs::metadata(b).unwrap().modified().unwrap().cmp(&std::fs::metadata(a).unwrap().modified().unwrap()));

    if let Some(path) = images.first() {
        let dest = format!("{}/{}.png", img_dir, number);
        std::fs::copy(path, &dest)?;
        eprintln!("✅ Ingested cover art to {}", dest);
    }
    Ok(())
}
