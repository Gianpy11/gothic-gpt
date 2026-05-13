"""
Gutenberg Corpus Preprocessor

This script reads a directory of raw text files downloaded from Project Gutenberg,
removes boilerplate (header, transcriber notes, licenses), normalizes punctuations and
concatenates the cleaned text into a single corpus.txt file.
"""

"""
The text is mostly ASCII, but we read and write using UTF-8 as a precaution
to safely handle any special characters. Aiming for an ASCII-like subset
helps keep the model's vocabulary small, readable and efficient.
"""

from pathlib import Path
import re

# Gutenberg project file delimiters
START_MARKER = "*** START OF THE PROJECT GUTENBERG"
END_MARKER = "*** END OF THE PROJECT GUTENBERG"
SEPARATOR = "\n\n\n\n"

# Editorial brackets to strip: anything in [...] that starts with a known prefix
EDITORIAL_BRACKET_PATTERN = re.compile(
    r"\[\s*(Transcriber'?s? Note|Footnote|Illustration|Note|Picture|Editor'?s? Note)[^\]]*\]",
    flags=re.IGNORECASE | re.DOTALL,
)

# Transcriber notes in prose form (no brackets), terminated by blank line
TRANSCRIBER_PROSE_PATTERN = re.compile(
    r"\n[ \t]*Transcriber'?s?[ \t]+[Nn]ote[s]?[^\n]*\n.*?(?=\n[ \t]*\n)",
    flags=re.DOTALL,
)

def clean_text(raw_text: str, title: str) -> str | None:
    start_idx = raw_text.find(START_MARKER)

    if (start_idx == -1):
        print(f"Error: string {START_MARKER} isn't present in {title}")
        return None
    
    end_idx = raw_text.find(END_MARKER)

    if (end_idx == -1):
        print(f"Error: string {END_MARKER} isn't present in {title}")
        return None
    
    content_start = raw_text.find('\n', start_idx) +1
    content_end = end_idx

    cleaned = raw_text[content_start:content_end]
    return cleaned


def normalize(text: str) -> str:
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2014": "--", "\u2013": "-",
        "\u2026": "...",
        "\xa0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def strip_editorial_brackets(text: str) -> str:
    """Remove editorial annotations (brackets and prose-form transcriber notes)."""
    text = EDITORIAL_BRACKET_PATTERN.sub("", text)
    text = TRANSCRIBER_PROSE_PATTERN.sub("", text)
    return text

def strip_front_matter(text: str) -> str:
    """There is no interest to front matter (title pages, copyright). Finding the first 
    line that looks like real prose: long enough and containing lowercase letters."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if len(line) >= 60 and any(c.islower() for c in line):
            return "\n".join(lines[i:])
    # fallback: if we never found a "prose" line, return everything
    return text

def main():
    base_dir = Path(__file__).resolve().parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"### Preprocessing {len(list(raw_dir.glob('*.txt')))} files ###\n")

    for file_path in sorted(raw_dir.glob("*.txt")):
        raw = file_path.read_text(encoding="utf-8")
        cleaned = clean_text(raw, file_path.name)

        if cleaned is None:
            print(f"  [skip] {file_path.name}")
            continue

        cleaned = strip_editorial_brackets(cleaned)
        cleaned = strip_front_matter(cleaned)
        normalized = normalize(cleaned).strip()
        output_path = processed_dir / file_path.name
        output_path.write_text(normalized, encoding="utf-8")
        print(f"  [ok]   {file_path.name}  ({len(normalized):>8} chars)")

    # Concatenate all processed files into corpus.txt
    print("\nBuilding corpus.txt...")
    corpus_parts = []
    for file_path in sorted(processed_dir.glob("*.txt")):
        if file_path.name == "corpus.txt":
            continue   # don't include the corpus in itself!
        corpus_parts.append(file_path.read_text(encoding="utf-8"))

    corpus = SEPARATOR.join(corpus_parts)
    corpus_path = processed_dir / "corpus.txt"
    corpus_path.write_text(corpus, encoding="utf-8")

    total_chars = len(corpus)
    print(f"\n--- Done. Corpus: {total_chars:,} characters in {len(corpus_parts)} files ---")


if __name__ == "__main__":
    main()