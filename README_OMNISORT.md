# Titus OmniSort Pro — 2-in-1 Folder & File Intelligent Sorter

Titus OmniSort Pro is a 2-in-1 desktop file and folder organization studio built with Python and PyQt6. It merges the capabilities of **[File Juggler](https://www.filejuggler.com/features/)**, **[Sortio](https://www.getsortio.com/#features)**, and **[Abelssoft File Organizer](https://www.abelssoft.de/en/windows/helpers/abelssoft-file-organizer)** into a single unified application.

---

## 🌟 The 2-in-1 Dual Paradigm

### 1. Mode 1: Batch Folder Auto-Cleaner & Organizer *(Sortio + File Juggler)*
- **Drag & Drop Folder Intake**: Drag any messy folder (like `Downloads`, `Desktop`, or messy work directories) directly into the app.
- **Instant Folder Audit**: Visual breakdown of total file count, total size, and category distribution chips.
- **Smart 1-Click Presets**:
  - 🌟 **By Category**: Documents, Images, Audio, Video, Archives, Code, Spreadsheets, Presentations, Executables, Fonts.
  - 🏷️ **By Extension**: Groups by `.pdf`, `.docx`, `.xlsx`, `.jpg`, `.png`, etc.
  - 📅 **By Date**: Subfolders by `Year/Month` (e.g. `2026/11-November`), `Year` only (`2026`), or `Exact Date` (`2026-11-01`).
  - 📏 **By File Size**: `Tiny (<100KB)`, `Small (100KB-1MB)`, `Medium (1MB-50MB)`, `Large (50MB-500MB)`, `Huge (>500MB)`.
  - 🔤 **Alphabetical Buckets**: `A - E`, `F - J`, `K - O`, `P - T`, `U - Z`, and `0-9 & Symbols`.
  - ⚡ **Rule Engine Pipeline**: Route files through custom multi-condition automation rules.
- **Destination Control**: Organize in-place (creating organized subfolders inside the source folder) OR into a separate target directory.
- **Dry-Run Simulation Table**: View a proposed before/after table showing exact target paths, sizes, and actions before touching a single file on disk.

### 2. Mode 2: Instant Drag-and-Drop Drop Zones Hub *(Abelssoft File Organizer)*
- **Interactive Drop Buckets**: A grid of visual tiles where you can drag and drop loose files or folders from Windows Explorer to sort them directly into target folders:
  - 📄 **Documents & PDFs** (`~/Documents`)
  - 🖼️ **Photos & Images** (`~/Pictures`)
  - 🧾 **Receipts & Invoices** (`~/Documents/Receipts`)
  - 🎵 **Music & Audio** (`~/Music`)
  - 🎬 **Videos & Clips** (`~/Videos`)
  - 📦 **Archives & Zips** (`~/Downloads/Archives`)
  - 💻 **Code & Dev Projects** (`~/Documents/Projects`)
  - ⚙️ **Installers & Setups** (`~/Downloads/Installers`)
- **Add Custom Drop Zones**: Create new custom tiles targeting any folder with custom icons, colors, and live sort counters.
- **📌 Floating Mini-Target (Always on Top)**: Dockable, semi-transparent desktop mini-widget that stays on top of your browser or email client. Drag files right onto it while browsing to sort them instantly.

---

## ⚡ Additional Core Capabilities

### 3. File Juggler Advanced Rule Engine & Deep Inspection
- **Deep File Inspection**:
  - **PDF Text Reader** (*PyMuPDF*): Reads text inside PDFs to identify invoices, receipts, dates, or keywords.
  - **Word Docx Reader** (*python-docx*): Reads paragraphs and tables.
  - **Plain Text / Code**: Reads keywords or regex inside `.txt`, `.csv`, `.md`, `.py`, `.log`, `.json`.
  - **Image EXIF Metadata** (*Pillow*): Camera model, date taken, and image dimensions.
- **Rule Builder**:
  - Combine conditions with `AND` / `OR` logic.
  - Match by file name, extension, category, size brackets, age in days, content, or EXIF camera.
  - Dynamic template variables in destination paths: `{year}`, `{month}`, `{date}`, `{category}`, `{ext}`, `{name}`.
  - Test rule interactively against any file.

### 4. Background Real-Time Folder Watcher *(File Juggler)*
- Monitors designated directories (e.g. `Downloads` or `Desktop`).
- **Download Settling Wait Time**: Automatically waits until downloads finish (debouncing partial `.crdownload` / `.tmp` files) before applying rules.
- Live auto-sort activity log.

### 5. Duplicate Cleaner *(Sortio)*
- **3-Tier High Performance Scanner**:
  - Size pre-filtering (skips unique files instantly).
  - 8KB quick hash.
  - Full SHA-256 validation.
- Grouped duplicate clusters with file paths, sizes, and timestamps.
- 1-Click Selection: "Keep Oldest (Select Newer)" or "Keep Newest (Select Older)".
- Safe Recycle to Windows Recycle Bin.

### 6. Transaction History & 1-Click Rollback / Undo *(Sortio)*
- Full persistent history of every sort operation.
- **1-Click Rollback**: Moves files back to their exact original paths and removes empty subfolders created during the sort.

---

## 🧭 MenuBar, ToolBar & Navigation Shortcuts

### MenuBar Hierarchy
- **File**: Open Folder (`Ctrl+O`), Set Destination (`Ctrl+D`), Open Downloads / Desktop, Reveal in Explorer (`Ctrl+E`), Exit (`Ctrl+Q`).
- **Actions**: Simulate Preview (`F5`), Run Organization (`Ctrl+Enter`), Select All (`Ctrl+A`), Deselect All (`Ctrl+Shift+A`), 1-Click Rollback (`Ctrl+Z`), Duplicate Scanner (`Ctrl+Shift+D`).
- **Rules**: New Rule (`Ctrl+N`), Test Rule on Sample (`Ctrl+T`), Reset to Defaults.
- **Watcher**: Start Watcher (`F9`), Stop Watcher (`F10`), Add Watch Folder, Clear Activity Log.
- **View**: Direct mode navigation (`Ctrl+1` through `Ctrl+6`), Toggle Floating Mini-Target (`F8`).
- **Help**: Quick Start Guide (`F1`), About Titus OmniSort Pro.

### Quick-Access ToolBar
- 📁 **Open Folder**  •  🔍 **Preview**  •  🚀 **Run Sort**  •  ⏪ **Undo Last**  •  🎯 **Drop Zones**  •  🔎 **Duplicates**  •  ⚙️ **Rules**  •  📌 **Float Target**  •  📡 **Watcher**

### Rich StatusBar
- Dynamic operation feedback, loaded directory badge, real-time watcher state, and rollback availability counter.

---

## 🚀 How to Launch

Double-click `launch_sorter.bat` or run:
```bash
python run_sorter.py
```

