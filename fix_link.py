with open("crate/src/main.rs", "r") as f:
    content = f.read()

content = content.replace(
    "- [None at this moment. Join us on GitHub!](https://github.com/ashutoshmjain/deepDive)",
    "- [None at this moment. Join us on GitHub!](github.md)"
)

with open("crate/src/main.rs", "w") as f:
    f.write(content)
