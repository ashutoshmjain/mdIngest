import re

with open('crate/src/main.rs', 'r') as f:
    content = f.read()

new_logic = """    let mut in_thematic_zone = false;
    let mut thematic_buffer = Vec::new();
    let num_regex = regex::Regex::new(r"\\d+\\.md").unwrap();
    for line in original_content.lines() {
        if line.contains("<!-- RECENT_END -->") {
            in_thematic_zone = true;
            continue;
        }
        if in_thematic_zone {
            if line.contains("# Recent") || line.contains("# WIP") || line.contains("# Archive") || line.contains("# Repository") {
                continue;
            }
            if num_regex.is_match(line) {
                continue;
            }
            if thematic_buffer.is_empty() && line.trim().is_empty() {
                continue;
            }
            thematic_buffer.push(line.to_string());
        }
    }"""

old_logic_pattern = re.compile(
    r"let mut in_thematic_zone = false;\s*"
    r"let mut thematic_buffer = Vec::new();\s*"
    r"for line in original_content\.lines\(\) \{\s*"
    r"if line\.contains\(\"<!-- RECENT_END -->\"\).*?thematic_buffer\.push\(line\.to_string\(\)\);\s*\}\s*\}", 
    re.DOTALL
)

# Use a function for repl to avoid escape issues in string substitution
def repl_func(match):
    return new_logic

updated_content = old_logic_pattern.sub(repl_func, content)

with open('crate/src/main.rs', 'w') as f:
    f.write(updated_content)

