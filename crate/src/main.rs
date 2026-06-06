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
        podcast_html: None,
        visual_html: None,
    });

    let mut number = None;
    let mut do_text = false;
    let mut do_image = false;
    let mut do_video = false;
    let mut title_override = None;
    let mut source = ingest_config.downloads_path.clone().unwrap_or_else(|| "/mnt/c/Users/ashut/Downloads".to_string());

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--text" => do_text = true,
            "--image" => do_image = true,
            "--video" => do_video = true,
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
        if args.len() > 1 && !args[1].starts_with('-') {
            // Support positional number
        } else {
            // Standard preprocessor mode
            let (_ctx, book) = mdbook::preprocess::CmdPreprocessor::parse_input(std::io::stdin())?;
            print!("{}", serde_json::to_string(&book)?);
        }
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
        if let Err(e) = update_summary(number) {
            eprintln!("⚠️ Failed to update SUMMARY.md: {}", e);
        } else {
            eprintln!("✅ Synchronized SUMMARY.md");
        }
    }
    Ok(())
}

fn update_summary(number: &str) -> Result<()> {
    let summary_path = "src/SUMMARY.md";
    let content = std::fs::read_to_string(summary_path)?;
    let md_path = format!("src/{}.md", number);
    
    // Extract title from the newly created markdown file
    let md_content = std::fs::read_to_string(&md_path)?;
    let h1_regex = regex::Regex::new(r"(?m)^#\s+\d+\s*:\s*(.*)$").unwrap();
    let title = if let Some(caps) = h1_regex.captures(&md_content) {
        caps.get(1).unwrap().as_str().trim()
    } else {
        "Untitled"
    };

    let new_entry = format!("- [{} : {}]({}.md)", number, title, number);
    
    // Check if already in SUMMARY.md
    if content.contains(&format!("({}.md)", number)) {
        return Ok(());
    }

    // Insert after <!-- RECENT_START -->
    let mut lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    if let Some(pos) = lines.iter().position(|l| l.contains("<!-- RECENT_START -->")) {
        lines.insert(pos + 1, new_entry);
        std::fs::write(summary_path, lines.join("\n"))?;
    }

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
    local_vids.sort(); // Consistent order

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
