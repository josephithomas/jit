# -*- coding: utf-8 -*-
"""
Titus II Teachers College - TSTC_Professional PDF Suite v5.0 (Adobe Acrobat Studio Edition)
Core Engines for:
1. PDF Spaces (Intelligent Workspaces & Universal Format Ingestion)
2. Advanced Acrobat AI Assistant (Multi-File Cross-Mining & Custom Personas)
3. Adobe Express Premium Studio (Creative Presentations, Infographics, Dossiers & Brand Kits)
4. Acrobat Pro Suite (Acrobat Sign, Version Control Diff, Legal Redaction & Admin Audit Trail)
Developed by Dr. Joseph I Thomas
"""

import os
import sys
import math
import re
import json
import time
import uuid
import hashlib
import difflib
import threading
import datetime
from typing import List, Dict, Any, Tuple, Optional, Set

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

# Optional / Standard Imports
try:
    import docx
except ImportError:
    docx = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import pptx
except ImportError:
    pptx = None

try:
    import requests
except ImportError:
    requests = None

try:
    import win32com.client
except ImportError:
    win32com = None


# ==============================================================================
# 1. UNIVERSAL FORMAT INGESTION & PDF SPACES ENGINE
# ==============================================================================
class PDFSpaceEngine:
    """Intelligent Workspace Hub & Universal Document Ingestion Engine."""

    @staticmethod
    def parse_universal_file(file_path: str) -> Dict[str, Any]:
        """Universal parser for PDF, Word, Excel, PowerPoint, Text, and Transcripts."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        file_size_kb = round(os.path.getsize(file_path) / 1024, 1)

        pages_data: List[Dict[str, Any]] = []
        full_text = ""

        # --- A. PDF Ingestion ---
        if ext == ".pdf":
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text("text").strip()
                p_text = text if text else "[Scanned/Image Page or Empty]"
                pages_data.append({
                    "page": i + 1,
                    "text": p_text,
                    "char_count": len(p_text)
                })
                full_text += p_text + "\n\n"
            doc.close()

        # --- B. Word Document Ingestion (.docx) ---
        elif ext in [".docx", ".doc"]:
            if docx is None:
                raise ImportError("python-docx is required to ingest Word documents.")
            doc_obj = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc_obj.paragraphs if p.text.strip()]
            for table in doc_obj.tables:
                for row in table.rows:
                    row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if row_cells:
                        paragraphs.append(" | ".join(row_cells))

            # Virtual pagination (~350 words per virtual page)
            current_page_text: List[str] = []
            current_word_count = 0
            page_num = 1

            for para in paragraphs:
                words = para.split()
                current_page_text.append(para)
                current_word_count += len(words)
                if current_word_count >= 350:
                    joined = "\n\n".join(current_page_text)
                    pages_data.append({"page": page_num, "text": joined, "char_count": len(joined)})
                    full_text += joined + "\n\n"
                    page_num += 1
                    current_page_text = []
                    current_word_count = 0

            if current_page_text or not pages_data:
                joined = "\n\n".join(current_page_text) if current_page_text else "[Empty Word Document]"
                pages_data.append({"page": page_num, "text": joined, "char_count": len(joined)})
                full_text += joined + "\n\n"

        # --- C. Excel Spreadsheets (.xlsx, .xls, .csv) ---
        elif ext in [".xlsx", ".xls", ".csv"]:
            if ext == ".csv":
                import csv
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                sheet_text = [f"=== CSV SPREADSHEET: {file_name} ==="]
                for r in rows[:200]:
                    sheet_text.append(" | ".join(r))
                joined = "\n".join(sheet_text)
                pages_data.append({"page": 1, "text": joined, "char_count": len(joined)})
                full_text += joined
            else:
                if openpyxl is None:
                    raise ImportError("openpyxl is required to ingest Excel spreadsheets.")
                wb = openpyxl.load_workbook(file_path, data_only=True)
                for s_idx, s_name in enumerate(wb.sheetnames):
                    sheet = wb[s_name]
                    lines = [f"=== SHEET: {s_name} ==="]
                    r_count = 0
                    for row in sheet.iter_rows(values_only=True):
                        if any(row):
                            row_vals = [str(c) if c is not None else "" for c in row]
                            lines.append(" | ".join(row_vals))
                            r_count += 1
                        if r_count >= 250:
                            lines.append(f"... [{sheet.max_row - 250} additional rows truncated for indexing] ...")
                            break
                    joined = "\n".join(lines) if lines else f"[Empty Sheet {s_name}]"
                    pages_data.append({"page": s_idx + 1, "text": joined, "char_count": len(joined)})
                    full_text += joined + "\n\n"

        # --- D. PowerPoint Decks (.pptx) ---
        elif ext in [".pptx", ".ppt"]:
            if pptx is not None:
                prs = pptx.Presentation(file_path)
                for s_idx, slide in enumerate(prs.slides):
                    slide_texts = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text:
                            slide_texts.append(shape.text.strip())
                    joined = f"=== SLIDE {s_idx+1} ===\n" + "\n".join(slide_texts) if slide_texts else f"=== SLIDE {s_idx+1} ===\n[Visual / Diagram Slide]"
                    pages_data.append({"page": s_idx + 1, "text": joined, "char_count": len(joined)})
                    full_text += joined + "\n\n"
            else:
                # Fallback: Plain text / XML extraction from PPTX zip structure
                import zipfile, xml.etree.ElementTree as ET
                try:
                    with zipfile.ZipFile(file_path, 'r') as z:
                        slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
                        slide_files.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
                        for s_idx, s_f in enumerate(slide_files):
                            xml_content = z.read(s_f)
                            tree = ET.fromstring(xml_content)
                            texts = [elem.text for elem in tree.iter() if elem.text and elem.text.strip()]
                            joined = f"=== SLIDE {s_idx+1} ===\n" + "\n".join(texts)
                            pages_data.append({"page": s_idx + 1, "text": joined, "char_count": len(joined)})
                            full_text += joined + "\n\n"
                except Exception:
                    pages_data.append({"page": 1, "text": f"[PowerPoint presentation: {file_name}]", "char_count": 50})

        # --- E. Plain Text, Markdown, RTF, JSON, Subtitles (.vtt, .srt, .txt, .md) ---
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
                    content = f.read()

            # For video transcripts (SRT / VTT), clean timecodes into readable dialogue
            if ext in [".srt", ".vtt"]:
                cleaned_lines = []
                for line in content.split("\n"):
                    l_s = line.strip()
                    if not l_s or l_s.isdigit() or "-->" in l_s or l_s.startswith("WEBVTT"):
                        continue
                    cleaned_lines.append(l_s)
                content = "\n".join(cleaned_lines)

            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            current_page_text = []
            current_word_count = 0
            page_num = 1

            for para in paragraphs:
                words = para.split()
                current_page_text.append(para)
                current_word_count += len(words)
                if current_word_count >= 350:
                    joined = "\n\n".join(current_page_text)
                    pages_data.append({"page": page_num, "text": joined, "char_count": len(joined)})
                    full_text += joined + "\n\n"
                    page_num += 1
                    current_page_text = []
                    current_word_count = 0

            if current_page_text or not pages_data:
                joined = "\n\n".join(current_page_text) if current_page_text else "[Empty File]"
                pages_data.append({"page": page_num, "text": joined, "char_count": len(joined)})
                full_text += joined + "\n\n"

        words_total = sum(len(p["text"].split()) for p in pages_data)

        return {
            "id": str(uuid.uuid4())[:8],
            "name": file_name,
            "path": os.path.abspath(file_path),
            "format": ext.upper().replace(".", "") if ext else "FILE",
            "size_kb": file_size_kb,
            "page_count": len(pages_data),
            "word_count": words_total,
            "pages": pages_data,
            "status": "Ready",
            "ingested_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
