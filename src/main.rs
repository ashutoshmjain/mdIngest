mod sanitizer;

use clap::{Parser, Subcommand};
use std::process::Command;
use anyhow::{Result, Context};
use glob::glob;
use std::path::PathBuf;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Ingest as text (Markdown)
    #[arg(long)]
    text: bool,

    /// Episode number (the Master Key)
    #[arg(short, long)]
    number: Option<String>,

    /// Source directory for exports
    #[arg(short, long, default_value = "/mnt/c/Users/ashut/Downloads")]
    source: String,

    /// Title override
    #[arg(short, long)]
    title: Option<String>,
}

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

    // 3. Handle Ingestion
    if cli.text {
        if let Some(number) = cli.number {
            ingest_text(&number, &cli.source, cli.title.as_deref())?;
        } else {
            anyhow::bail!("Error: Episode number (-n, --number) is required.");
        }
    } else if cli.number.is_some() {
        println!("Please specify asset type (e.g., --text)");
    } else {
        let (_ctx, book) = mdbook::preprocess::CmdPreprocessor::parse_input(std::io::stdin())?;
        serde_json::to_writer(std::io::stdout(), &book)?;
    }

    Ok(())
}

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

fn run_doctor() -> Result<()> {
    println!("Checking environment...");

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
            if toml.contains("preprocessor.katex") {
                println!("✅ book.toml: KaTeX configured");
            } else {
                println!("⚠️  book.toml: KaTeX preprocessor missing");
            }
        }
    }

    Ok(())
}

fn ingest_text(number: &str, source: &str, title: Option<&str>) -> Result<()> {
    println!("Ingesting text for episode {} from {}...", number, source);
    
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

    let latest_file = all_files.first().context(format!("No .md, .zip, or .rs files found in {}", source))?;
    println!("Found export: {:?}", latest_file);

    let content = if latest_file.extension().unwrap() == "zip" {
        extract_html_from_zip(latest_file)?
    } else {
        std::fs::read_to_string(latest_file)?
    };

    let processed = sanitizer::process_content(content, number, title);

    let dest_path = format!("src/{}.md", number);
    std::fs::write(&dest_path, processed)?;
    println!("Saved: {}", dest_path);

    update_summary(number, &dest_path)?;
    
    Ok(())
}

fn extract_html_from_zip(zip_path: &PathBuf) -> Result<String> {
    let file = std::fs::File::open(zip_path)?;
    let mut archive = zip::ZipArchive::new(file)?;
    
    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        if file.name().ends_with(".html") {
            let mut html_content = String::new();
            use std::io::Read;
            file.read_to_string(&mut html_content)?;
            
            // Google Docs HTML has equations in title attributes of images
            // We use scraper to extract these or just use a simple regex for now since we just need the text
            // html2md does a decent job, but we might lose equations if they are in titles.
            // Let's preprocess the HTML to pull title attributes out of equation images.
            let eq_regex = regex::Regex::new(r#"<img[^>]*class="[^"]*Math[^"]*"[^>]*title="([^"]*)"[^>]*>"#).unwrap();
            let preprocessed_html = eq_regex.replace_all(&html_content, |caps: &regex::Captures| {
                format!(" ${}$ ", caps.get(1).unwrap().as_str())
            }).to_string();

            return Ok(html2md::parse_html(&preprocessed_html));
        }
    }
    anyhow::bail!("No HTML file found in ZIP archive")
}

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
        println!("Updated SUMMARY.md");
    }

    Ok(())
}
