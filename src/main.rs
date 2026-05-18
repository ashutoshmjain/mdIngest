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
            ingest_text(&number, &cli.source)?;
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

fn ingest_text(number: &str, source: &str) -> Result<()> {
    println!("Ingesting text for episode {}...", number);
    
    let pattern = format!("{}/*.md", source);
    let mut files: Vec<PathBuf> = glob(&pattern)?
        .filter_map(Result::ok)
        .filter(|p| {
            let filename = p.file_name().unwrap().to_str().unwrap();
            !["SUMMARY.md", "cover.md", "README.md"].contains(&filename)
        })
        .collect();

    files.sort_by(|a, b| {
        let metadata_a = std::fs::metadata(a).unwrap();
        let metadata_b = std::fs::metadata(b).unwrap();
        metadata_b.modified().unwrap().cmp(&metadata_a.modified().unwrap())
    });

    let latest_file = files.first().context(format!("No .md files found in {}", source))?;
    println!("Found export: {:?}", latest_file);

    let content = std::fs::read_to_string(latest_file)?;
    let processed = sanitizer::process_content(content, number);

    let dest_path = format!("src/{}.md", number);
    std::fs::write(&dest_path, processed)?;
    println!("Saved: {}", dest_path);

    update_summary(number, &dest_path)?;
    
    Ok(())
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
