import re

with open("crate/src/main.rs", "r") as f:
    content = f.read()

# 1. Rename "The Tip of the Chain" to "Recent Blocks"
content = content.replace(
    'final_lines.push("\\n# The Tip of the Chain".to_string());',
    'final_lines.push("\\n# Recent Blocks".to_string());'
)

# 2. Remove "The Network" wrapper and un-indent Mempool and Archive items
old_network = """    final_lines.push("\\n# The Network\\n".to_string());
    final_lines.push("- [The Mempool (Unconfirmed)](mempool.md)".to_string());
    if wip_parked.is_empty() {
        final_lines.push("    - [None at this moment. Join us on GitHub!](github.md)".to_string());
    } else {
        for ep in wip_parked {
            let display_num = ep.filename.trim_start_matches('_');
            final_lines.push(format!("    - [{} : {}]({}.md)", display_num, ep.title, ep.filename));
        }
    }

    final_lines.push("\\n- [Deep Storage (The Ledger)](archive.md)".to_string());
    if !overflow_numbered.is_empty() {
        final_lines.push("  - [Verified Blocks (Older Episodes)]()".to_string());
        for ep in overflow_numbered {
            final_lines.push(format!("      - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }"""

new_network = """    final_lines.push("\\n# The Mempool (Unconfirmed)".to_string());
    final_lines.push("- [WIP / Call for Participation](mempool.md)".to_string());
    if wip_parked.is_empty() {
        final_lines.push("  - [None at this moment. Join us on GitHub!](github.md)".to_string());
    } else {
        for ep in wip_parked {
            let display_num = ep.filename.trim_start_matches('_');
            final_lines.push(format!("  - [{} : {}]({}.md)", display_num, ep.title, ep.filename));
        }
    }

    final_lines.push("\\n# Deep Storage (The Ledger)".to_string());
    final_lines.push("- [The Archive](archive.md)".to_string());
    if !overflow_numbered.is_empty() {
        final_lines.push("  - [Verified Blocks (Older Episodes)]()".to_string());
        for ep in overflow_numbered {
            final_lines.push(format!("      - [{} : {}]({}.md)", ep.number.unwrap(), ep.title, ep.filename));
        }
    }"""

content = content.replace(old_network, new_network)

# 3. Update the skip strings in the thematic parser to reflect the new structure
old_skips = 'let skip_strings = ["# WIP", "# Archive", "# Repository", "parked.md", "mempool.md", "Deep Storage", "The Network", "Verified Blocks", "Older Episodes", "github.md"];'
new_skips = 'let skip_strings = ["# WIP", "# Archive", "# Repository", "parked.md", "mempool.md", "Deep Storage", "The Network", "Verified Blocks", "Older Episodes", "github.md", "# Recent Blocks", "# The Mempool (Unconfirmed)"];'
content = content.replace(old_skips, new_skips)


with open("crate/src/main.rs", "w") as f:
    f.write(content)

