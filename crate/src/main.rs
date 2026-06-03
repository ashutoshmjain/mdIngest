//! # md-publish (The Ingestion Layer)
//!
//! A professional, modular asset ingestion bridge for `mdbook`. This crate serves 
//! as the **Ingestion Layer** within an autonomous **Research-to-Publish Workflow**.

mod sanitizer;

use anyhow::{Result};
use glob::glob;
use std::path::PathBuf;
use std::process::Command;
use serde::{Deserialize, Serialize};

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

fn ingest_image(number: &str, source: &str, config: &IngestConfig) -> Result<()> {
    eprintln!("🎨 Ingesting image for episode {}...", number);
    let img_dir = "src/img";
    std::fs::create_dir_all(img_dir)?;
    let mut images: Vec<PathBuf> = glob(&format!("{}/*{}*.png", source, number))?.filter_map(Result::ok).collect();
    images.sort_by(|a, b| std::fs::metadata(b).unwrap().modified().unwrap().cmp(&std::fs::metadata(a).unwrap().modified().unwrap()));

    if let Some(path) = images.first() {
        let dest = format!("{}/{}.png", img_dir, number);
        std::fs::copy(path, &dest)?;
        eprintln!("✅ Ingested cover art to {}", dest);

        // Hybrid Layout Injection
        let md_path = format!("src/{}.md", number);
        if let Ok(content) = std::fs::read_to_string(&md_path) {
            let podcast_html = config.podcast_html.as_deref().unwrap_or("");
            let mut audio_feed = String::new();
            audio_feed.push_str("\n<!-- AUDIO_FEED_START -->\n");
            audio_feed.push_str(&format!("![Cover Image](img/{}.png)\n\n<center><h3>Audio Feed from <a href=\"https://notebooklm.google.com/\" target=\"_blank\" style=\"text-decoration: none; color: inherit; border-bottom: 1px solid #555;\">notebookLM</a></h3></center>\n\n{}\n", number, podcast_html));
            audio_feed.push_str("<!-- AUDIO_FEED_END -->\n");

            // Always strip existing block to ensure clean re-placement
            let mut clean_content = if let (Some(s), Some(e)) = (content.find("<!-- AUDIO_FEED_START -->"), content.find("<!-- AUDIO_FEED_END -->")) {
                let mut c = String::new();
                c.push_str(&content[..s]);
                c.push_str(&content[e + "<!-- AUDIO_FEED_END -->".len()..]);
                c
            } else {
                content.clone()
            };

            // Re-calculate anchor point and insert
            let final_content = if let Some(pos) = sanitizer::find_first_substantial_paragraph(&clean_content) {
                let mut nc = String::new();
                nc.push_str(&clean_content[..pos]);
                nc.push_str(&audio_feed);
                nc.push_str(&clean_content[pos..]);
                nc
            } else {
                // Fallback to top (below H1)
                let mut nc = String::new();
                if let Some(h1_end) = clean_content.find('\n').map(|i| i + 1) {
                    nc.push_str(&clean_content[..h1_end]);
                    nc.push_str(&audio_feed);
                    nc.push_str(&clean_content[h1_end..]);
                } else {
                    nc.push_str(&audio_feed);
                    nc.push_str(&clean_content);
                }
                nc
            };
            
            std::fs::write(&md_path, final_content)?;
            eprintln!("✅ Injected audio feed into {}", md_path);
        }
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
<center><a href="https://www.tiktok.com/@shutoshabot" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">TikTok</a><a href="https://www.instagram.com/shutoshabot/" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Instagram</a><a href="https://www.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">YouTube</a><a href="https://open.spotify.com/show/07r9EZMLpFC7qwZwxsJ5P9" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">Spotify</a></center>
"#;
    let visual_links = config.visual_html.as_deref().unwrap_or(default_visual_links);

    let mut html = String::new();
    html.push_str("\n<!-- VIDEO_STRIP_START -->\n");
    html.push_str(&format!("\n<center><h3>Info Graphics feed from <a href=\"https://mosaic.so\" target=\"_blank\" style=\"text-decoration: none; color: inherit; border-bottom: 1px solid #555;\">Mosaic.SO</a></h3></center>\n{}\n", visual_links));
    
    html.push_str("<div class=\"video-carousel-container\" style=\"display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 15px; padding: 20px 0; scroll-behavior: smooth;\">\n");

    for path in local_vids.iter() {
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
