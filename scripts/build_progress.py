from pathlib import Path
import re

ROOTS = ["Livros", "Index"]
README = Path("README.md")

START = "<!-- START_PROGRESS -->"
END = "<!-- END_PROGRESS -->"


# ---------- Helpers ----------
IGNORE_EXTENSIONS = {
    ".png",".jpg",".jpeg",".webp",".gif",".pdf",".zip",".rar"
}


def is_translation_file(path: Path):
    if path.is_dir():
        return False

    # ignore hidden files
    if path.name.startswith("."):
        return False

    ext = path.suffix.lower()

    # ignore binaries
    if ext in IGNORE_EXTENSIONS:
        return False

    # allow md OR extensionless files
    return True

def progress_bar(percent, size=40):
    filled = int(size * percent / 100)
    return "█" * filled + "░" * (size - filled)


def translated(file: Path):
    try:
        return file.read_text(encoding="utf-8").strip() != ""
    except:
        return False


def scan_folder(folder: Path):
    files = [f for f in folder.rglob("*") if is_translation_file(f)]
    done = [f for f in files if translated(f)]
    return done, files

def natural_key(text):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', str(text))
    ]

# ---------- Build report ----------

lines = []
untranslated_files = []

global_done = 0
global_total = 0

# GLOBAL PROGRESS
for root in ROOTS:
    done, files = scan_folder(Path(root))
    global_done += len(done)
    global_total += len(files)

overall_percent = (global_done/global_total*100) if global_total else 0

lines.append(f"**Overall: {global_done}/{global_total} — {overall_percent:.1f}%**")
lines.append(progress_bar(overall_percent))
lines.append("\n---\n")


# ---------- LIVROS ----------
livros = Path("Livros")
lines.append("## 📚 Livros\n")

for book in sorted([p for p in livros.iterdir() if p.is_dir()] , key=lambda x: natural_key(x.name)):

    done, files = scan_folder(book)
    percent = (len(done)/len(files)*100) if files else 0

    lines.append(f"### {book.name} — {percent:.0f}%")
    lines.append(progress_bar(percent, 30))

    # chapters
    for chapter in sorted([c for c in book.iterdir() if c.is_dir()] , key=lambda x: natural_key(x.name)):
        c_done, c_files = scan_folder(chapter)
        if not c_files:
            continue

        c_percent = (len(c_done)/len(c_files)*100)

        lines.append(f"- **{chapter.name}** — {c_percent:.0f}%")

        for f in c_files:
            if not translated(f):
                untranslated_files.append(f)

    lines.append("")


# ---------- INDEX ----------
index = Path("Index")
lines.append("\n## 🗂 Index\n")

for cat in sorted([p for p in index.iterdir() if p.is_dir()] , key=lambda x: natural_key(x.name)):
    done, files = scan_folder(cat)
    percent = (len(done)/len(files)*100) if files else 0
    lines.append(f"- **{cat.name}** — {percent:.0f}%")

    for f in files:
        if not translated(f):
            untranslated_files.append(f)


# ---------- UNTRANSLATED ----------
lines.append("\n---\n")
lines.append("## ❌ Untranslated files\n")

for f in sorted(untranslated_files):
    lines.append("- "+str(f).replace("\\", "/"))


progress_block = "\n".join(lines)


# ---------- Inject into README ----------

content = README.read_text(encoding="utf-8")
before = content.split(START)[0]
after = content.split(END)[1]

new_content = before + START + "\n" + progress_block + "\n" + END + after
README.write_text(new_content, encoding="utf-8")

print("README dashboard updated")