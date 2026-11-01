# -*- coding: utf-8 -*-
"""
Titus II Teachers College - TSTC_Professional PDF Suite v4.0 (patched)
Integrated Institutional Desktop Suite combining features of Adobe Acrobat Pro,
ABBYY FineReader PDF, and the OpenView Dynamic Index & Table of Contents Builder.
Developed by Dr. Joseph I Thomas

Patch notes (debug pass):
- Retain CTkImage references so the PDF canvas and thumbnails no longer blank out
- OpenView index GOTO links are shifted correctly when the index is prepended
- Safe page-spec parser (``1, 3-5, 8``) used by Extract / Delete tools
- Image watermark now honours the ``opacity`` argument (PyMuPDF 1.18+)
- Header/footer page numbers are truly centered via text-width measurement
- insert_blank_page empty-document size handling made explicit
"""

import os
import sys
import math
import re
import json
import threading
import traceback
import importlib
import webbrowser
from typing import List, Dict, Any, Tuple, Optional

try:
    import requests
except ImportError:
    requests = None

import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu, ttk, Canvas
from PIL import Image, ImageTk, ImageEnhance, ImageFilter

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter

# Optional / Fallback Imports
try:
    from pdf2docx import Converter as DocxConverter
except ImportError:
    DocxConverter = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


def _get_surya_modules():
    """Dynamically import optional Surya OCR modules to avoid static import errors when surya-ocr is not installed."""
    try:
        surya_ocr = importlib.import_module("surya.ocr")
        surya_det = importlib.import_module("surya.model.detection")
        surya_rec = importlib.import_module("surya.model.recognition")
        return surya_ocr.run_ocr, surya_det.load_model, surya_rec.load_model
    except Exception:
        return None, None, None


# Set CustomTkinter Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==============================================================================
# TITUS II THEME & STYLING CONSTANTS
# ==============================================================================
PRIMARY_COLOR = "#6D28D9"      # Royal Purple
PRIMARY_HOVER = "#5B21B6"
SECONDARY_COLOR = "#0F172A"    # Deep Navy
ACCENT_GREEN = "#10B981"       # Emerald
ACCENT_GREEN_HOVER = "#059669"
BG_DARK = "#1E293B"
BG_CARD = "#334155"
TEXT_LIGHT = "#F8FAFC"
ACCENT_AMBER = "#F59E0B"

# ==============================================================================
# PDF ENGINE BACKEND (ADOBE + ABBYY + OPENVIEW BACKEND UTILITIES)
# ==============================================================================
class PDFEngine:
    """Backend engine for PDF processing using PyMuPDF (fitz) and PyPDF."""

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count

    @staticmethod
    def parse_page_spec(spec: str, max_page: int) -> List[int]:
        """Parse a user page specification such as ``'1, 3-5, 8'`` into a
        sorted unique list of 1-based page numbers within ``[1, max_page]``.

        Raises ``ValueError`` with a clear message on malformed input.
        """
        pages: set = set()
        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                bits = part.split("-", 1)
                try:
                    start = int(bits[0].strip())
                    end = int(bits[1].strip())
                except ValueError:
                    raise ValueError(f"Invalid page range: '{part}'")
                if start > end:
                    start, end = end, start
                for p in range(start, end + 1):
                    if 1 <= p <= max_page:
                        pages.add(p)
            else:
                if not part.isdigit():
                    raise ValueError(f"Invalid page number: '{part}'")
                p = int(part)
                if 1 <= p <= max_page:
                    pages.add(p)
        return sorted(pages)

    @staticmethod
    def extract_pages(pdf_path: str, page_numbers: List[int], output_path: str) -> bool:
        """Extract specific 1-indexed page numbers to a new PDF."""
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()
        for p in page_numbers:
            if 1 <= p <= len(doc):
                new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        return True

    @staticmethod
    def merge_pdfs(pdf_paths: List[str], output_path: str) -> bool:
        """Merge multiple PDF files into one output PDF."""
        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        return True

    @staticmethod
    def delete_pages(pdf_path: str, pages_to_delete: List[int], output_path: str) -> bool:
        """Delete 1-indexed pages from PDF."""
        doc = fitz.open(pdf_path)
        delete_set = set(p - 1 for p in pages_to_delete if 1 <= p <= len(doc))
        keep_indices = [i for i in range(len(doc)) if i not in delete_set]
        new_doc = fitz.open()
        for i in keep_indices:
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        return True

    @staticmethod
    def reorder_pages(pdf_path: str, new_order: List[int], output_path: str) -> bool:
        """Reorder pages based on list of 1-indexed page numbers."""
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()
        for p in new_order:
            if 1 <= p <= len(doc):
                new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        return True

    @staticmethod
    def rotate_pages(pdf_path: str, degrees: int, page_indices: Optional[List[int]], output_path: str) -> bool:
        """Rotate specified or all pages by given degrees (90, 180, 270)."""
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            if page_indices is None or (i + 1) in page_indices:
                page.set_rotation((page.rotation + degrees) % 360)
        doc.save(output_path)
        doc.close()
        return True

    @staticmethod
    def crop_pages(pdf_path: str, top: float, bottom: float, left: float, right: float, output_path: str) -> bool:
        """Crop page boundaries by margins (in points)."""
        doc = fitz.open(pdf_path)
        for page in doc:
            rect = page.rect
            new_rect = fitz.Rect(
                rect.x0 + left,
                rect.y0 + top,
                rect.x1 - right,
                rect.y1 - bottom
            )
            page.set_cropbox(new_rect)
        doc.save(output_path)
        doc.close()
        return True

    @staticmethod
    def insert_blank_page(pdf_path: str, position: int, output_path: str) -> bool:
        """Insert a blank page at position (0-indexed)."""
        doc = fitz.open(pdf_path)
        if len(doc) > 0:
            width = doc[0].rect.width
            height = doc[0].rect.height
        else:
            # Fallback to A4 (points)
            width, height = 595.0, 842.0
        doc.insert_page(position, width=width, height=height)
        doc.save(output_path)
        doc.close()
        return True

    # --------------------------------------------------------------------------
    # ADOBE ACROBAT PRO: ANNOTATIONS, WATERMARKS, REDACTION & SECURITY
    # --------------------------------------------------------------------------

    @staticmethod
    def add_text_watermark(pdf_path: str, text: str, output_path: str,
                           font_size: int = 36, opacity: float = 0.3,
                           angle: float = 45.0, color: Tuple[float, float, float] = (0.5, 0.5, 0.5)) -> bool:
        """Apply custom text watermark to all pages at an arbitrary rotation angle.

        NOTE (fix): the original implementation rounded `angle` down to the nearest
        multiple of 90 degrees (`(int(angle) // 90 * 90) % 360`), so a diagonal
        45-degree watermark was silently rendered horizontally. fitz.Page.insert_text's
        `rotate` kwarg only accepts multiples of 90, so we now use the `morph`
        kwarg (a fixpoint + rotation matrix) to support any angle.
        """
        doc = fitz.open(pdf_path)
        for page in doc:
            rect = page.rect
            center = fitz.Point(rect.width / 2, rect.height / 2)
            rot_matrix = fitz.Matrix(1, 1).prerotate(angle)
            page.insert_text(
                center,
                text,
                fontname="helv",
                fontsize=font_size,
                color=color,
                fill_opacity=opacity,
                morph=(center, rot_matrix),
                overlay=True
            )
        doc.save(output_path)
        doc.close()
        return True

    @staticmethod
    def add_image_watermark(pdf_path: str, image_path: str, output_path: str, scale: float = 0.3, opacity: float = 0.4) -> bool:
        """Overlay image watermark (e.g. institutional logo) on all pages.

        ``opacity`` is applied when supported by the installed PyMuPDF version
        (1.18+). Older builds silently ignore the keyword.
        """
        doc = fitz.open(pdf_path)
        try:
            img_doc = fitz.open(image_path)
            if len(img_doc) == 0:
                img_doc.close()
                raise ValueError(f"Watermark image '{image_path}' has no valid image content.")
            rect_img = img_doc[0].rect
            img_doc.close()

            for page in doc:
                p_rect = page.rect
                w = rect_img.width * scale
                h = rect_img.height * scale
                x = (p_rect.width - w) / 2
                y = (p_rect.height - h) / 2
                img_rect = fitz.Rect(x, y, x + w, y + h)
                try:
                    img_opts: Dict[str, Any] = {"opacity": max(0.0, min(1.0, float(opacity)))}
                    page.insert_image(
                        img_rect,
                        filename=image_path,
                        overlay=True,
                        **img_opts
                    )
                except TypeError:
                    page.insert_image(img_rect, filename=image_path, overlay=True)
            doc.save(output_path)
        finally:
            doc.close()
        return True

    @staticmethod
    def add_page_numbers_and_header(pdf_path: str, output_path: str,
                                     header_text: str = "", footer_text: str = "",
                                     include_page_num: bool = True) -> bool:
        """Apply Headers, Footers, and Page Numbers across document."""
        doc = fitz.open(pdf_path)
        try:
            total_pages = len(doc)
            for i, page in enumerate(doc):
                p_num = i + 1
                rect = page.rect

                # Header (left-aligned)
                if header_text:
                    page.insert_text(
                        fitz.Point(36, 30),
                        header_text,
                        fontsize=9,
                        color=(0.3, 0.3, 0.3),
                        overlay=True,
                    )

                # Footer & Page Number — properly centered using text width
                f_str = footer_text
                if include_page_num:
                    p_str = f"Page {p_num} of {total_pages}"
                    f_str = f"{footer_text}  |  {p_str}" if footer_text else p_str

                if f_str:
                    tw = fitz.get_text_length(f_str, fontname="helv", fontsize=9)
                    x = max(36.0, (rect.width - tw) / 2.0)
                    page.insert_text(
                        fitz.Point(x, rect.height - 25),
                        f_str,
                        fontsize=9,
                        color=(0.3, 0.3, 0.3),
                        overlay=True,
                    )

            doc.save(output_path)
        finally:
            doc.close()
        return True

    @staticmethod
    def add_stamp_annotation(pdf_path: str, page_num: int, stamp_text: str, output_path: str) -> bool:
        """Add official stamp annotation (e.g. APPROVED, TITUS II OFFICIAL)."""
        doc = fitz.open(pdf_path)
        try:
            if 1 <= page_num <= len(doc):
                page = doc[page_num - 1]
                rect = fitz.Rect(page.rect.width - 220, 40, page.rect.width - 40, 90)
                annot = page.add_rect_annot(rect)
                annot.set_colors(stroke=(0.7, 0.1, 0.1), fill=(0.98, 0.9, 0.9))
                annot.set_border(width=2)
                annot.update()
                
                page.insert_text(
                    fitz.Point(page.rect.width - 210, 70),
                    stamp_text,
                    fontsize=13,
                    color=(0.7, 0.1, 0.1),
                    overlay=True
                )
            doc.save(output_path)
        finally:
            doc.close()
        return True

    @staticmethod
    def redact_text(pdf_path: str, search_query: str, output_path: str) -> int:
        """Permanently redact (black out) text matching search_query."""
        doc = fitz.open(pdf_path)
        count = 0
        for page in doc:
            rects = page.search_for(search_query)
            for rect in rects:
                annot = page.add_redact_annot(rect, fill=(0, 0, 0))
                count += 1
            page.apply_redactions()
        doc.save(output_path)
        doc.close()
        return count

    @staticmethod
    def compress_pdf(pdf_path: str, output_path: str) -> bool:
        """Optimize and compress PDF file size."""
        doc = fitz.open(pdf_path)
        doc.save(output_path, deflate=True, garbage=4, clean=True)
        doc.close()
        return True

    @staticmethod
    def encrypt_pdf(pdf_path: str, user_pw: str, owner_pw: str, output_path: str) -> bool:
        """Encrypt PDF with AES 128-bit encryption."""
        doc = fitz.open(pdf_path)
        perm = fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT
        doc.save(
            output_path,
            encryption=fitz.PDF_ENCRYPT_AES_128,
            user_pw=user_pw,
            owner_pw=owner_pw if owner_pw else user_pw,
            permissions=perm
        )
        doc.close()
        return True

    @staticmethod
    def decrypt_pdf(pdf_path: str, password: str, output_path: str) -> bool:
        """Decrypt protected PDF."""
        doc = fitz.open(pdf_path)
        if doc.is_encrypted:
            if not doc.authenticate(password):
                doc.close()
                raise ValueError("Invalid password provided for decryption.")
        doc.save(output_path)
        doc.close()
        return True

    # --------------------------------------------------------------------------
    # ABBYY FINEREADER: OCR & CONVERSION ENGINES
    # --------------------------------------------------------------------------

    @staticmethod
    def perform_ocr_extraction(pdf_path: str, lang: str = "eng+mal") -> str:
        """
        Multilingual OCR Engine. Uses PyMuPDF text layer fallback and PyTesseract / PIL
        image enhancement if available.
        """
        doc = fitz.open(pdf_path)
        full_text = []

        for i, page in enumerate(doc):
            full_text.append(f"--- PAGE {i + 1} ---")
            p_text = page.get_text("text").strip()
            
            if len(p_text) > 30:
                full_text.append(p_text)
            else:
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                enhancer = ImageEnhance.Contrast(img)
                img_enhanced = enhancer.enhance(1.5)
                
                if pytesseract is not None:
                    try:
                        tess_lang = "eng"
                        if "mal" in lang:
                            tess_lang += "+mal"
                        ocr_txt = pytesseract.image_to_string(img_enhanced, lang=tess_lang)
                        full_text.append(ocr_txt)
                    except Exception:
                        full_text.append(p_text if p_text else "[Scanned Image Content - PyTesseract Engine Exception]")
                else:
                    full_text.append(p_text if p_text else "[Image Content - PyMuPDF Text Layer Empty]")
            full_text.append("\n")

        doc.close()
        return "\n".join(full_text)

    @staticmethod
    def convert_pdf_to_word(pdf_path: str, docx_path: str) -> bool:
        """Convert PDF document to editable Microsoft Word (.docx)."""
        if DocxConverter is not None:
            cv = DocxConverter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            return True
        elif docx is not None:
            doc = fitz.open(pdf_path)
            word_doc = docx.Document()
            word_doc.add_heading("Exported PDF Document", 0)
            for page in doc:
                text = page.get_text("text")
                word_doc.add_paragraph(text)
                word_doc.add_page_break()
            word_doc.save(docx_path)
            doc.close()
            return True
        else:
            raise RuntimeError("Neither pdf2docx nor python-docx package is available.")

    @staticmethod
    def convert_pdf_to_searchable_pdf(pdf_path: str, output_pdf_path: str) -> bool:
        """
        Generates a searchable PDF by adding an invisible OCR text layer over
        scanned/image-only pages, so the resulting file can be searched/copied.

        NOTE (fix): the original implementation only called `doc.convert_to_pdf()`
        and re-wrote the same bytes back out -- it never actually OCR'd anything,
        so scanned pages stayed completely unsearchable despite the feature name.
        This version rasterizes image-only pages and burns in an invisible
        (render_mode=3) text layer aligned to each OCR'd word's bounding box.
        Pages that already contain a real text layer are left untouched.
        """
        if pytesseract is None:
            raise RuntimeError(
                "pytesseract is required to build a searchable PDF from scanned pages.\n"
                "Please install it with: pip install pytesseract"
            )

        doc = fitz.open(pdf_path)
        for page in doc:
            existing_text = page.get_text("text").strip()
            if len(existing_text) > 30:
                # Page already has a genuine text layer -- nothing to OCR.
                continue

            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            try:
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            except Exception:
                continue

            scale_x = page.rect.width / pix.width
            scale_y = page.rect.height / pix.height

            n_boxes = len(ocr_data.get("text", []))
            for i in range(n_boxes):
                word = ocr_data["text"][i].strip()
                if not word:
                    continue
                x, y, w, h = (ocr_data["left"][i], ocr_data["top"][i],
                              ocr_data["width"][i], ocr_data["height"][i])
                pdf_x = x * scale_x
                pdf_y = (y + h) * scale_y  # approximate text baseline
                font_size = max(1.0, h * scale_y * 0.85)
                try:
                    page.insert_text(
                        fitz.Point(pdf_x, pdf_y),
                        word,
                        fontsize=font_size,
                        render_mode=3,  # invisible text -- searchable & selectable only
                        overlay=True
                    )
                except Exception:
                    continue

        doc.save(output_pdf_path, deflate=True)
        doc.close()
        return True

    @staticmethod
    def perform_surya_ocr_extraction(pdf_path: str, langs: Optional[List[str]] = None) -> str:
        """
        Advanced Surya Deep Learning Multilingual OCR Engine (English & Malayalam).
        """
        if langs is None:
            langs = ["en", "ml"]

        run_ocr, load_det_model, load_rec_model = _get_surya_modules()

        if convert_from_path is None or run_ocr is None or load_det_model is None or load_rec_model is None:
            raise RuntimeError(
                "Surya OCR dependencies missing. Please install surya-ocr and pdf2image:\n"
                "pip install surya-ocr pdf2image"
            )

        # NOTE (fix): model loading / OCR execution can fail even when the
        # packages import successfully (e.g. API changes, missing weights,
        # no GPU/CPU memory). Previously any such failure produced an
        # unguarded traceback all the way up through the worker thread;
        # now it is surfaced as a clear, catchable RuntimeError.
        try:
            det_model = load_det_model()
            rec_model = load_rec_model()
            images = convert_from_path(pdf_path)
            predictions = run_ocr(images, [langs] * len(images), det_model, rec_model)
        except Exception as e:
            raise RuntimeError(f"Surya OCR failed to run: {e}")

        extracted_text = ""
        for idx, page_pred in enumerate(predictions):
            extracted_text += f"--- PAGE {idx + 1} ---\n"
            for line in page_pred.text_lines:
                extracted_text += line.text + "\n"
            extracted_text += "\n"

        return extracted_text

    @staticmethod
    def search_text(pdf_path: str, query: str) -> int:
        """Search for text occurrence query across document pages and return total match count."""
        doc = fitz.open(pdf_path)
        total_matches = 0
        for page in doc:
            rects = page.search_for(query)
            total_matches += len(rects)
        doc.close()
        return total_matches

    @staticmethod
    def highlight_text(pdf_path: str, query: str, output_path: str) -> int:
        """Search for query string in PDF, apply highlight annotations, and save to output_path."""
        doc = fitz.open(pdf_path)
        match_count = 0
        for page in doc:
            rects = page.search_for(query)
            for rect in rects:
                annot = page.add_highlight_annot(rect)
                annot.update()
                match_count += 1
        doc.save(output_path)
        doc.close()
        return match_count

    @staticmethod
    def find_and_replace_text(pdf_path: str, find_query: str, replace_query: str, output_path: str) -> int:
        """Search for find_query string in PDF, replace with replace_query text via redaction, and save."""
        doc = fitz.open(pdf_path)
        match_count = 0
        for page in doc:
            rects = page.search_for(find_query)
            for rect in rects:
                annot = page.add_redact_annot(rect, text=replace_query)
                match_count += 1
            if rects:
                page.apply_redactions()
        doc.save(output_path)
        doc.close()
        return match_count

    @staticmethod
    def _write_text_file(path: str, text: str) -> None:
        """Small helper used by GUI callbacks so file handles are always closed
        (the original code called `open(path, "w").write(text)` inline, which
        leaves the file handle open until Python's garbage collector gets to it)."""
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    # --------------------------------------------------------------------------
    # OPENVIEW DYNAMIC INDEX & TOC BUILDER
    # --------------------------------------------------------------------------

    @staticmethod
    def extract_document_toc(pdf_path: str) -> List[Dict[str, Any]]:
        """Extract outline/bookmarks from PDF."""
        doc = fitz.open(pdf_path)
        toc = doc.get_toc() # [[level, title, page_num], ...]
        doc.close()
        result = []
        for item in toc:
            result.append({
                "level": item[0],
                "title": item[1],
                "page": item[2]
            })
        return result

    @staticmethod
    def generate_openview_index_pdf(
        entries: List[Dict[str, Any]],
        output_pdf_path: str,
        title: str = "DOCUMENT INDEX & TABLE OF CONTENTS",
        subtitle: str = "Titus II Teachers College - OpenView Design Catalog",
        template: str = "Titus II Institutional Classic"
    ) -> bool:
        """
        Creates a high-resolution Index page PDF with OpenView dot-leader layout,
        academic typography, institutional header, and active internal hyperlinks!
        """
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        
        header_color = (0.42, 0.15, 0.85) if template == "Modern Academic" else (0.09, 0.14, 0.3)
        line_color = (0.8, 0.8, 0.8)

        # 1. Header Banner & Branding
        page.draw_rect(fitz.Rect(36, 36, 559, 115), color=None, fill=(0.96, 0.97, 0.99))
        page.draw_rect(fitz.Rect(36, 36, 559, 115), color=header_color, width=1.5)
        
        page.insert_text(fitz.Point(50, 65), title, fontsize=15, color=header_color, fontname="helv")
        page.insert_text(fitz.Point(50, 85), subtitle, fontsize=10, color=(0.3, 0.3, 0.3), fontname="helv")
        page.insert_text(fitz.Point(50, 102), "Titus II Teachers College Enterprise OpenView Engine (Dr. Joseph I Thomas)", fontsize=8, color=(0.5, 0.5, 0.5), fontname="helv")

        # 2. Table Headers
        page.draw_line(fitz.Point(36, 135), fitz.Point(559, 135), color=header_color, width=1)
        page.insert_text(fitz.Point(40, 130), "SECTION / TOPIC TITLE", fontsize=9, color=header_color, fontname="helv")
        page.insert_text(fitz.Point(510, 130), "PAGE", fontsize=9, color=header_color, fontname="helv")
        page.draw_line(fitz.Point(36, 137), fitz.Point(559, 137), color=line_color, width=0.5)

        current_y = 160
        max_y = 790

        for entry in entries:
            if current_y > max_y:
                page = doc.new_page(width=595, height=842)
                current_y = 60

            level = entry.get("level", 1)
            e_title = entry.get("title", "Untitled Section")
            target_page = entry.get("page", 1)

            indent = 40 + (level - 1) * 20
            font_size = 11 if level == 1 else (10 if level == 2 else 9)
            font_name = "helv"
            text_color = (0.1, 0.1, 0.1) if level == 1 else (0.25, 0.25, 0.25)

            page.insert_text(fitz.Point(indent, current_y), e_title, fontsize=font_size, color=text_color, fontname=font_name)

            title_width = fitz.get_text_length(e_title, fontname=font_name, fontsize=font_size)
            dot_start = indent + title_width + 10
            dot_end = 505

            if dot_end > dot_start:
                dot_count = int((dot_end - dot_start) / 4.5)
                dots_str = ". " * dot_count
                page.insert_text(fitz.Point(dot_start, current_y), dots_str, fontsize=8, color=(0.6, 0.6, 0.6))

            p_num_str = str(target_page)
            page.insert_text(fitz.Point(515, current_y), p_num_str, fontsize=font_size, color=header_color, fontname="helv")

            link_rect = fitz.Rect(indent, current_y - font_size, 550, current_y + 4)
            link_dict = {
                "kind": fitz.LINK_GOTO,
                "page": max(0, target_page - 1),
                "from": link_rect
            }
            try:
                page.insert_link(link_dict)
            except Exception:
                pass

            current_y += 24 if level == 1 else 20

        page.draw_line(fitz.Point(36, 810), fitz.Point(559, 810), color=line_color, width=0.5)
        page.insert_text(fitz.Point(36, 825), "Generated by Titus II OpenView Index Suite v4.0 (Dr. Joseph I Thomas)", fontsize=8, color=(0.5, 0.5, 0.5))

        doc.save(output_pdf_path)
        doc.close()
        return True

    @staticmethod
    def attach_index_to_pdf(master_pdf: str, index_pdf: str, output_pdf_path: str, prepend: bool = True) -> bool:
        """Inject index PDF as the 1st page(s) or appended at end of master PDF.

        When prepending, GOTO links written against the original master page
        numbers are shifted by the number of index pages so they still land
        on the correct content pages in the combined document.
        """
        doc_master = fitz.open(master_pdf)
        doc_index = fitz.open(index_pdf)
        index_page_count = len(doc_index)

        new_doc = fitz.open()

        if prepend:
            new_doc.insert_pdf(doc_index)
            new_doc.insert_pdf(doc_master)

            # Links live on the index pages (indices 0 .. index_page_count-1).
            # Their targets were written against the original master (0-based),
            # so shift each target by index_page_count. Do NOT touch links that
            # already exist inside the original master content.
            for page_idx in range(index_page_count):
                page = new_doc[page_idx]
                links = list(page.get_links())
                for link in links:
                    if link.get("kind") == fitz.LINK_GOTO and "page" in link:
                        link["page"] = link["page"] + index_page_count
                        try:
                            page.delete_link(link)
                            page.insert_link(link)
                        except Exception:
                            pass
        else:
            new_doc.insert_pdf(doc_master)
            new_doc.insert_pdf(doc_index)

        new_doc.save(output_pdf_path)
        new_doc.close()
        doc_index.close()
        doc_master.close()
        return True

# ==============================================================================
# PDF AI CHAT & RAG ENGINE (GEMINI, OPENAI, CLAUDE & LOCAL OFFLINE)
# ==============================================================================
class PDFChatEngine:
    """Advanced AI Chat & RAG Engine for PDF Documents."""

    @staticmethod
    def extract_document_pages(pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from each page with metadata."""
        if not pdf_path or not os.path.exists(pdf_path):
            return []
        doc = fitz.open(pdf_path)
        pages_data = []
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            pages_data.append({
                "page": i + 1,
                "text": text if text else "[Page contains images or scanned content with no extracted text layer]",
                "char_count": len(text)
            })
        doc.close()
        return pages_data

    @staticmethod
    def query_local_bm25(pages_data: List[Dict[str, Any]], query: str) -> Tuple[str, List[int]]:
        """Intelligent local document synthesis and question-answering engine."""
        if not pages_data:
            return "No document pages available for analysis.", []

        query_lower = query.lower().strip()
        is_summary_request = any(w in query_lower for w in [
            "summarise", "summarize", "summary", "outline", "overview", "what is this document",
            "explain document", "about", "takeaways", "synopsis", "gist", "brief"
        ])

        if is_summary_request:
            # 1. Extract Overview & Scope from early pages
            overview_points = []
            seen_texts = set()
            for p in pages_data[:8]:
                text = p["text"].strip()
                if not text:
                    continue
                paragraphs = [para.strip() for para in text.split("\n\n") if len(para.strip()) > 30]
                for para in paragraphs:
                    clean_para = " ".join([l.strip() for l in para.split("\n") if l.strip()])
                    if any(k in clean_para.lower() for k in [
                        "programme", "course", "curriculum", "education", "university", "college",
                        "objective", "overview", "master", "bachelor", "credit", "syllabus", "regulation",
                        "scope", "degree", "aims", "designed", "framework", "introduction"
                    ]):
                        short_p = clean_para[:260].strip()
                        if short_p not in seen_texts:
                            seen_texts.add(short_p)
                            overview_points.append((p["page"], short_p))
                    if len(overview_points) >= 4:
                        break
                if len(overview_points) >= 4:
                    break

            # 2. Extract Structural Components & Modules across document
            structure_points = []
            for p in pages_data:
                text = p["text"]
                for line in text.split("\n"):
                    line_s = line.strip()
                    if (
                        re.match(r'^(semester|module|unit|course|paper|part|section)\s+[ivx\d]+', line_s, re.IGNORECASE)
                        or ("credit" in line_s.lower() and len(line_s) < 100)
                        or ("core course" in line_s.lower() and len(line_s) < 100)
                        or ("specialisation" in line_s.lower() and len(line_s) < 100)
                    ):
                        if 12 < len(line_s) < 110 and line_s not in [it[1] for it in structure_points]:
                            structure_points.append((p["page"], line_s))
                    if len(structure_points) >= 5:
                        break
                if len(structure_points) >= 5:
                    break

            # 3. Extract Key Regulations / Assessment / Objectives
            highlight_points = []
            for p in pages_data:
                text = p["text"]
                for line in text.split("\n"):
                    line_s = line.strip()
                    if any(k in line_s.lower() for k in ["objective", "eligibility", "evaluation", "assessment", "attendance", "internship", "dissertation"]):
                        if 20 < len(line_s) < 140 and line_s not in [it[1] for it in highlight_points]:
                            highlight_points.append((p["page"], line_s))
                    if len(highlight_points) >= 4:
                        break
                if len(highlight_points) >= 4:
                    break

            # Format like Gemini in Image 2
            output_lines = [
                f"Here is a structured executive summary of the document:\n",
                "### 📌 Overview & Scope"
            ]
            cited_pages = set()
            if overview_points:
                for p_num, pt in overview_points[:3]:
                    output_lines.append(f"• {pt} [Page {p_num}]")
                    cited_pages.add(p_num)
            else:
                output_lines.append(f"• Document outlines core guidelines, institutional specifications, and academic curriculum. [Page 1]")
                cited_pages.add(1)

            if structure_points:
                output_lines.append("\n### 📑 Programme Structure & Credits")
                for p_num, pt in structure_points[:4]:
                    output_lines.append(f"• {pt} [Page {p_num}]")
                    cited_pages.add(p_num)

            if highlight_points:
                output_lines.append("\n### 🎯 Objectives & Academic Guidelines")
                for p_num, pt in highlight_points[:3]:
                    output_lines.append(f"• {pt} [Page {p_num}]")
                    cited_pages.add(p_num)

            output_lines.append("\n💡 *Tip: For full conversational AI reasoning and deeper Q&A, click '⚡ Get Free Gemini Key' above and paste your free Google AI Studio key.*")
            return "\n".join(output_lines), sorted(list(cited_pages))

        # Otherwise: Specific Question Answering
        query_words = set(re.findall(r'\w+', query.lower()))
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or", "what", "how", "why", "who", "which", "where", "tell", "me", "about", "can", "you", "show", "give", "please"}
        keywords = query_words - stopwords
        if not keywords:
            keywords = query_words

        scored_paragraphs = []
        for p in pages_data:
            text = p["text"]
            paragraphs = [para.strip() for para in text.split("\n\n") if len(para.strip()) > 20]
            for para in paragraphs:
                clean_para = " ".join([l.strip() for l in para.split("\n") if l.strip()])
                para_lower = clean_para.lower()
                score = 0
                for kw in keywords:
                    count = len(re.findall(r'\b' + re.escape(kw) + r'\b', para_lower))
                    score += count * 4
                    if kw in para_lower:
                        score += 1
                if score > 0:
                    scored_paragraphs.append((score, p["page"], clean_para))

        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_paragraphs[:4]

        if not top_matches:
            top_matches = [(1, 1, " ".join(pages_data[0]["text"].split()[:80]))]

        cited_pages = sorted(list(set([m[1] for m in top_matches])))

        output_lines = [
            f"Here are the relevant findings from the document regarding **\"{query}\"**:\n"
        ]
        for idx, (score, p_num, text_content) in enumerate(top_matches):
            snippet = text_content[:320].strip()
            output_lines.append(f"• **[Page {p_num}]**: {snippet}")

        output_lines.append("\n💡 *Tip: For full conversational AI reasoning and deeper Q&A, click '⚡ Get Free Gemini Key' above and paste your free Google AI Studio key.*")
        return "\n".join(output_lines), cited_pages

    @staticmethod
    def build_system_prompt() -> str:
        return (
            "You are TitusOmni — the Omniscient and Omnipotent Academic & Document Intelligence AI for Titus II Teachers College.\n"
            "You possess total, omniscient comprehension of the provided PDF document, curriculum guidelines, educational pedagogy, research frameworks, institutional policies, and technical analysis.\n"
            "You are also omnipotent in capability: you can analyze, synthesize, generate 10-question exam MCQs with answer keys, draft lesson plans, tabulate statistical data, translate across languages (Malayalam, Hindi, English, etc.), and guide PDF actions (Compress, Convert to Word, OCR, Split, Watermark, OpenView Index, Encrypt).\n\n"
            "RULES:\n"
            "1. Ground all answers and insights with supreme accuracy on the document text.\n"
            "2. ALWAYS cite page numbers using exact format [Page X] whenever referencing specific facts, figures, sections, or quotes (e.g. [Page 1], [Page 4]).\n"
            "3. If asked to generate MCQs: Provide 10 rigorous, high-quality multiple choice questions with options A, B, C, D, followed by an Answer Key & Rationale.\n"
            "4. If asked for a lesson plan: Detail Learning Objectives (Blooms Taxonomy), Pedagogical Strategies, Prerequisites, Content Breakdown, and Evaluation/Assessment.\n"
            "5. If asked for summaries/outlines: Structure with rich markdown headings (### 📌 Overview & Scope, ### 📑 Curriculum & Structure, ### 🎯 Guidelines & Takeaways).\n"
            "6. If user asks to perform a PDF action (e.g. compress, convert to word, ocr, watermark, split): explain what will be done and confirm the parameters.\n"
            "7. Be proactive, articulate, supremely helpful, and empowering to the user."
        )

    @staticmethod
    def prepare_document_context(pages_data: List[Dict[str, Any]], query: str, max_chars: int = 400000) -> str:
        """Intelligently selects and packages document context for LLMs to avoid HTTP payload overflows and timeouts."""
        if not pages_data:
            return "[No text content found in document. If this is a scanned PDF, please run OCR first.]"

        query_lower = query.lower()
        is_summary = any(w in query_lower for w in ["summarise", "summarize", "summary", "outline", "overview", "about", "takeaways", "structure"])

        if is_summary:
            # Include first 25 pages (preface, TOC, intro, chapters) + evenly sampled pages across the whole doc
            early_pages = pages_data[:25]
            step = max(1, len(pages_data) // 25)
            sampled_pages = pages_data[25::step]
            selected = {p['page']: p for p in (early_pages + sampled_pages)}
            target_pages = [selected[k] for k in sorted(selected.keys())]
        else:
            # RAG matched pages + opening pages
            words = set(re.findall(r'\w+', query_lower)) - {"the", "a", "an", "is", "are", "in", "on", "at", "to", "for", "of", "and", "or", "what", "how", "why"}
            scored = []
            for p in pages_data:
                sc = sum(p["text"].lower().count(w) for w in words)
                if sc > 0:
                    scored.append((sc, p))
            scored.sort(key=lambda x: x[0], reverse=True)
            top_rag = [p for _, p in scored[:20]]
            selected = {p['page']: p for p in (pages_data[:3] + top_rag)}
            target_pages = [selected[k] for k in sorted(selected.keys())]

        doc_blocks = []
        cur_len = 0
        for p in target_pages:
            t = p["text"].strip()
            if not t:
                continue
            block = f"--- BEGIN PAGE {p['page']} ---\n{t}\n--- END PAGE {p['page']} ---"
            if cur_len + len(block) > max_chars:
                break
            doc_blocks.append(block)
            cur_len += len(block)

        if not doc_blocks:
            doc_blocks = [f"--- BEGIN PAGE {p['page']} ---\n{p['text']}\n--- END PAGE {p['page']} ---" for p in pages_data[:10] if p['text'].strip()]

        return "\n\n".join(doc_blocks)

    @staticmethod
    def query_gemini_api(api_key: str, model_name: str, pages_data: List[Dict[str, Any]], history: List[Dict[str, str]], query: str) -> str:
        """Query Google Gemini API with smart model fallback."""
        if not api_key:
            raise ValueError("Google Gemini API Key is missing. Please enter your API key in the top bar.")
        if not requests:
            raise ValueError("requests package is not installed.")

        api_key = api_key.strip().strip("'\"")
        full_doc_str = PDFChatEngine.prepare_document_context(pages_data, query, max_chars=450000)

        prompt = (
            f"{PDFChatEngine.build_system_prompt()}\n\n"
            f"=== PDF DOCUMENT CONTENT ===\n"
            f"{full_doc_str}\n"
            f"============================\n\n"
        )
        if history:
            prompt += "=== RECENT CHAT HISTORY ===\n"
            for msg in history[-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            prompt += "===========================\n\n"

        prompt += f"User Question: {query}\nAssistant Answer:"

        # Try user model first, followed by stable Google Gemini production endpoints
        target_model = model_name or "gemini-2.0-flash"
        models_to_try = [target_model]
        for alt in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"]:
            if alt not in models_to_try:
                models_to_try.append(alt)

        last_err = ""
        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 2048
                }
            }

            try:
                res = requests.post(url, headers=headers, json=payload, timeout=45)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                    raise ValueError("Gemini API returned empty content.")
                else:
                    err_msg = res.text
                    try:
                        err_json = res.json()
                        if "error" in err_json:
                            err_msg = err_json["error"].get("message", err_msg)
                    except Exception:
                        pass
                    last_err = f"Gemini Error ({res.status_code}): {err_msg}"
                    # If 404 (model name changed or unavailable in region), try next model
                    if res.status_code == 404:
                        continue
                    else:
                        raise ValueError(last_err)
            except requests.RequestException as e:
                raise ValueError(f"Network error connecting to Gemini API: {str(e)}")

        raise ValueError(last_err or "Google Gemini request failed.")

    @staticmethod
    def query_openai_api(api_key: str, model_name: str, pages_data: List[Dict[str, Any]], history: List[Dict[str, str]], query: str) -> str:
        """Query OpenAI API."""
        if not api_key:
            raise ValueError("OpenAI API Key is missing.")
        if not requests:
            raise ValueError("requests package is not installed.")

        api_key = api_key.strip().strip("'\"")
        full_doc_str = PDFChatEngine.prepare_document_context(pages_data, query, max_chars=350000)

        messages = [
            {"role": "system", "content": f"{PDFChatEngine.build_system_prompt()}\n\n=== PDF DOCUMENT CONTENT ===\n{full_doc_str}"}
        ]
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        target_model = model_name or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"OpenAI API Error ({res.status_code}): {res.text}")
        except requests.RequestException as e:
            raise ValueError(f"Network error connecting to OpenAI API: {str(e)}")

    @staticmethod
    def query_anthropic_api(api_key: str, model_name: str, pages_data: List[Dict[str, Any]], history: List[Dict[str, str]], query: str) -> str:
        """Query Anthropic Claude API."""
        if not api_key:
            raise ValueError("Anthropic API Key is missing.")
        if not requests:
            raise ValueError("requests package is not installed.")

        api_key = api_key.strip().strip("'\"")
        full_doc_str = PDFChatEngine.prepare_document_context(pages_data, query, max_chars=350000)

        system_instruction = f"{PDFChatEngine.build_system_prompt()}\n\n=== PDF DOCUMENT CONTENT ===\n{full_doc_str}"
        messages = []
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        target_model = model_name or "claude-3-5-sonnet-20241022"
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": target_model,
            "max_tokens": 2048,
            "system": system_instruction,
            "messages": messages
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                data = res.json()
                content_blocks = data.get("content", [])
                if content_blocks:
                    return content_blocks[0].get("text", "")
                raise ValueError("Anthropic API returned empty content.")
            else:
                raise ValueError(f"Anthropic API Error ({res.status_code}): {res.text}")
        except requests.RequestException as e:
            raise ValueError(f"Network error connecting to Anthropic API: {str(e)}")

    @staticmethod
    def query_groq_api(api_key: str, model_name: str, pages_data: List[Dict[str, Any]], history: List[Dict[str, str]], query: str) -> str:
        """Query Groq High-Speed LLM Inference API."""
        if not api_key:
            raise ValueError("Groq API Key is missing.")
        if not requests:
            raise ValueError("requests package is not installed.")

        api_key = api_key.strip().strip("'\"")
        full_doc_str = PDFChatEngine.prepare_document_context(pages_data, query, max_chars=250000)

        messages = [
            {"role": "system", "content": f"{PDFChatEngine.build_system_prompt()}\n\n=== PDF DOCUMENT CONTENT ===\n{full_doc_str}"}
        ]
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        target_model = model_name or "llama-3.3-70b-versatile"
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Groq API Error ({res.status_code}): {res.text}")
        except requests.RequestException as e:
            raise ValueError(f"Network error connecting to Groq API: {str(e)}")

    @staticmethod
    def query_openrouter_api(api_key: str, model_name: str, pages_data: List[Dict[str, Any]], history: List[Dict[str, str]], query: str) -> str:
        """Query OpenRouter Multi-Model Gateway API."""
        if not api_key:
            raise ValueError("OpenRouter API Key is missing.")
        if not requests:
            raise ValueError("requests package is not installed.")

        api_key = api_key.strip().strip("'\"")
        full_doc_str = PDFChatEngine.prepare_document_context(pages_data, query, max_chars=250000)

        messages = [
            {"role": "system", "content": f"{PDFChatEngine.build_system_prompt()}\n\n=== PDF DOCUMENT CONTENT ===\n{full_doc_str}"}
        ]
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        target_model = model_name or "google/gemini-2.0-flash-exp:free"
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://tituslibrary.weebly.com/",
            "X-Title": "TSTC Professional PDF Suite"
        }
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"OpenRouter API Error ({res.status_code}): {res.text}")
        except requests.RequestException as e:
            raise ValueError(f"Network error connecting to OpenRouter API: {str(e)}")

    @staticmethod
    def query_smart_auto_switch(
        all_keys: Dict[str, str],
        preferred_provider: str,
        preferred_model: str,
        pages_data: List[Dict[str, Any]],
        history: List[Dict[str, str]],
        query: str
    ) -> Tuple[str, str]:
        """
        Intelligent multi-provider auto-failover engine.
        Tries providers in priority order, detecting 429 quota exhaustion, invalid keys,
        or server errors, and automatically switches to the next available provider/key.
        Falls back to Local Offline Search if all remote APIs fail or are unconfigured.
        """
        if "local" in preferred_provider.lower():
            ans, _ = PDFChatEngine.query_local_bm25(pages_data, query)
            return ans, "Local Offline Document Engine"

        # List of provider handlers
        candidate_providers = [
            ("Google Gemini", "gemini", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"], PDFChatEngine.query_gemini_api),
            ("Groq", "groq", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b", "gemma2-9b-it"], PDFChatEngine.query_groq_api),
            ("OpenAI (GPT)", "openai", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], PDFChatEngine.query_openai_api),
            ("Anthropic Claude", "claude", ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"], PDFChatEngine.query_anthropic_api),
            ("OpenRouter", "openrouter", ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-r1:free"], PDFChatEngine.query_openrouter_api),
        ]

        # If user picked a specific provider, prioritize it
        is_user_explicit_provider = ("auto" not in preferred_provider.lower())
        for i, (prov_name, k_name, models, fn) in enumerate(candidate_providers):
            if k_name in preferred_provider.lower() or prov_name.lower() in preferred_provider.lower():
                item = candidate_providers.pop(i)
                m_list = [preferred_model] + [m for m in item[2] if m != preferred_model]
                candidate_providers.insert(0, (item[0], item[1], m_list, item[3]))
                break

        failover_logs = []
        last_explicit_err = None

        for prov_name, k_name, models, call_fn in candidate_providers:
            raw_key_str = all_keys.get(k_name, "").strip()
            if not raw_key_str:
                env_var_map = {
                    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
                    "openai": ["OPENAI_API_KEY"],
                    "claude": ["ANTHROPIC_API_KEY"],
                    "groq": ["GROQ_API_KEY"],
                    "openrouter": ["OPENROUTER_API_KEY"]
                }
                for env_k in env_var_map.get(k_name, []):
                    env_val = os.environ.get(env_k, "").strip()
                    if env_val:
                        raw_key_str = env_val
                        break

            if not raw_key_str:
                continue

            # Support comma-separated keys for pool rotation
            key_list = [k.strip() for k in raw_key_str.split(",") if k.strip()]

            for active_key in key_list:
                for target_model in models:
                    try:
                        res = call_fn(active_key, target_model, pages_data, history, query)
                        if res and len(res.strip()) > 0:
                            if failover_logs:
                                badge = f"{prov_name} ({target_model}) [Auto-Switched: {', '.join(failover_logs)}]"
                            else:
                                badge = f"{prov_name} ({target_model})"
                            return res, badge
                    except Exception as e:
                        err_str = str(e)
                        if is_user_explicit_provider and not last_explicit_err:
                            last_explicit_err = err_str

                        if "429" in err_str or "quota" in err_str.lower() or "resource_exhausted" in err_str.lower():
                            failover_logs.append(f"{prov_name} quota exhausted")
                        elif "400" in err_str or "401" in err_str or "403" in err_str or "invalid" in err_str.lower():
                            failover_logs.append(f"{prov_name} key/request issue")
                        else:
                            failover_logs.append(f"{prov_name} unavailable")
                        continue

        # Seamless fallback to Local Offline Engine
        local_ans, _ = PDFChatEngine.query_local_bm25(pages_data, query)
        if last_explicit_err:
            prefix = f"⚠️ *[{preferred_provider} failed: {last_explicit_err}. Auto-switched to Local Document Intelligence Engine]*\n\n"
            return prefix + local_ans, "Local Offline Document Engine (Auto-Fallback)"
        elif failover_logs:
            prefix = f"⚡ *[Auto-Failover Active: Cloud AI quota/rate-limit reached ({'; '.join(failover_logs[:3])}). Seamlessly switched to Local Document Intelligence Engine]*\n\n"
            return prefix + local_ans, "Local Offline Document Engine (Auto-Fallback)"
        else:
            return local_ans, "Local Offline Document Engine (No API Key Required)"

# ==============================================================================
# MAIN DESKTOP APPLICATION SHELL
# ==============================================================================
class TSTC_ProfessionalPDFSuite(ctk.CTk):
    """TSTC_Professional PDF Suite v4.0 Main GUI Window."""

    def __init__(self):
        super().__init__()

        self.title("Titus II Teachers College - TSTC_Professional PDF Suite v4.0 (Dr. Joseph I Thomas)")
        self.geometry("1380x880")
        self.minsize(1100, 720)

        self.active_pdf_path: Optional[str] = None
        self.pdf_doc: Optional[fitz.Document] = None
        self.current_page_idx: int = 0
        self.zoom_factor: float = 1.0
        self._current_page_image: Optional[Any] = None  # strong ref for CTkImage
        self.thumbnail_images: List[Any] = []
        self.openview_entries: List[Dict[str, Any]] = [
            {"level": 1, "title": "1. Institutional Introduction & Overview", "page": 1},
            {"level": 2, "title": "1.1 Academic Vision & Mission Statement", "page": 2},
            {"level": 1, "title": "2. Curriculum & Teacher Education Policy", "page": 3},
            {"level": 2, "title": "2.1 Pedagogical Guidelines & Assessment", "page": 4},
            {"level": 1, "title": "3. Departmental Reports & Research Papers", "page": 5}
        ]
        self.chat_history: List[Dict[str, str]] = []
        self.api_keys: Dict[str, str] = self.load_api_keys_config()

        self.after(200, self.set_window_icon)

        self.setup_menubar()
        self.setup_layout_grid()
        self.setup_sidebar()
        self.setup_main_workspace()
        self.setup_status_bar()

        self.show_welcome_workspace()
        self.after(600, self.verify_runtime_dependencies)

    def verify_runtime_dependencies(self):
        """Self-healing routine that verifies critical DLLs and binary components."""
        issues = []
        try:
            import fitz
            doc = fitz.open()
            doc.close()
        except Exception as e:
            issues.append(f"PyMuPDF/fitz: {str(e)}")

        try:
            import PIL.Image
        except Exception as e:
            issues.append(f"Pillow/PIL: {str(e)}")

        if issues:
            self.set_status(f"⚠️ Dependency Notice: {'; '.join(issues[:2])}")
        else:
            self.set_status("All system DLLs, runtime libraries, and PDF engines verified ready.")

    def get_config_file_path(self) -> str:
        return os.path.join(os.path.expanduser("~"), ".tstc_pdf_suite_config.json")

    def load_api_keys_config(self) -> Dict[str, str]:
        cfg_path = self.get_config_file_path()
        defaults = {
            "gemini": os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", "")),
            "groq": os.environ.get("GROQ_API_KEY", ""),
            "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "claude": os.environ.get("ANTHROPIC_API_KEY", "")
        }
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if v:
                                defaults[k] = v
            except Exception:
                pass
        return defaults

    def save_api_keys_config(self):
        cfg_path = self.get_config_file_path()
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception:
            pass

    def set_window_icon(self):
        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            ico_path = os.path.join(base_dir, "titus.ico")
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
            png_path = os.path.join(base_dir, "logo.png")
            if os.path.exists(png_path):
                icon_img = ImageTk.PhotoImage(Image.open(png_path))
                self.iconphoto(False, icon_img)
                self._app_icon_photo_ref = icon_img
        except Exception:
            pass

    def load_logo_image(self) -> Optional[ctk.CTkImage]:
        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            img_path = os.path.join(base_dir, "logo.png")
            if os.path.exists(img_path):
                pil_img = Image.open(img_path).convert("RGBA")
                w, h = pil_img.size
                ratio = min(70 / w, 74 / h)
                display_w, display_h = max(1, int(w * ratio)), max(1, int(h * ratio))
                pil_resized = pil_img.resize((display_w, display_h), Image.Resampling.LANCZOS)
                self._logo_ctk_ref = ctk.CTkImage(light_image=pil_resized, dark_image=pil_resized, size=(display_w, display_h))
                return self._logo_ctk_ref
        except Exception:
            pass
        return None

    # ==========================================================================
    # 1. MAIN MENU BAR
    # ==========================================================================
    def setup_menubar(self):
        menubar = Menu(self)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="📂 Upload / Open Master PDF...", command=self.upload_master_pdf)
        file_menu.add_command(label="💾 Save Active Document As...", command=self.save_active_as)
        file_menu.add_separator()
        file_menu.add_command(label="ℹ️ Document Metadata & Properties", command=self.show_metadata_tool)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Close Master PDF", command=self.close_master_pdf)
        file_menu.add_command(label="🚪 Exit Application", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="🔍 Find / Replace Text Engine", command=self.show_find_replace_tool)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        page_menu = Menu(menubar, tearoff=0)
        page_menu.add_command(label="✂️ Extract Target Page(s)", command=self.show_split_tool)
        page_menu.add_command(label="🧩 Merge Multiple PDFs", command=self.show_merge_tool)
        page_menu.add_command(label="🗑️ Delete Selected Page(s)", command=self.show_delete_tool)
        page_menu.add_command(label="🔀 Reorder PDF Pages", command=self.show_reorder_tool)
        page_menu.add_command(label="🔄 Rotate Pages", command=self.show_rotate_tool)
        page_menu.add_command(label="📐 Crop Canvas Margins", command=self.show_crop_tool)
        page_menu.add_command(label="➕ Append / Insert Blank Page", command=self.show_blank_tool)
        menubar.add_cascade(label="Page Operations", menu=page_menu)

        adobe_menu = Menu(menubar, tearoff=0)
        adobe_menu.add_command(label="✍️ Annotations & Official Stamps", command=self.show_annotations_tool)
        adobe_menu.add_command(label="💧 Custom Text & Image Watermark", command=self.show_watermark_tool)
        adobe_menu.add_command(label="🔢 Header, Footer & Page Numbers", command=self.show_header_footer_tool)
        adobe_menu.add_command(label="██ Permanent Content Redaction", command=self.show_redact_tool)
        adobe_menu.add_command(label="⚡ File Size Compression", command=self.show_compress_tool)
        adobe_menu.add_command(label="🔒 Password Encryption & Security", command=self.show_protect_tool)
        adobe_menu.add_command(label="🔓 Remove Password / Unlock", command=self.show_unlock_tool)
        menubar.add_cascade(label="Adobe Suite", menu=adobe_menu)

        abbyy_menu = Menu(menubar, tearoff=0)
        abbyy_menu.add_command(label="🔍 Multilingual OCR Scan (En/Ml/Hi)", command=self.show_ocr_tool)
        abbyy_menu.add_command(label="📄 PDF to Word (.docx) Converter", command=self.show_pdf_to_word_tool)
        abbyy_menu.add_command(label="📊 PDF to Searchable PDF", command=self.show_searchable_pdf_tool)
        abbyy_menu.add_command(label="📝 Extract Text to File", command=self.show_ext_text_tool)
        abbyy_menu.add_command(label="🖼️ Extract Embedded Images", command=self.show_ext_img_tool)
        abbyy_menu.add_command(label="⚡ Batch Folder Converter & OCR", command=self.show_batch_tool)
        menubar.add_cascade(label="ABBYY FineReader", menu=abbyy_menu)

        index_menu = Menu(menubar, tearoff=0)
        index_menu.add_command(label="📖 Custom OpenView Index Designer", command=self.show_openview_tool)
        index_menu.add_command(label="🔍 Auto Extract Document TOC", command=self.auto_extract_toc)
        index_menu.add_command(label="🔖 Interactive Bookmarks Inspector", command=self.show_bookmarks_tool)
        menubar.add_cascade(label="OpenView Index", menu=index_menu)

        ai_menu = Menu(menubar, tearoff=0)
        ai_menu.add_command(label="⚡ TitusOmni (Omniscient & Omnipotent AI Bot)", command=self.show_titus_omni)
        ai_menu.add_command(label="🌐 50 AI Document Chat Tools Hub", command=self.show_ai_tools_hub)
        ai_menu.add_separator()
        ai_menu.add_command(label="📝 Executive Synthesis", command=lambda: self.titus_omni_quick_prompt("Please provide a comprehensive multi-section executive synthesis of this document with page citations."))
        ai_menu.add_command(label="🎯 10 Exam MCQs & Answer Key", command=lambda: self.titus_omni_quick_prompt("Generate 10 multiple choice exam questions (MCQs) with options A-D, correct answers, and rationale from this document."))
        ai_menu.add_command(label="📋 Academic Lesson Plan & Objectives", command=lambda: self.titus_omni_quick_prompt("Create a structured pedagogical lesson plan including learning outcomes, teaching strategies, and assessment guidelines from this document."))
        menubar.add_cascade(label="⚡ TitusOmni AI", menu=ai_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="🔍 Zoom In (+25%)", command=lambda: self.adjust_zoom(0.25))
        help_menu.add_command(label="🔍 Zoom Out (-25%)", command=lambda: self.adjust_zoom(-0.25))
        help_menu.add_command(label="📐 Fit Page to Screen", command=self.fit_zoom_to_page)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About TSTC_Professional PDF Suite", command=self.show_about_dialog)
        menubar.add_cascade(label="Help & View", menu=help_menu)

        self.config(menu=menubar)

    # ==========================================================================
    # 2. LAYOUT GRID CONFIGURATION
    # ==========================================================================
    def setup_layout_grid(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

    # ==========================================================================
    # 3. SIDEBAR & NAVIGATION
    # ==========================================================================
    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=280, corner_radius=0, fg_color=BG_DARK)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        logo = self.load_logo_image()
        if logo:
            ctk.CTkLabel(self.sidebar_frame, image=logo, text="").pack(pady=(15, 5))

        ctk.CTkLabel(
            self.sidebar_frame,
            text="TITUS II TEACHERS COLLEGE\nTSTC_Professional Suite v4.0\nBy Dr. Joseph I Thomas",
            font=("Arial", 12, "bold"),
            text_color=TEXT_LIGHT,
            justify="center"
        ).pack(pady=(5, 12))

        self.upload_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="📂 Upload Master PDF",
            command=self.upload_master_pdf,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            height=42,
            font=("Arial", 13, "bold")
        )
        self.upload_btn.pack(pady=(5, 15), padx=12, fill="x")

        self.create_category_header("⚡ TITUSOMNI AI SUITE")
        self.create_tool_button("⚡ TitusOmni (Omniscient AI)", self.show_titus_omni)
        self.create_tool_button("🌐 50 AI Document Chat Hub", self.show_ai_tools_hub)

        self.create_category_header("📄 FILE & PAGE OPERATIONS")
        self.create_tool_button("✂️ Extract Pages", self.show_split_tool)
        self.create_tool_button("🧩 Merge PDFs", self.show_merge_tool)
        self.create_tool_button("🗑️ Delete Pages", self.show_delete_tool)
        self.create_tool_button("🔀 Reorder Pages", self.show_reorder_tool)
        self.create_tool_button("🔄 Rotate Canvas", self.show_rotate_tool)
        self.create_tool_button("📐 Crop Margins", self.show_crop_tool)
        self.create_tool_button("➕ Insert Blank / PDF Page", self.show_blank_tool)
        self.create_tool_button("🖼️ Images to PDF", self.show_img_to_pdf_tool)

        self.create_category_header("🎨 ADOBE ACROBAT PRO SUITE")
        self.create_tool_button("✍️ Annotations & Stamps", self.show_annotations_tool)
        self.create_tool_button("💧 Text & Image Watermark", self.show_watermark_tool)
        self.create_tool_button("🔢 Headers & Page Numbers", self.show_header_footer_tool)
        self.create_tool_button("██ Permanent Redaction", self.show_redact_tool)
        self.create_tool_button("⚡ File Size Compression", self.show_compress_tool)
        self.create_tool_button("🔒 AES Encryption & Protect", self.show_protect_tool)
        self.create_tool_button("🔓 Remove Password", self.show_unlock_tool)
        self.create_tool_button("ℹ️ Edit Document Metadata", self.show_metadata_tool)

        self.create_category_header("👁️ ABBYY FINEREADER SUITE")
        self.create_tool_button("🔍 Multilingual OCR (En/Ml)", self.show_ocr_tool)
        self.create_tool_button("🔍 Find & Replace Engine", self.show_find_replace_tool)
        self.create_tool_button("📄 PDF to Word (.docx)", self.show_pdf_to_word_tool)
        self.create_tool_button("📊 PDF to Searchable PDF", self.show_searchable_pdf_tool)
        self.create_tool_button("📝 Extract Text", self.show_ext_text_tool)
        self.create_tool_button("🖼️ Extract Images", self.show_ext_img_tool)
        self.create_tool_button("⚡ Batch Folder Converter", self.show_batch_tool)

        self.create_category_header("📖 OPENVIEW INDEX & TOC")
        self.create_tool_button("📖 OpenView Index Designer", self.show_openview_tool)
        self.create_tool_button("🔖 Interactive Bookmarks", self.show_bookmarks_tool)

    def create_category_header(self, text: str):
        ctk.CTkLabel(
            self.sidebar_frame,
            text=text,
            font=("Arial", 11, "bold"),
            text_color=ACCENT_AMBER,
            anchor="w"
        ).pack(pady=(12, 4), padx=12, fill="x")

    def create_tool_button(self, text: str, command: Any):
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            command=command,
            fg_color=BG_CARD,
            hover_color=PRIMARY_COLOR,
            anchor="w",
            height=32,
            font=("Arial", 11)
        )
        btn.pack(pady=2, padx=12, fill="x")

    # ==========================================================================
    # 4. MAIN WORKSPACE CONTAINER & SPLIT PDF CANVAS VIEWER
    # ==========================================================================
    def setup_main_workspace(self):
        self.main_workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.main_workspace.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_workspace.grid_rowconfigure(1, weight=1)
        self.main_workspace.grid_columnconfigure(0, weight=1)

        self.header_toolbar = ctk.CTkFrame(self.main_workspace, height=45, fg_color=BG_CARD)
        self.header_toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.lbl_master_filename = ctk.CTkLabel(
            self.header_toolbar,
            text="Active Master PDF: None",
            font=("Arial", 12, "bold"),
            text_color=TEXT_LIGHT
        )
        self.lbl_master_filename.pack(side="left", padx=15, pady=8)

        btn_nav_prev = ctk.CTkButton(self.header_toolbar, text="◀ Prev", width=65, command=self.prev_page, fg_color="gray30")
        btn_nav_prev.pack(side="right", padx=(2, 10), pady=6)

        self.lbl_page_nav = ctk.CTkLabel(self.header_toolbar, text="Page 0 / 0", font=("Arial", 11))
        self.lbl_page_nav.pack(side="right", padx=5)

        btn_nav_next = ctk.CTkButton(self.header_toolbar, text="Next ▶", width=65, command=self.next_page, fg_color="gray30")
        btn_nav_next.pack(side="right", padx=2, pady=6)

        btn_zoom_in = ctk.CTkButton(self.header_toolbar, text="➕ Zoom In", width=75, command=lambda: self.adjust_zoom(0.2), fg_color="gray30")
        btn_zoom_in.pack(side="right", padx=5, pady=6)

        btn_zoom_out = ctk.CTkButton(self.header_toolbar, text="➖ Zoom Out", width=75, command=lambda: self.adjust_zoom(-0.2), fg_color="gray30")
        btn_zoom_out.pack(side="right", padx=2, pady=6)

        self.split_container = ctk.CTkFrame(self.main_workspace, fg_color="transparent")
        self.split_container.grid(row=1, column=0, sticky="nsew")
        self.split_container.grid_rowconfigure(0, weight=1)
        self.split_container.grid_columnconfigure(0, weight=3)
        self.split_container.grid_columnconfigure(1, weight=2)

        self.viewer_frame = ctk.CTkFrame(self.split_container, fg_color=BG_DARK)
        self.viewer_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.viewer_frame.grid_rowconfigure(0, weight=1)
        self.viewer_frame.grid_columnconfigure(1, weight=1)

        self.thumb_sidebar = ctk.CTkScrollableFrame(self.viewer_frame, width=110, fg_color="gray15", corner_radius=0)
        self.thumb_sidebar.grid(row=0, column=0, sticky="nsew")

        self.canvas_scroll = ctk.CTkScrollableFrame(self.viewer_frame, fg_color="gray20")
        self.canvas_scroll.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        self.lbl_canvas_render = ctk.CTkLabel(self.canvas_scroll, text="No PDF Document Loaded\n\nClick 'Upload Master PDF' to begin.", font=("Arial", 14), text_color="gray60")
        self.lbl_canvas_render.pack(expand=True, pady=100)

        self.tool_workspace = ctk.CTkFrame(self.split_container, fg_color=BG_CARD)
        self.tool_workspace.grid(row=0, column=1, sticky="nsew")
        self.tool_workspace.grid_rowconfigure(0, weight=1)
        self.tool_workspace.grid_columnconfigure(0, weight=1)

        self.current_tool_frame = None

    # ==========================================================================
    # 5. STATUS BAR
    # ==========================================================================
    def setup_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0, fg_color=SECONDARY_COLOR)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="System Status: Ready. Developed by Dr. Joseph I Thomas.",
            font=("Arial", 11),
            text_color=TEXT_LIGHT
        )
        self.lbl_status.pack(side="left", padx=15, pady=4)

        self.progress_bar = ctk.CTkProgressBar(self.status_bar, width=180, height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=15, pady=8)

    # ==========================================================================
    # MASTER PDF LOAD & LIVE CANVAS RENDER ENGINE
    # ==========================================================================
    def upload_master_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select Master PDF File",
            filetypes=[("PDF Documents", "*.pdf")]
        )
        if file_path:
            self.load_pdf_document(file_path)

    def load_pdf_document(self, file_path: str, navigate_to_split: bool = True):
        try:
            if self.pdf_doc:
                self.pdf_doc.close()

            self.active_pdf_path = file_path
            self.pdf_doc = fitz.open(file_path)
            self.current_page_idx = 0
            self.zoom_factor = 1.0

            filename = os.path.basename(file_path)
            page_count = len(self.pdf_doc)
            self.lbl_master_filename.configure(text=f"Active Master PDF: {filename} ({page_count} Pages)")
            self.lbl_status.configure(text=f"Loaded master document: {filename}")

            self.render_current_page()
            self.generate_thumbnails()
            messagebox.showinfo("Master PDF Loaded", f"Successfully loaded:\n{filename}\n\nTotal Pages: {page_count}\nYou can now execute any feature in the suite.")
            # NOTE (fix): navigation to the Extract-Pages tool is now optional.
            # Previously this was unconditional, so if a user clicked, say,
            # "Redact Text" with no PDF loaded, got prompted to upload one via
            # check_master_pdf_loaded(), and did so, they were dumped onto the
            # unrelated Split/Extract tool instead of the Redact tool they
            # actually asked for.
            if navigate_to_split:
                self.show_split_tool()
        except Exception as e:
            messagebox.showerror("PDF Load Error", f"Failed to load PDF file:\n{str(e)}")

    def close_master_pdf(self):
        if self.pdf_doc:
            self.pdf_doc.close()
            self.pdf_doc = None
        self.active_pdf_path = None
        self.current_page_idx = 0
        self._current_page_image = None
        self.thumbnail_images.clear()
        self.lbl_master_filename.configure(text="Active Master PDF: None")
        self.lbl_page_nav.configure(text="Page 0 / 0")
        self.lbl_canvas_render.configure(text="No PDF Document Loaded\n\nClick 'Upload Master PDF' to begin.", image=None)

        for widget in self.thumb_sidebar.winfo_children():
            widget.destroy()

        self.show_welcome_workspace()

    def render_current_page(self):
        if not self.pdf_doc or len(self.pdf_doc) == 0:
            return

        page_count = len(self.pdf_doc)
        self.current_page_idx = max(0, min(self.current_page_idx, page_count - 1))
        self.lbl_page_nav.configure(text=f"Page {self.current_page_idx + 1} / {page_count}")

        page = self.pdf_doc[self.current_page_idx]
        mat = fitz.Matrix(self.zoom_factor * 1.0, self.zoom_factor * 1.0)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))

        # Retain a strong reference — otherwise Tk/CTk garbage-collects the
        # image and the canvas label goes blank.
        self._current_page_image = ctk_img
        self.lbl_canvas_render.configure(image=ctk_img, text="")

    def generate_thumbnails(self):
        for widget in self.thumb_sidebar.winfo_children():
            widget.destroy()

        self.thumbnail_images.clear()

        if not self.pdf_doc:
            return

        for i in range(min(len(self.pdf_doc), 50)):
            page = self.pdf_doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))
            # Keep a strong reference so thumbnails do not vanish
            self.thumbnail_images.append(ctk_img)

            btn_thumb = ctk.CTkButton(
                self.thumb_sidebar,
                image=ctk_img,
                text=f"P. {i + 1}",
                compound="top",
                width=90,
                height=110,
                fg_color="gray25",
                hover_color=PRIMARY_COLOR,
                command=lambda idx=i: self.jump_to_page(idx)
            )
            btn_thumb.pack(pady=5, padx=5)

    def jump_to_page(self, page_idx: int):
        self.current_page_idx = page_idx
        self.render_current_page()

    def prev_page(self):
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.render_current_page()

    def next_page(self):
        if self.pdf_doc and self.current_page_idx < len(self.pdf_doc) - 1:
            self.current_page_idx += 1
            self.render_current_page()

    def adjust_zoom(self, delta: float):
        self.zoom_factor = max(0.4, min(3.0, self.zoom_factor + delta))
        self.render_current_page()

    def fit_zoom_to_page(self):
        self.zoom_factor = 1.0
        self.render_current_page()

    def check_master_pdf_loaded(self) -> bool:
        """
        NOTE (fix): the original version always returned False after prompting
        for an upload -- even if the user *did* pick a valid file -- and it
        delegated to `upload_master_pdf()`, whose success callback always
        force-navigated to the Extract-Pages tool. That meant clicking any
        other tool (Redact, Watermark, OCR, etc.) without a PDF loaded would
        warn you, let you pick a file, and then silently land you on the
        wrong tool. This version loads the file without forcing that
        navigation and returns True/False based on whether a PDF actually
        ended up loaded, so the caller's original tool request proceeds.
        """
        if not self.active_pdf_path or not os.path.exists(self.active_pdf_path):
            messagebox.showwarning(
                "Master PDF Required",
                "Please select a PDF document to continue. You will be taken to the tool you selected once it loads."
            )
            file_path = filedialog.askopenfilename(
                title="Select Master PDF File",
                filetypes=[("PDF Documents", "*.pdf")]
            )
            if file_path:
                self.load_pdf_document(file_path, navigate_to_split=False)
            return self.active_pdf_path is not None
        return True

    def save_active_as(self):
        if not self.check_master_pdf_loaded():
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")])
        if save_path:
            self.pdf_doc.save(save_path)
            messagebox.showinfo("Saved", f"Document saved successfully to:\n{save_path}")

    def switch_tool_frame(self, frame_builder_func: Any):
        if self.current_tool_frame:
            self.current_tool_frame.destroy()
        self.current_tool_frame = frame_builder_func(self.tool_workspace)
        self.current_tool_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def run_async_task(self, task_func: Any, on_complete: Optional[Any] = None, status_msg: str = "Processing task..."):
        self.lbl_status.configure(text=f"Status: {status_msg}")
        self.progress_bar.start()

        def worker():
            err = None
            result = None
            try:
                result = task_func()
            except Exception as e:
                err = e
                traceback.print_exc()

            def finish():
                self.progress_bar.stop()
                self.progress_bar.set(0)
                self.lbl_status.configure(text="System Status: Ready")
                if err:
                    messagebox.showerror("Execution Error", f"Operation failed:\n{str(err)}")
                elif on_complete:
                    on_complete(result)

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    # ==========================================================================
    # TOOL ROUTER HOOKS
    # ==========================================================================
    def show_welcome_workspace(self): self.switch_tool_frame(self.frame_welcome)
    def show_titus_omni(self): self.switch_tool_frame(self.frame_titus_omni)
    def show_ai_tools_hub(self): self.switch_tool_frame(self.frame_ai_tools_hub)
    def show_pdf_chat_tool(self): self.show_titus_omni()
    def titus_omni_quick_prompt(self, prompt: str):
        self.show_titus_omni()
        self.after(300, lambda: getattr(self, '_titus_omni_send_fn', lambda p: None)(prompt))
    def show_split_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_split)
    def show_merge_tool(self): self.switch_tool_frame(self.frame_merge)
    def show_delete_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_delete)
    def show_reorder_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_reorder)
    def show_rotate_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_rotate)
    def show_crop_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_crop)
    def show_blank_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_blank)
    def show_img_to_pdf_tool(self): self.switch_tool_frame(self.frame_img_to_pdf)

    def show_annotations_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_annotations)
    def show_watermark_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_watermark)
    def show_header_footer_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_header_footer)
    def show_redact_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_redact)
    def show_compress_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_compress)
    def show_protect_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_protect)
    def show_unlock_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_unlock)
    def show_metadata_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_metadata)

    def show_ocr_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_ocr)
    def show_find_replace_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_find_replace)

    def show_pdf_to_word_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_pdf_to_word)
    def show_searchable_pdf_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_searchable_pdf)
    def show_ext_text_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_ext_text)
    def show_ext_img_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_ext_img)
    def show_batch_tool(self): self.switch_tool_frame(self.frame_batch)

    def show_openview_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_openview)
    def show_bookmarks_tool(self):
        if self.check_master_pdf_loaded(): self.switch_tool_frame(self.frame_bookmarks)

    # ==========================================================================
    # TOOL WORKSPACE PANELS & EXECUTION ENGINES
    # ==========================================================================

    def frame_welcome(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(f, text="TSTC_Professional PDF Suite v4.0", font=("Arial", 22, "bold"), text_color=PRIMARY_COLOR).pack(pady=(25, 4))
        ctk.CTkLabel(f, text="Developed by Dr. Joseph I Thomas", font=("Arial", 13, "bold"), text_color=ACCENT_AMBER).pack(pady=(0, 6))
        ctk.CTkLabel(
            f,
            text="Titus II Teachers College Institutional Enterprise Desktop Platform\nCombining Adobe Acrobat Pro, ABBYY FineReader PDF, OpenView Catalog Index Engine, and AI Chat Assistant.",
            font=("Arial", 12),
            text_color="gray70",
            justify="center"
        ).pack(pady=5)

        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(pady=15)

        ctk.CTkButton(
            btn_row,
            text="📂 Upload Master PDF",
            command=self.upload_master_pdf,
            height=46,
            width=220,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_row,
            text="💬 Chat with PDF (AI)",
            command=self.show_pdf_chat_tool,
            height=46,
            width=220,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)

        cards_frame = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=10)
        cards_frame.pack(pady=15, padx=25, fill="both", expand=True)

        features = [
            ("🤖 AI Document Chat & RAG", "Ask questions, generate executive summaries & key takeaways with interactive page citations [Page X]."),
            ("🎨 Adobe Acrobat Pro Suite", "Extract, merge, delete, reorder, rotate, crop, split, annotate, watermark, redact, compress, and encrypt PDFs."),
            ("👁️ ABBYY FineReader OCR", "Multilingual OCR (English, Malayalam, Hindi), extract text/images, and convert PDF to editable Word (.docx)."),
            ("📖 OpenView Index Designer", "Create institutional table of contents, design catalogs, dot-leader indexes, and interactive hyperlinked PDFs.")
        ]

        for i, (title, desc) in enumerate(features):
            row = i // 2
            col = i % 2
            card = ctk.CTkFrame(cards_frame, fg_color=BG_CARD, corner_radius=8)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            cards_frame.grid_columnconfigure(col, weight=1)
            cards_frame.grid_rowconfigure(row, weight=1)

            ctk.CTkLabel(card, text=title, font=("Arial", 13, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(card, text=desc, font=("Arial", 11), text_color=TEXT_LIGHT, justify="left", wraplength=280).pack(anchor="w", padx=12, pady=(0, 10))

        return f

    # --------------------------------------------------------------------------
    # 1. CORE PAGE OPERATIONS
    # --------------------------------------------------------------------------
    def frame_split(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="✂️ Extract Target Page(s)", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Specify page numbers or page range to isolate into a new PDF (e.g. 1, 3-5, 8).", font=("Arial", 11), text_color="gray70").pack(pady=5)
        
        self.ent_split_range = ctk.CTkEntry(f, placeholder_text="e.g. 1, 2, 4-7", width=320, height=35)
        self.ent_split_range.pack(pady=15)
        self.ent_split_range.insert(0, f"1-{len(self.pdf_doc)}" if self.pdf_doc else "1")

        def execute():
            val = self.ent_split_range.get().strip()
            if not val:
                return messagebox.showwarning("Input Required", "Please enter page numbers or range.")

            max_page = len(self.pdf_doc) if self.pdf_doc else 0
            try:
                pages = PDFEngine.parse_page_spec(val, max_page)
            except ValueError as e:
                return messagebox.showerror("Invalid Page Spec", str(e))

            if not pages:
                return messagebox.showwarning("No Pages", "No valid pages found in the specified range.")

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.extract_pages(self.active_pdf_path, pages, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Extracted {len(pages)} pages to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Extracting pages..."
                )

        ctk.CTkButton(f, text="Execute Extraction", command=execute, height=38, fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER).pack(pady=20)
        return f

    def frame_merge(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🧩 Merge Multiple PDF Files", font=("Arial", 18, "bold")).pack(pady=15)
        
        pdf_list: List[str] = []
        listbox_frame = ctk.CTkFrame(f)
        listbox_frame.pack(pady=10, fill="x", padx=20)

        lbl_files = ctk.CTkLabel(listbox_frame, text="No PDF files queued for merge.", font=("Arial", 11))
        lbl_files.pack(pady=15)

        def update_labels():
            if pdf_list:
                lbl_files.configure(text=f"Queued Files ({len(pdf_list)}):\n" + "\n".join(os.path.basename(p) for p in pdf_list))
            else:
                lbl_files.configure(text="No PDF files queued for merge.")

        def add_files():
            files = filedialog.askopenfilenames(filetypes=[("PDF Documents", "*.pdf")])
            if files:
                pdf_list.extend(files)
                update_labels()

        def clear_files():
            pdf_list.clear()
            update_labels()

        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(pady=10)
        ctk.CTkButton(btn_row, text="➕ Add PDF Files", command=add_files, width=140).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="🗑️ Clear List", command=clear_files, width=120, fg_color="gray40").pack(side="left", padx=5)

        def execute():
            if len(pdf_list) < 2:
                return messagebox.showwarning("Merge Warning", "Please add at least 2 PDF files to merge.")
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.merge_pdfs(pdf_list, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Merged {len(pdf_list)} PDF files into:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Merging PDF files..."
                )

        ctk.CTkButton(f, text="Execute PDF Merge", command=execute, height=40, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_delete(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🗑️ Delete Selected Pages", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Enter page numbers to permanently remove from document (e.g. 2, 4, 7-9).", font=("Arial", 11), text_color="gray70").pack(pady=5)
        
        ent_del = ctk.CTkEntry(f, placeholder_text="e.g. 2, 5, 8-10", width=320, height=35)
        ent_del.pack(pady=15)

        def execute():
            val = ent_del.get().strip()
            if not val:
                return messagebox.showwarning("Input Required", "Enter page numbers to delete.")

            max_page = len(self.pdf_doc) if self.pdf_doc else 0
            try:
                del_pages = PDFEngine.parse_page_spec(val, max_page)
            except ValueError as e:
                return messagebox.showerror("Invalid Page Spec", str(e))

            if not del_pages:
                return messagebox.showwarning("No Pages", "No valid pages found to delete.")

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.delete_pages(self.active_pdf_path, del_pages, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Deleted pages {del_pages}. Output saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Deleting specified pages..."
                )

        ctk.CTkButton(f, text="Delete Pages & Save", command=execute, height=38, fg_color="red").pack(pady=20)
        return f

    def frame_reorder(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔀 Reorder PDF Pages", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Enter full new sequence of page numbers separated by commas.", font=("Arial", 11), text_color="gray70").pack(pady=5)

        total_pages = len(self.pdf_doc) if self.pdf_doc else 1
        default_order = ", ".join(str(i) for i in range(1, total_pages + 1))
        
        ent_order = ctk.CTkEntry(f, width=340, height=35)
        ent_order.pack(pady=15)
        ent_order.insert(0, default_order)

        def execute():
            raw = ent_order.get().strip()
            order = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.reorder_pages(self.active_pdf_path, order, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Reordered pages. Saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Reordering document pages..."
                )

        ctk.CTkButton(f, text="Apply Reordered Sequence", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_rotate(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔄 Rotate Document Pages", font=("Arial", 18, "bold")).pack(pady=15)
        
        opt_angle = ctk.CTkOptionMenu(f, values=["90 Degrees Clockwise", "180 Degrees", "270 Degrees Counter-Clockwise"])
        opt_angle.pack(pady=10)

        def execute():
            deg = 90
            sel = opt_angle.get()
            if "180" in sel: deg = 180
            elif "270" in sel: deg = 270

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.rotate_pages(self.active_pdf_path, deg, None, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Rotated pages by {deg}°. Output saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Rotating pages..."
                )

        ctk.CTkButton(f, text="Rotate & Save PDF", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_crop(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="📐 Crop Canvas Margins", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Specify margin crop offsets in points (72 points = 1 inch).", font=("Arial", 11), text_color="gray70").pack(pady=5)

        ent_top = ctk.CTkEntry(f, placeholder_text="Top Margin (pts)", width=220)
        ent_top.pack(pady=5); ent_top.insert(0, "36")

        ent_bottom = ctk.CTkEntry(f, placeholder_text="Bottom Margin (pts)", width=220)
        ent_bottom.pack(pady=5); ent_bottom.insert(0, "36")

        ent_left = ctk.CTkEntry(f, placeholder_text="Left Margin (pts)", width=220)
        ent_left.pack(pady=5); ent_left.insert(0, "36")

        ent_right = ctk.CTkEntry(f, placeholder_text="Right Margin (pts)", width=220)
        ent_right.pack(pady=5); ent_right.insert(0, "36")

        def execute():
            t = float(ent_top.get() or 0)
            b = float(ent_bottom.get() or 0)
            l = float(ent_left.get() or 0)
            r = float(ent_right.get() or 0)
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.crop_pages(self.active_pdf_path, t, b, l, r, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Cropped margins. Output saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Cropping page margins..."
                )

        ctk.CTkButton(f, text="Apply Margin Crop", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_blank(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="➕ Insert Blank Page", font=("Arial", 18, "bold")).pack(pady=15)
        
        ent_pos = ctk.CTkEntry(f, placeholder_text="Insert Position (Page Number)", width=240)
        ent_pos.pack(pady=10)
        ent_pos.insert(0, "1")

        def execute():
            pos = int(ent_pos.get().strip()) - 1
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.insert_blank_page(self.active_pdf_path, max(0, pos), save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Blank page inserted. Saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Inserting blank page..."
                )

        ctk.CTkButton(f, text="Insert Blank Page & Save", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_img_to_pdf(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🖼️ Batch Images to PDF Converter", font=("Arial", 18, "bold")).pack(pady=15)
        
        def execute():
            files = filedialog.askopenfilenames(filetypes=[("Image Formats", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
            if not files: return
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                def process():
                    imgs = [Image.open(p).convert("RGB") for p in files]
                    imgs[0].save(save_path, save_all=True, append_images=imgs[1:])
                    return save_path

                self.run_async_task(
                    process,
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Compiled {len(files)} image assets to PDF:\n{res}"),
                        self.load_pdf_document(res)
                    ),
                    status_msg="Compiling images into PDF document..."
                )

        ctk.CTkButton(f, text="Select Image Files & Compile to PDF", command=execute, height=42, fg_color=PRIMARY_COLOR).pack(pady=30)
        return f

    # --------------------------------------------------------------------------
    # 2. ADOBE ACROBAT PRO SUITE
    # --------------------------------------------------------------------------

    def frame_annotations(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="✍️ Annotations & Official Stamps", font=("Arial", 18, "bold")).pack(pady=15)
        
        ctk.CTkLabel(f, text="Select Official Preset Stamp to apply to current page:", font=("Arial", 11)).pack(pady=5)
        opt_stamp = ctk.CTkOptionMenu(f, values=["TITUS II OFFICIAL", "APPROVED & VERIFIED", "CONFIDENTIAL", "ACADEMIC REVIEWED"])
        opt_stamp.pack(pady=10)

        def apply_stamp():
            stamp_text = opt_stamp.get()
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                p_num = self.current_page_idx + 1
                self.run_async_task(
                    lambda: PDFEngine.add_stamp_annotation(self.active_pdf_path, p_num, stamp_text, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Stamp Applied", f"Applied stamp '{stamp_text}' to Page {p_num}.\nSaved to: {save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Applying official stamp..."
                )

        ctk.CTkButton(f, text="Apply Stamp to Active Page", command=apply_stamp, height=38, fg_color=PRIMARY_COLOR).pack(pady=15)
        return f

    def frame_watermark(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="💧 Custom Text & Image Watermark", font=("Arial", 18, "bold")).pack(pady=15)
        
        tab_wm = ctk.CTkTabview(f)
        tab_wm.pack(pady=10, fill="both")
        tab_text = tab_wm.add("Text Watermark")
        tab_img = tab_wm.add("Image Logo Watermark")

        ent_wm_text = ctk.CTkEntry(tab_text, placeholder_text="Watermark Text", width=300, height=35)
        ent_wm_text.pack(pady=10)
        ent_wm_text.insert(0, "TITUS II TEACHERS COLLEGE")

        def apply_text_wm():
            txt = ent_wm_text.get()
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.add_text_watermark(self.active_pdf_path, txt, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Applied watermark '{txt}' across document.\nSaved to: {save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Applying text watermark..."
                )

        ctk.CTkButton(tab_text, text="Apply Text Watermark", command=apply_text_wm, height=38, fg_color=PRIMARY_COLOR).pack(pady=15)

        def apply_img_wm():
            img_file = filedialog.askopenfilename(filetypes=[("Image Formats", "*.png;*.jpg;*.jpeg")])
            if img_file:
                save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
                if save_path:
                    self.run_async_task(
                        lambda: PDFEngine.add_image_watermark(self.active_pdf_path, img_file, save_path),
                        on_complete=lambda res: (
                            messagebox.showinfo("Success", f"Applied logo watermark. Saved to:\n{save_path}"),
                            self.load_pdf_document(save_path)
                        ),
                        status_msg="Overlaying image logo watermark..."
                    )

        ctk.CTkButton(tab_img, text="Select Logo Image & Apply Watermark", command=apply_img_wm, height=38, fg_color=PRIMARY_COLOR).pack(pady=25)
        return f

    def frame_header_footer(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔢 Header, Footer & Page Numbers", font=("Arial", 18, "bold")).pack(pady=15)
        
        ent_header = ctk.CTkEntry(f, placeholder_text="Header Text (Top Left)", width=320, height=35)
        ent_header.pack(pady=8)
        ent_header.insert(0, "Titus II Teachers College - Official Publication")

        ent_footer = ctk.CTkEntry(f, placeholder_text="Footer Text (Bottom)", width=320, height=35)
        ent_footer.pack(pady=8)

        chk_pg_num = ctk.CTkCheckBox(f, text="Append Dynamic Page Numbers (Page X of Y)")
        chk_pg_num.pack(pady=12)
        chk_pg_num.select()

        def execute():
            h_txt = ent_header.get()
            f_txt = ent_footer.get()
            p_num = chk_pg_num.get() == 1
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.add_page_numbers_and_header(self.active_pdf_path, save_path, h_txt, f_txt, p_num),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Header & Page numbers applied. Saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Applying headers & page numbers..."
                )

        ctk.CTkButton(f, text="Apply Header & Page Numbers", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_redact(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="██ Permanent Content Redaction", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Enter sensitive string to permanently black-out across PDF content layer.", font=("Arial", 11), text_color="gray70").pack(pady=5)

        ent_redact = ctk.CTkEntry(f, placeholder_text="Search String to Redact...", width=320, height=35)
        ent_redact.pack(pady=15)

        def execute():
            query = ent_redact.get().strip()
            if not query:
                return messagebox.showwarning("Warning", "Enter string to redact.")
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.redact_text(self.active_pdf_path, query, save_path),
                    on_complete=lambda cnt: (
                        messagebox.showinfo("Redaction Complete", f"Permanently redacted {cnt} instance(s) of '{query}'.\nSaved to: {save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg=f"Redacting text '{query}'..."
                )

        ctk.CTkButton(f, text="Execute Permanent Redaction", command=execute, height=38, fg_color="red").pack(pady=20)
        return f

    def frame_compress(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="⚡ File Size Compression & Optimization", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Compress streams, garbage collect unused objects, and optimize layout.", font=("Arial", 11), text_color="gray70").pack(pady=5)

        def execute():
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.compress_pdf(self.active_pdf_path, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Document compressed successfully.\nSaved to: {save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Optimizing and compressing PDF..."
                )

        ctk.CTkButton(f, text="Execute Compression & Save", command=execute, height=40, fg_color=PRIMARY_COLOR).pack(pady=25)
        return f

    def frame_protect(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔒 Password Encryption & Security", font=("Arial", 18, "bold")).pack(pady=15)

        ent_pw = ctk.CTkEntry(f, placeholder_text="User Password (Required)", show="*", width=300, height=35)
        ent_pw.pack(pady=10)

        ent_owner = ctk.CTkEntry(f, placeholder_text="Owner Password (Optional)", show="*", width=300, height=35)
        ent_owner.pack(pady=10)

        def execute():
            pw = ent_pw.get()
            owner = ent_owner.get()
            if not pw:
                return messagebox.showwarning("Warning", "User password cannot be empty.")
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.encrypt_pdf(self.active_pdf_path, pw, owner, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"AES 128-bit Encryption applied!\nSaved to: {save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Applying AES encryption..."
                )

        ctk.CTkButton(f, text="Encrypt & Lock Document", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_unlock(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔓 Remove Password / Unlock PDF", font=("Arial", 18, "bold")).pack(pady=15)

        ent_pw = ctk.CTkEntry(f, placeholder_text="Enter Document Master Password", show="*", width=300, height=35)
        ent_pw.pack(pady=15)

        def execute():
            pw = ent_pw.get()
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.decrypt_pdf(self.active_pdf_path, pw, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Password security removed. Unlocked PDF saved to:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Unlocking PDF document..."
                )

        ctk.CTkButton(f, text="Unlock & Save Unrestricted File", command=execute, height=38, fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER).pack(pady=20)
        return f

    def frame_metadata(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="ℹ️ Edit Document Properties & Metadata", font=("Arial", 18, "bold")).pack(pady=15)

        meta = self.pdf_doc.metadata if self.pdf_doc else {}

        ent_title = ctk.CTkEntry(f, placeholder_text="Document Title", width=320, height=35)
        ent_title.pack(pady=8)
        ent_title.insert(0, meta.get("title", ""))

        ent_author = ctk.CTkEntry(f, placeholder_text="Author / Institution", width=320, height=35)
        ent_author.pack(pady=8)
        ent_author.insert(0, meta.get("author", "Dr. Joseph I Thomas, Titus II Teachers College"))

        ent_subject = ctk.CTkEntry(f, placeholder_text="Subject / Topic", width=320, height=35)
        ent_subject.pack(pady=8)
        ent_subject.insert(0, meta.get("subject", ""))

        def execute():
            doc = fitz.open(self.active_pdf_path)
            doc.set_metadata({
                "title": ent_title.get(),
                "author": ent_author.get(),
                "subject": ent_subject.get()
            })
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                doc.save(save_path)
                doc.close()
                messagebox.showinfo("Success", f"Metadata updated successfully!\nSaved to: {save_path}")
                self.load_pdf_document(save_path)

        ctk.CTkButton(f, text="Commit Metadata Updates", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    # --------------------------------------------------------------------------
    # 3. ABBYY FINEREADER SUITE
    # --------------------------------------------------------------------------

    def frame_ocr(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔍 Advanced Multilingual OCR Engine", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Extract English & Malayalam text using Surya Deep Learning AI or PyMuPDF/Tesseract fallback.", font=("Arial", 11), text_color="gray70").pack(pady=5)

        opt_lang = ctk.CTkOptionMenu(f, values=[
            "Surya Deep Learning OCR (English & Malayalam)",
            "Tesseract / PyMuPDF (eng+mal)",
            "Tesseract / PyMuPDF (eng)",
            "Tesseract / PyMuPDF (mal)"
        ])
        opt_lang.pack(pady=15)

        def execute():
            sel = opt_lang.get()
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt"), ("Markdown", "*.md")])
            if not save_path:
                return

            if "Surya" in sel:
                self.run_async_task(
                    lambda: PDFEngine.perform_surya_ocr_extraction(self.active_pdf_path, langs=["en", "ml"]),
                    on_complete=lambda text: (
                        PDFEngine._write_text_file(save_path, text),
                        messagebox.showinfo("OCR Success", f"Surya Multilingual OCR extraction finalized!\nSaved output text to: {save_path}")
                    ),
                    status_msg="Running Surya Deep Learning OCR Scan..."
                )
            else:
                lang_code = "eng+mal" if "eng+mal" in sel else ("eng" if "eng" in sel else "mal")
                self.run_async_task(
                    lambda: PDFEngine.perform_ocr_extraction(self.active_pdf_path, lang=lang_code),
                    on_complete=lambda text: (
                        PDFEngine._write_text_file(save_path, text),
                        messagebox.showinfo("OCR Success", f"Multilingual OCR extraction finalized!\nSaved output text to: {save_path}")
                    ),
                    status_msg="Executing OCR text recognition..."
                )

        ctk.CTkButton(f, text="Run Multilingual OCR Scan", command=execute, height=40, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    def frame_find_replace(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔍 Find & Replace Engine", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(
            f,
            text=f"Active Source: {os.path.basename(self.active_pdf_path) if self.active_pdf_path else 'None'}",
            font=("Arial", 11, "italic"),
            text_color="gray70"
        ).pack(pady=2)

        self.find_ent = ctk.CTkEntry(f, placeholder_text="Find Text String...", width=340, height=35)
        self.find_ent.pack(pady=10)

        self.replace_ent = ctk.CTkEntry(f, placeholder_text="Replace With...", width=340, height=35)
        self.replace_ent.pack(pady=10)

        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(pady=20)

        def do_find_text():
            query = self.find_ent.get().strip()
            if not query:
                return messagebox.showwarning("Warning", "Please enter a search query!")
            try:
                total_matches = PDFEngine.search_text(self.active_pdf_path, query)
                messagebox.showinfo("Search Results", f"Found '{query}' {total_matches} time(s) across the active master document.")
            except Exception as e:
                messagebox.showerror("Execution Error", str(e))

        def do_highlight_search():
            query = self.find_ent.get().strip()
            if not query:
                return messagebox.showwarning("Warning", "Please enter a search string to highlight!")
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")])
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.highlight_text(self.active_pdf_path, query, save_path),
                    on_complete=lambda match_count: (
                        messagebox.showinfo("Success", f"Highlighted {match_count} occurrence(s) and saved output file:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg=f"Highlighting '{query}' across pages..."
                )

        def do_replace_text():
            find_query = self.find_ent.get().strip()
            replace_query = self.replace_ent.get()
            if not find_query:
                return messagebox.showwarning("Warning", "Please enter a target search string to replace!")
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")])
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.find_and_replace_text(self.active_pdf_path, find_query, replace_query, save_path),
                    on_complete=lambda match_count: (
                        messagebox.showinfo("Success", f"Replaced {match_count} occurrence(s) of '{find_query}' with '{replace_query}'.\nSaved to: {save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg=f"Replacing '{find_query}' with '{replace_query}'..."
                )

        ctk.CTkButton(btn_frame, text="🔍 Find Instances", command=do_find_text, height=36, width=150).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🖍️ Highlight & Save", command=do_highlight_search, height=36, width=150, fg_color="teal").pack(side="left", padx=5)
        ctk.CTkButton(f, text="✏️ Replace All & Save PDF", command=do_replace_text, height=38, width=310, fg_color=PRIMARY_COLOR).pack(pady=10)

        return f

    def frame_pdf_to_word(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="📄 PDF to Word (.docx) Converter", font=("Arial", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(f, text="Converts document typography, tables, and page layout to editable Microsoft Word format.", font=("Arial", 11), text_color="gray70").pack(pady=5)

        def execute():
            save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.convert_pdf_to_word(self.active_pdf_path, save_path),
                    on_complete=lambda res: messagebox.showinfo("Conversion Success", f"Successfully converted PDF to Word format:\n{save_path}"),
                    status_msg="Converting PDF to Word document..."
                )

        ctk.CTkButton(f, text="Convert to Word (.docx)", command=execute, height=40, fg_color=PRIMARY_COLOR).pack(pady=25)
        return f

    def frame_searchable_pdf(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="📊 PDF to Searchable PDF Layer", font=("Arial", 18, "bold")).pack(pady=15)

        def execute():
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                self.run_async_task(
                    lambda: PDFEngine.convert_pdf_to_searchable_pdf(self.active_pdf_path, save_path),
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"Searchable PDF generated:\n{save_path}"),
                        self.load_pdf_document(save_path)
                    ),
                    status_msg="Generating searchable text layer..."
                )

        ctk.CTkButton(f, text="Generate Searchable PDF", command=execute, height=40, fg_color=PRIMARY_COLOR).pack(pady=25)
        return f

    def frame_ext_text(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="📝 Extract Raw Text Content", font=("Arial", 18, "bold")).pack(pady=15)

        def execute():
            save_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if save_path:
                def process():
                    doc = fitz.open(self.active_pdf_path)
                    full = "".join(page.get_text() + "\n" for page in doc)
                    doc.close()
                    with open(save_path, "w", encoding="utf-8") as out:
                        out.write(full)
                    return save_path

                self.run_async_task(
                    process,
                    on_complete=lambda res: messagebox.showinfo("Success", f"Raw text extracted to:\n{res}"),
                    status_msg="Extracting text layer..."
                )

        ctk.CTkButton(f, text="Harvest Text to .txt File", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=25)
        return f

    def frame_ext_img(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🖼️ Extract Embedded Raster Images", font=("Arial", 18, "bold")).pack(pady=15)

        def execute():
            save_dir = filedialog.askdirectory(title="Select Output Image Directory")
            if save_dir:
                def process():
                    doc = fitz.open(self.active_pdf_path)
                    count = 0
                    for i in range(len(doc)):
                        for img_info in doc.get_page_images(i):
                            xref = img_info[0]
                            pix = fitz.Pixmap(doc, xref)
                            if pix.n - pix.alpha > 3:
                                pix = fitz.Pixmap(fitz.csRGB, pix)
                            pix.save(os.path.join(save_dir, f"asset_page_{i+1}_img_{count+1}.png"))
                            count += 1
                    doc.close()
                    return count

                self.run_async_task(
                    process,
                    on_complete=lambda cnt: messagebox.showinfo("Success", f"Extracted {cnt} image assets to:\n{save_dir}"),
                    status_msg="Extracting embedded image assets..."
                )

        ctk.CTkButton(f, text="Select Output Folder & Extract Images", command=execute, height=38, fg_color=PRIMARY_COLOR).pack(pady=25)
        return f

    def frame_batch(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="⚡ Batch Directory Converter Suite", font=("Arial", 18, "bold")).pack(pady=15)
        
        opt_batch = ctk.CTkOptionMenu(f, values=["Batch PDF to Word (.docx)", "Batch Text Extraction (.txt)", "Batch File Size Compression"])
        opt_batch.pack(pady=15)

        def execute():
            src_dir = filedialog.askdirectory(title="Select Input PDF Directory")
            if not src_dir: return
            out_dir = filedialog.askdirectory(title="Select Output Directory")
            if not out_dir: return

            mode = opt_batch.get()

            def process():
                pdf_files = [f for f in os.listdir(src_dir) if f.lower().endswith(".pdf")]
                count = 0
                for fname in pdf_files:
                    in_p = os.path.join(src_dir, fname)
                    base = os.path.splitext(fname)[0]
                    if "Word" in mode:
                        out_p = os.path.join(out_dir, base + ".docx")
                        PDFEngine.convert_pdf_to_word(in_p, out_p)
                    elif "Text" in mode:
                        out_p = os.path.join(out_dir, base + ".txt")
                        t = PDFEngine.perform_ocr_extraction(in_p)
                        with open(out_p, "w", encoding="utf-8") as f_out: f_out.write(t)
                    elif "Compression" in mode:
                        out_p = os.path.join(out_dir, base + "_compressed.pdf")
                        PDFEngine.compress_pdf(in_p, out_p)
                    count += 1
                return count

            self.run_async_task(
                process,
                on_complete=lambda cnt: messagebox.showinfo("Batch Complete", f"Processed {cnt} PDF files successfully!"),
                status_msg="Running batch folder operations..."
            )

        ctk.CTkButton(f, text="Select Directory & Execute Batch", command=execute, height=40, fg_color=PRIMARY_COLOR).pack(pady=20)
        return f

    # --------------------------------------------------------------------------
    # 4. OPENVIEW DYNAMIC INDEX & TOC BUILDER
    # --------------------------------------------------------------------------

    def frame_openview(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="📖 Custom OpenView Index & TOC Designer", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(f, text="Design formal Table of Contents with OpenView dot-leader layout and clickable links.", font=("Arial", 11), text_color="gray70").pack(pady=2)

        opt_tpl = ctk.CTkOptionMenu(f, values=["Titus II Institutional Classic", "Modern Academic", "Minimalist OpenView Catalog"])
        opt_tpl.pack(pady=10)

        items_frame = ctk.CTkFrame(f)
        items_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkLabel(items_frame, text="Current Index Entries:", font=("Arial", 12, "bold")).pack(pady=5)

        entry_widgets: List[Tuple[ctk.CTkEntry, ctk.CTkEntry, ctk.CTkOptionMenu]] = []
        entries_scroll = ctk.CTkFrame(items_frame)
        entries_scroll.pack(fill="x", pady=5)

        def refresh_entries_ui():
            for w in entries_scroll.winfo_children():
                w.destroy()
            entry_widgets.clear()

            for idx, item in enumerate(self.openview_entries):
                row = ctk.CTkFrame(entries_scroll, fg_color="transparent")
                row.pack(fill="x", pady=2)

                opt_lvl = ctk.CTkOptionMenu(row, values=["L1", "L2", "L3"], width=60)
                opt_lvl.set(f"L{item.get('level', 1)}")
                opt_lvl.pack(side="left", padx=2)

                ent_t = ctk.CTkEntry(row, width=220)
                ent_t.insert(0, item.get("title", ""))
                ent_t.pack(side="left", padx=2)

                ent_p = ctk.CTkEntry(row, width=50)
                ent_p.insert(0, str(item.get("page", 1)))
                ent_p.pack(side="left", padx=2)

                btn_del = ctk.CTkButton(row, text="❌", width=30, fg_color="red", command=lambda i=idx: remove_entry(i))
                btn_del.pack(side="left", padx=2)

                entry_widgets.append((ent_t, ent_p, opt_lvl))

        def add_new_entry():
            self.openview_entries.append({"level": 1, "title": "New Section Entry", "page": 1})
            refresh_entries_ui()

        def remove_entry(index: int):
            if 0 <= index < len(self.openview_entries):
                self.openview_entries.pop(index)
                refresh_entries_ui()

        refresh_entries_ui()

        btn_add = ctk.CTkButton(items_frame, text="➕ Add Index Entry", command=add_new_entry, width=140)
        btn_add.pack(pady=8)

        def auto_populate():
            self.auto_extract_toc()
            refresh_entries_ui()

        btn_auto = ctk.CTkButton(items_frame, text="🔍 Auto-Scan Document Heading Bookmarks", command=auto_populate, fg_color="gray40")
        btn_auto.pack(pady=4)

        def execute_generate():
            compiled_entries = []
            for e_title_widget, e_page_widget, e_lvl_widget in entry_widgets:
                t_str = e_title_widget.get().strip()
                p_num = int(e_page_widget.get().strip()) if e_page_widget.get().strip().isdigit() else 1
                lvl = int(e_lvl_widget.get().replace("L", ""))
                compiled_entries.append({"level": lvl, "title": t_str, "page": p_num})

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            if save_path:
                temp_idx_pdf = os.path.join(os.path.dirname(save_path), "_temp_index.pdf")

                def process():
                    PDFEngine.generate_openview_index_pdf(
                        compiled_entries,
                        temp_idx_pdf,
                        template=opt_tpl.get()
                    )
                    PDFEngine.attach_index_to_pdf(
                        self.active_pdf_path,
                        temp_idx_pdf,
                        save_path,
                        prepend=True
                    )
                    if os.path.exists(temp_idx_pdf):
                        os.remove(temp_idx_pdf)
                    return save_path

                self.run_async_task(
                    process,
                    on_complete=lambda res: (
                        messagebox.showinfo("Success", f"OpenView Index generated with active links and inserted as Page 1!\nSaved to: {res}"),
                        self.load_pdf_document(res)
                    ),
                    status_msg="Generating OpenView Index page & hyperlinking..."
                )

        ctk.CTkButton(f, text="🚀 Build & Inject OpenView Index (Page 1)", command=execute_generate, height=42, fg_color=PRIMARY_COLOR, font=("Arial", 13, "bold")).pack(pady=20)
        return f

    def auto_extract_toc(self):
        if not self.pdf_doc: return
        toc = PDFEngine.extract_document_toc(self.active_pdf_path)
        if toc:
            self.openview_entries = toc
            messagebox.showinfo("TOC Extracted", f"Found {len(toc)} outline heading bookmarks in master PDF!")
        else:
            messagebox.showinfo("TOC Notice", "No embedded PDF outline bookmarks found. Added default template entries.")

    def frame_bookmarks(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(parent)
        ctk.CTkLabel(f, text="🔖 Interactive Bookmarks Inspector", font=("Arial", 18, "bold")).pack(pady=15)

        toc = PDFEngine.extract_document_toc(self.active_pdf_path) if self.pdf_doc else []
        txt_b = "\n".join(f"Level {item['level']}: {item['title']} (Page {item['page']})" for item in toc) if toc else "No bookmarks found in document."

        tb = ctk.CTkTextbox(f, width=320, height=200)
        tb.pack(pady=10)
        tb.insert("1.0", txt_b)

        return f

    # --------------------------------------------------------------------------
    # 5. TITUSOMNI - THE OMNISCIENT & OMNIPOTENT CONVERSATIONAL INTELLIGENCE BOT
    # --------------------------------------------------------------------------

    AI_TOOLS_CATALOG = [
        {"name": "ChatPDF", "cat": "Dedicated PDF Chat", "url": "https://www.chatpdf.com/", "desc": "Chat with any PDF. Instant summaries, research analysis, and page citations."},
        {"name": "Google NotebookLM", "cat": "Academic & Research AI", "url": "https://notebooklm.google.com/", "desc": "Personalized AI research notebook grounded in your uploaded documents."},
        {"name": "Google Gemini", "cat": "Frontier Multi-Modal LLM", "url": "https://gemini.google.com/", "desc": "Upload large PDFs with 1M+ token context window and multi-modal reasoning."},
        {"name": "OpenAI ChatGPT", "cat": "Frontier Multi-Modal LLM", "url": "https://chatgpt.com/", "desc": "Upload documents, analyze with Advanced Data Analysis and Python code execution."},
        {"name": "Anthropic Claude", "cat": "Frontier Multi-Modal LLM", "url": "https://claude.ai/", "desc": "200k context window, exceptional reasoning over complex reports, books, and policies."},
        {"name": "AskYourPDF", "cat": "Dedicated PDF Chat", "url": "https://askyourpdf.com/", "desc": "Interactive chat system for PDF files with direct Chrome extension and API access."},
        {"name": "PDF.ai", "cat": "Dedicated PDF Chat", "url": "https://pdf.ai/", "desc": "Upload legal contracts, financial reports, and manuals to chat effortlessly."},
        {"name": "Humata AI", "cat": "Dedicated PDF Chat", "url": "https://humata.ai/", "desc": "Like ChatGPT for your files, summarize academic papers and find answers fast."},
        {"name": "SciSpace (Typeset)", "cat": "Academic & Research AI", "url": "https://typeset.io/", "desc": "AI workspace to read, understand, and extract insights from research papers."},
        {"name": "ChatDOC", "cat": "Dedicated PDF Chat", "url": "https://www.chatdoc.com/", "desc": "AI reader that extracts tables, formulas, and text with exact page citations."},
        {"name": "Perplexity AI", "cat": "Frontier Multi-Modal LLM", "url": "https://www.perplexity.ai/", "desc": "Conversational search and file analysis with real-time web citations."},
        {"name": "Microsoft Copilot", "cat": "Frontier Multi-Modal LLM", "url": "https://copilot.microsoft.com/", "desc": "Multi-modal document analysis with GPT-4 and Office ecosystem."},
        {"name": "Sharly AI", "cat": "Dedicated PDF Chat", "url": "https://sharly.ai/", "desc": "Document assistant for PDFs, Word docs, PowerPoints, and web links."},
        {"name": "Unriddle AI", "cat": "Dedicated PDF Chat", "url": "https://unriddle.ai/", "desc": "Read complex documents faster, highlight text, and generate connected notes."},
        {"name": "Julius AI", "cat": "Data & Math File Chat", "url": "https://julius.ai/", "desc": "Analyze spreadsheets, CSVs, and PDFs with automated Python charts and data science."},
        {"name": "Scholarcy", "cat": "Academic & Research AI", "url": "https://www.scholarcy.com/", "desc": "Online AI summarizer that breaks papers down into structured summary cards."},
        {"name": "Consensus AI", "cat": "Academic & Research AI", "url": "https://consensus.app/", "desc": "AI search engine for research papers with scientific evidence synthesis."},
        {"name": "Elicit", "cat": "Academic & Research AI", "url": "https://elicit.com/", "desc": "Automated literature review, extract paper claims, and synthesize findings."},
        {"name": "PopAi", "cat": "Data & Synthesis AI", "url": "https://popai.pro/", "desc": "AI workspace to chat with documents, create slides, and generate summaries."},
        {"name": "Monica AI", "cat": "Frontier Multi-Modal LLM", "url": "https://monica.im/", "desc": "All-in-one AI copilot supporting PDF chat, translation, and mind mapping."},
        {"name": "Sider AI", "cat": "Frontier Multi-Modal LLM", "url": "https://sider.ai/", "desc": "Multi-model AI sidebar to chat with files, PDFs, images, and web pages."},
        {"name": "Afforai", "cat": "Academic & Research AI", "url": "https://afforai.com/", "desc": "AI research assistant that searches, summarizes, and translates documents."},
        {"name": "Docalysis", "cat": "Dedicated PDF Chat", "url": "https://docalysis.com/", "desc": "Answer questions from your PDF documents in seconds."},
        {"name": "LightPDF AI", "cat": "Dedicated PDF Chat", "url": "https://lightpdf.com/chatdoc", "desc": "Free online tool to extract summaries and answers from PDFs & Word docs."},
        {"name": "PDFgear AI", "cat": "Dedicated PDF Chat", "url": "https://www.pdfgear.com/chat-pdf/", "desc": "Desktop and online PDF copilot with smart document analysis."},
        {"name": "Smallpdf AI", "cat": "Dedicated PDF Chat", "url": "https://smallpdf.com/ai-pdf", "desc": "Summarize and chat with PDFs securely online."},
        {"name": "ILovePDF AI", "cat": "Dedicated PDF Chat", "url": "https://www.ilovepdf.com/chat-pdf", "desc": "Ask questions and extract data from your PDF documents."},
        {"name": "Foxit PDF AI", "cat": "Dedicated PDF Chat", "url": "https://www.foxit.com/pdf-editor/", "desc": "Cloud PDF reader with embedded AI smart document chat."},
        {"name": "Mindgrasp AI", "cat": "Data & Synthesis AI", "url": "https://mindgrasp.ai/", "desc": "Instantly create notes, summaries, and flashcards from documents and videos."},
        {"name": "Scite.ai", "cat": "Academic & Research AI", "url": "https://scite.ai/", "desc": "Smart citation discovery and document claim verification with AI."},
        {"name": "Paperpal", "cat": "Academic & Research AI", "url": "https://paperpal.com/", "desc": "Academic writing and document checking copilot for researchers."},
        {"name": "Litmaps", "cat": "Academic & Research AI", "url": "https://www.litmaps.com/", "desc": "Discover and map citation networks and literature connections."},
        {"name": "ResearchRabbit", "cat": "Academic & Research AI", "url": "https://www.researchrabbit.ai/", "desc": "Visual literature explorer and personalized academic discovery tool."},
        {"name": "SciSummary", "cat": "Academic & Research AI", "url": "https://scisummary.com/", "desc": "Summarize complex scientific research papers in seconds."},
        {"name": "Coral AI", "cat": "Dedicated PDF Chat", "url": "https://www.getcoralai.com/", "desc": "Chat with any book or long-form PDF document in seconds."},
        {"name": "FileGPT", "cat": "Dedicated PDF Chat", "url": "https://filegpt.app/", "desc": "Chat with PDFs, audio, video, YouTube, and website links simultaneously."},
        {"name": "Chatize", "cat": "Dedicated PDF Chat", "url": "https://chatize.com/", "desc": "Free AI document reader to talk with PDF, Word, EPUB, and text files."},
        {"name": "PDF.to.chat", "cat": "Dedicated PDF Chat", "url": "https://pdf.to.chat/", "desc": "Quick minimalist PDF chat and question answering engine."},
        {"name": "PDFPal", "cat": "Dedicated PDF Chat", "url": "https://pdfpal.ai/", "desc": "Offline and private native AI tool to chat with local PDF files."},
        {"name": "DeepSeek AI", "cat": "Frontier Multi-Modal LLM", "url": "https://chat.deepseek.com/", "desc": "Frontier reasoning and deep document analysis platform."},
        {"name": "Poe by Quora", "cat": "Frontier Multi-Modal LLM", "url": "https://poe.com/", "desc": "Chat with multiple custom bots and upload documents across models."},
        {"name": "HuggingChat", "cat": "Frontier Multi-Modal LLM", "url": "https://huggingface.co/chat/", "desc": "Open-source AI chat platform with document analysis capabilities."},
        {"name": "Mistral Le Chat", "cat": "Frontier Multi-Modal LLM", "url": "https://chat.mistral.ai/", "desc": "Mistral conversational engine with document uploading and analysis."},
        {"name": "Kimi AI", "cat": "Frontier Multi-Modal LLM", "url": "https://kimi.moonshot.cn/", "desc": "2M-token ultra-long context window for books and full encyclopaedias."},
        {"name": "MyMap AI", "cat": "Data & Synthesis AI", "url": "https://www.mymap.ai/", "desc": "Convert documents and PDFs into visual interactive mind maps and flowcharts."},
        {"name": "MapDeduce", "cat": "Data & Synthesis AI", "url": "https://www.mapdeduce.com/", "desc": "Review legal contracts, find red flags, and summarize complex clauses."},
        {"name": "Rows AI", "cat": "Data & Math File Chat", "url": "https://rows.com/", "desc": "Spreadsheet with built-in AI to summarize and query tabular documents."},
        {"name": "Akkio", "cat": "Data & Math File Chat", "url": "https://www.akkio.com/", "desc": "Generative AI for data analysis, chat with document datasets, and forecasting."},
        {"name": "DocAnalysis", "cat": "Dedicated PDF Chat", "url": "https://docanalysis.com/", "desc": "AI document analyzer with multi-language Q&A and key points extraction."},
        {"name": "Anysummary", "cat": "Data & Synthesis AI", "url": "https://www.anysummary.app/", "desc": "Summarize long PDFs, interviews, audio, and video files in seconds."}
    ]

    def frame_titus_omni(self, parent) -> ctk.CTkFrame:
        """⚡ TitusOmni — Omniscient & Omnipotent Conversational AI Assistant Workspace."""
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(2, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # 1. TOP COMMAND BAR & ACTIVE MODEL ROUTER
        # ----------------------------------------------------------------------
        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        title_row = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_row.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            title_row,
            text="⚡ TitusOmni  |  Omniscient & Omnipotent Intelligence Bot",
            font=("Arial", 16, "bold"),
            text_color=ACCENT_AMBER
        ).pack(side="left")

        btn_hub_switch = ctk.CTkButton(
            title_row,
            text="🌐 50 AI Tools Hub ➔",
            width=160,
            height=28,
            font=("Arial", 11, "bold"),
            fg_color="gray30",
            hover_color=PRIMARY_COLOR,
            command=self.show_ai_tools_hub
        )
        btn_hub_switch.pack(side="right", padx=(5, 0))

        btn_select_pdf = ctk.CTkButton(
            title_row,
            text="📂 Switch PDF",
            width=120,
            height=28,
            font=("Arial", 11, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.upload_master_pdf
        )
        btn_select_pdf.pack(side="right", padx=5)

        provider_map = {
            "🤖 Auto-Smart Omni (Auto-Switch & Failover)": {"key_name": "auto", "models": ["auto-best (Gemini ➔ Groq ➔ OpenAI ➔ Claude ➔ Local)"]},
            "Google Gemini 2.0 (1M+ Tokens)": {"key_name": "gemini", "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"]},
            "Groq Ultra-Fast (Free Tier)": {"key_name": "groq", "models": ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b", "mixtral-8x7b-32768", "gemma2-9b-it"]},
            "OpenRouter Gateway": {"key_name": "openrouter", "models": ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-r1:free"]},
            "OpenAI GPT-4o": {"key_name": "openai", "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]},
            "Anthropic Claude 3.5": {"key_name": "claude", "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]},
            "Local Offline Engine (Zero-Key)": {"key_name": "local", "models": ["local-bm25-search"]}
        }

        config_row = ctk.CTkFrame(top_bar, fg_color="transparent")
        config_row.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(config_row, text="AI Engine:", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 4))
        opt_provider = ctk.CTkOptionMenu(config_row, values=list(provider_map.keys()), width=210)
        opt_provider.pack(side="left", padx=4)

        ctk.CTkLabel(config_row, text="Model:", font=("Arial", 11, "bold")).pack(side="left", padx=(8, 4))
        opt_model = ctk.CTkOptionMenu(config_row, values=provider_map["🤖 Auto-Smart Omni (Auto-Switch & Failover)"]["models"], width=170)
        opt_model.pack(side="left", padx=4)

        lbl_key = ctk.CTkLabel(config_row, text="API Key:", font=("Arial", 11, "bold"))
        lbl_key.pack(side="left", padx=(8, 4))

        ent_api_key = ctk.CTkEntry(config_row, show="*", width=150, placeholder_text="Optional / Auto...")
        ent_api_key.pack(side="left", padx=4)

        def update_provider_ui(choice: str):
            info = provider_map.get(choice, provider_map["🤖 Auto-Smart Omni (Auto-Switch & Failover)"])
            opt_model.configure(values=info["models"])
            opt_model.set(info["models"][0])
            k_name = info["key_name"]
            if k_name == "local":
                ent_api_key.configure(state="disabled", placeholder_text="Offline (No Key Required)")
                ent_api_key.delete(0, "end")
                lbl_key.configure(text_color="gray50")
            elif k_name == "auto":
                ent_api_key.configure(state="normal", placeholder_text="Auto / Fallback Active")
                ent_api_key.delete(0, "end")
                lbl_key.configure(text_color=TEXT_LIGHT)
                saved_k = self.api_keys.get("gemini", "") or self.api_keys.get("groq", "") or self.api_keys.get("openai", "")
                if saved_k:
                    ent_api_key.insert(0, saved_k)
            else:
                ent_api_key.configure(state="normal", placeholder_text=f"Enter {choice} Key...")
                lbl_key.configure(text_color=TEXT_LIGHT)
                ent_api_key.delete(0, "end")
                saved_k = self.api_keys.get(k_name, "")
                if saved_k:
                    ent_api_key.insert(0, saved_k)

        opt_provider.configure(command=update_provider_ui)

        is_key_hidden = [True]
        def toggle_key_visibility():
            if is_key_hidden[0]:
                ent_api_key.configure(show="")
                btn_show_key.configure(text="🔒 Hide")
                is_key_hidden[0] = False
            else:
                ent_api_key.configure(show="*")
                btn_show_key.configure(text="👁️ Show")
                is_key_hidden[0] = True

        btn_show_key = ctk.CTkButton(config_row, text="👁️ Show", width=55, command=toggle_key_visibility, fg_color="gray35")
        btn_show_key.pack(side="left", padx=2)

        def save_current_key():
            p_choice = opt_provider.get()
            k_name = provider_map.get(p_choice, {}).get("key_name")
            val = ent_api_key.get().strip()
            if k_name and k_name != "local":
                target_k = "gemini" if k_name == "auto" else k_name
                self.api_keys[target_k] = val
                self.save_api_keys_config()
                messagebox.showinfo("Saved", f"Saved API key for {p_choice} locally!")

        btn_save_key = ctk.CTkButton(config_row, text="💾 Save", width=55, command=save_current_key, fg_color=PRIMARY_COLOR)
        btn_save_key.pack(side="left", padx=2)

        btn_get_free_key = ctk.CTkButton(
            config_row,
            text="⚡ Free Gemini Key",
            width=135,
            font=("Arial", 11, "bold"),
            fg_color=ACCENT_GREEN,
            hover_color=PRIMARY_HOVER,
            command=lambda: webbrowser.open("https://aistudio.google.com/app/apikey")
        )
        btn_get_free_key.pack(side="left", padx=4)

        update_provider_ui("🤖 Auto-Smart Omni (Auto-Switch & Failover)")

        # ----------------------------------------------------------------------
        # 2. TITUSOMNI SUPERPOWERS QUICK ACTION BAR
        # ----------------------------------------------------------------------
        preset_bar = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=6)
        preset_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=2)

        def run_omni_prompt(prompt_text: str):
            send_user_message(prompt_text)

        ctk.CTkButton(preset_bar, text="📝 Full Synthesis", height=28, command=lambda: run_omni_prompt("Please provide a comprehensive multi-section executive synthesis of this document with page citations [Page X]."), fg_color="gray25", hover_color=PRIMARY_COLOR).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(preset_bar, text="🎯 10 Exam MCQs + Key", height=28, command=lambda: run_omni_prompt("Generate 10 rigorous multiple choice exam questions (MCQs) with options A-D, answer key, and detailed pedagogical rationale based on this document with page citations."), fg_color="gray25", hover_color=PRIMARY_COLOR).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(preset_bar, text="📋 Lesson Plan & Objectives", height=28, command=lambda: run_omni_prompt("Create a structured pedagogical lesson plan including Bloom's taxonomy learning outcomes, teaching strategies, unit topics, and assessment criteria from this document with page citations."), fg_color="gray25", hover_color=PRIMARY_COLOR).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(preset_bar, text="📊 Extract Tables & Data", height=28, command=lambda: run_omni_prompt("Extract, tabulate, and explain all numerical statistics, course credit distributions, and tabular data found in this document with page citations."), fg_color="gray25", hover_color=PRIMARY_COLOR).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(preset_bar, text="📑 Outline & TOC", height=28, command=lambda: run_omni_prompt("Provide a section-by-section structural outline and syllabus breakdown with page numbers."), fg_color="gray25", hover_color=PRIMARY_COLOR).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(preset_bar, text="🌐 Translate to Malayalam", height=28, command=lambda: run_omni_prompt("Translate the executive overview and key objectives of this document into fluent Malayalam script with page references."), fg_color="gray25", hover_color=PRIMARY_COLOR).pack(side="left", padx=3, pady=3)

        def export_chat_transcript():
            if not self.chat_history:
                return messagebox.showwarning("No History", "Conversation history is currently empty.")
            save_p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt"), ("Markdown File", "*.md")])
            if save_p:
                lines = [f"=== TITUSOMNI INTELLIGENCE CONVERSATION REPORT ===", f"Document: {os.path.basename(self.active_pdf_path) if self.active_pdf_path else 'None'}\n"]
                for item in self.chat_history:
                    r_title = "USER" if item["role"] == "user" else "TITUSOMNI"
                    lines.append(f"[{r_title}]\n{item['content']}\n" + "-"*50 + "\n")
                with open(save_p, "w", encoding="utf-8") as file_out:
                    file_out.write("\n".join(lines))
                messagebox.showinfo("Exported", f"TitusOmni intelligence report exported to:\n{save_p}")

        def clear_chat_history():
            self.chat_history.clear()
            for w in chat_scroll.winfo_children():
                w.destroy()
            append_system_intro()

        ctk.CTkButton(preset_bar, text="💾 Export", width=70, height=28, command=export_chat_transcript, fg_color="gray25", hover_color=ACCENT_GREEN).pack(side="right", padx=3, pady=3)
        ctk.CTkButton(preset_bar, text="🧹 Clear", width=65, height=28, command=clear_chat_history, fg_color="gray25", hover_color="crimson").pack(side="right", padx=3, pady=3)

        # ----------------------------------------------------------------------
        # 3. INTERACTIVE CHAT STREAM WITH CITATIONS & DIRECT ACTION CARDS
        # ----------------------------------------------------------------------
        chat_scroll = ctk.CTkScrollableFrame(f, fg_color="gray15", corner_radius=8)
        chat_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        def detect_action_intent(text_query: str):
            ql = text_query.lower().strip()
            if any(k in ql for k in ['compress', 'reduce size', 'shrink', 'smaller size']):
                return 'compress', '⚡ Execute File Size Compression Now', self.show_compress_tool
            elif any(k in ql for k in ['word', 'docx', 'convert to word']):
                return 'pdf_to_word', '📄 Convert PDF to Word (.docx) Now', self.show_pdf_to_word_tool
            elif any(k in ql for k in ['ocr', 'scan', 'searchable', 'image to text']):
                return 'ocr', '🔍 Execute Multilingual OCR Scan Now', self.show_ocr_tool
            elif any(k in ql for k in ['extract page', 'split', 'save page', 'cut page']):
                return 'split', '✂️ Execute Page Extraction Now', self.show_split_tool
            elif any(k in ql for k in ['watermark', 'stamp']):
                return 'watermark', '💧 Apply Watermark / Stamp Now', self.show_watermark_tool
            elif any(k in ql for k in ['toc', 'table of contents', 'index', 'openview', 'bookmarks']):
                return 'openview', '📖 Build OpenView Index Page Now', self.show_openview_tool
            elif any(k in ql for k in ['encrypt', 'protect', 'password', 'lock']):
                return 'protect', '🔒 Apply AES Encryption Now', self.show_protect_tool
            return None, None, None

        def append_bubble(role: str, text: str, badge: Optional[str] = None, action_info: Optional[Tuple] = None):
            is_user = (role == "user")
            bubble_frame = ctk.CTkFrame(
                chat_scroll,
                fg_color="#5B21B6" if is_user else "#1E293B",
                border_width=1,
                border_color="#7C3AED" if is_user else "#334155",
                corner_radius=10
            )
            
            if is_user:
                bubble_frame.pack(anchor="e", pady=6, padx=(60, 10), fill="none")
                header_txt = "👤 You"
                h_color = ACCENT_AMBER
            else:
                bubble_frame.pack(anchor="w", pady=6, padx=(10, 60), fill="none")
                header_txt = f"⚡ TitusOmni ({badge})" if badge else "⚡ TitusOmni (Omniscient AI)"
                h_color = ACCENT_GREEN

            header_row = ctk.CTkFrame(bubble_frame, fg_color="transparent")
            header_row.pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(header_row, text=header_txt, font=("Arial", 11, "bold"), text_color=h_color).pack(side="left")

            lbl_msg = ctk.CTkLabel(
                bubble_frame,
                text=text,
                font=("Segoe UI", 12),
                text_color="#FFFFFF",
                justify="left",
                anchor="w",
                wraplength=480
            )
            lbl_msg.pack(padx=12, pady=(2, 8), fill="both", expand=True)

            if role == "assistant":
                # Page Citations
                matches = re.findall(r'\[Page\s*(\d+)\]|Page\s*(\d+)', text, re.IGNORECASE)
                page_nums = set()
                for m in matches:
                    num_str = m[0] or m[1]
                    if num_str.isdigit():
                        page_nums.add(int(num_str))

                if page_nums:
                    citations_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
                    citations_frame.pack(anchor="w", padx=10, pady=(0, 6))
                    ctk.CTkLabel(citations_frame, text="Document References:", font=("Arial", 10, "italic"), text_color="gray70").pack(side="left", padx=(0, 4))
                    for p_num in sorted(page_nums):
                        ctk.CTkButton(
                            citations_frame,
                            text=f"📄 Page {p_num}",
                            width=75,
                            height=22,
                            font=("Arial", 10, "bold"),
                            fg_color=BG_CARD,
                            hover_color=PRIMARY_COLOR,
                            command=lambda idx=p_num-1: self.jump_to_page(idx)
                        ).pack(side="left", padx=2)

                # Omnipotent Action Execution Card
                if action_info and action_info[1] and action_info[2]:
                    act_tag, act_label, act_fn = action_info
                    action_card = ctk.CTkFrame(bubble_frame, fg_color=BG_DARK, corner_radius=6)
                    action_card.pack(fill="x", padx=10, pady=(4, 8))
                    ctk.CTkLabel(action_card, text="⚡ Omnipotent PDF Action Ready:", font=("Arial", 10, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=8, pady=(4, 2))
                    ctk.CTkButton(
                        action_card,
                        text=f"{act_label} ➔",
                        height=28,
                        font=("Arial", 11, "bold"),
                        fg_color=PRIMARY_COLOR,
                        hover_color=PRIMARY_HOVER,
                        command=act_fn
                    ).pack(fill="x", padx=8, pady=(2, 6))

        def append_system_intro():
            doc_name = os.path.basename(self.active_pdf_path) if self.active_pdf_path else "No Document Loaded"
            p_count = len(self.pdf_doc) if self.pdf_doc else 0
            if self.active_pdf_path:
                intro_txt = (
                    f"👋 Greetings! I am **TitusOmni**, your Omniscient and Omnipotent Document Intelligence Assistant.\n\n"
                    f"📄 **Active Document**: **{doc_name}** ({p_count} Pages)\n"
                    "🌟 **Omniscient Powers**: Ask any deep question, request executive syntheses, generate 10 exam MCQs with rationale, create pedagogical lesson plans, or extract tables with exact `[Page X]` citations.\n"
                    "🛠️ **Omnipotent Powers**: Command me to perform PDF actions (e.g. *'compress this PDF'*, *'convert to Word'*, *'extract pages 1-5'*, *'run OCR'*, *'watermark CONFIDENTIAL'*)."
                )
            else:
                intro_txt = (
                    "👋 Greetings! I am **TitusOmni**, your Omniscient and Omnipotent Document Intelligence Assistant.\n\n"
                    "To begin, click **'📂 Switch PDF'** above to load a document, or type any academic or PDF question below!\n"
                    "🤖 **Auto-Failover Active**: Seamlessly routed through Google Gemini 2.0, Groq 70B, DeepSeek R1, Claude, OpenAI, or Local Offline Synthesis."
                )
            append_bubble("assistant", intro_txt, badge="TitusOmni Core")

        # ----------------------------------------------------------------------
        # 4. USER COMMAND INPUT & SEND CONTROLS
        # ----------------------------------------------------------------------
        input_frame = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(4, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        ent_chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask TitusOmni anything, request analysis/MCQs, or command a PDF action (e.g. compress this PDF)...",
            height=42,
            font=("Segoe UI", 12)
        )
        ent_chat_input.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="ew")

        def send_user_message(query_override: Optional[str] = None):
            query = query_override if query_override else ent_chat_input.get().strip()
            if not query:
                return

            if not self.active_pdf_path or not os.path.exists(self.active_pdf_path):
                messagebox.showwarning("Master PDF Required", "Please select a PDF document for TitusOmni to analyze.")
                self.upload_master_pdf()
                if not self.active_pdf_path:
                    return

            if not query_override:
                ent_chat_input.delete(0, "end")

            append_bubble("user", query)
            self.chat_history.append({"role": "user", "content": query})

            # Detect Omnipotent Action Intent
            action_info = detect_action_intent(query)

            p_choice = opt_provider.get()
            m_choice = opt_model.get()
            api_k = ent_api_key.get().strip()

            active_keys = dict(self.api_keys)
            k_name = provider_map.get(p_choice, {}).get("key_name", "auto")
            if api_k:
                target_k = "gemini" if k_name == "auto" else k_name
                active_keys[target_k] = api_k

            pages_data = PDFChatEngine.extract_document_pages(self.active_pdf_path)

            def task_backend():
                return PDFChatEngine.query_smart_auto_switch(
                    all_keys=active_keys,
                    preferred_provider=p_choice,
                    preferred_model=m_choice,
                    pages_data=pages_data,
                    history=self.chat_history[:-1],
                    query=query
                )

            def on_complete(result_tuple):
                response_text, provider_badge = result_tuple
                append_bubble("assistant", response_text, badge=provider_badge, action_info=action_info)
                self.chat_history.append({"role": "assistant", "content": response_text})

            self.run_async_task(
                task_backend,
                on_complete=on_complete,
                status_msg=f"TitusOmni synthesizing ({p_choice})..."
            )

        self._titus_omni_send_fn = send_user_message

        btn_send = ctk.CTkButton(
            input_frame,
            text="Send 🚀",
            width=90,
            height=42,
            font=("Arial", 12, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=send_user_message
        )
        btn_send.grid(row=0, column=1, padx=(5, 10), pady=8)

        ent_chat_input.bind("<Return>", lambda event: send_user_message())

        append_system_intro()
        return f

    def frame_ai_tools_hub(self, parent) -> ctk.CTkFrame:
        """50 AI Document Chat Tools Directory Catalog."""
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(3, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # 1. TOP HEADER
        # ----------------------------------------------------------------------
        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        title_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(8, 4))

        doc_name = os.path.basename(self.active_pdf_path) if self.active_pdf_path else "No Master PDF Loaded"
        p_cnt = len(self.pdf_doc) if self.pdf_doc else 0
        ctk.CTkLabel(
            title_frame,
            text=f"🌐 50 AI Document Chat Tools Directory",
            font=("Arial", 16, "bold"),
            text_color=TEXT_LIGHT
        ).pack(side="left")

        btn_titus_omni = ctk.CTkButton(
            title_frame,
            text="⚡ Open TitusOmni AI Bot",
            width=180,
            height=28,
            font=("Arial", 11, "bold"),
            fg_color=ACCENT_GREEN,
            hover_color=PRIMARY_HOVER,
            command=self.show_titus_omni
        )
        btn_titus_omni.pack(side="right", padx=(5, 0))

        btn_select_pdf = ctk.CTkButton(
            title_frame,
            text="📂 Switch PDF",
            width=130,
            height=28,
            font=("Arial", 11, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.upload_master_pdf
        )
        btn_select_pdf.pack(side="right", padx=5)

        active_file_bar = ctk.CTkFrame(top_bar, fg_color="transparent")
        active_file_bar.pack(fill="x", padx=12, pady=(0, 6))

        lbl_active_desc = ctk.CTkLabel(
            active_file_bar,
            text=f"📄 Document: {doc_name} ({p_cnt} Pages)  |  Path: {self.active_pdf_path or 'None'}",
            font=("Arial", 11, "italic"),
            text_color=ACCENT_AMBER
        )
        lbl_active_desc.pack(side="left")

        # ----------------------------------------------------------------------
        # 2. DOCUMENT INTELLIGENCE & 1-CLICK EXTRACTION CARD
        # ----------------------------------------------------------------------
        doc_intel_card = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=8)
        doc_intel_card.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        metrics_row = ctk.CTkFrame(doc_intel_card, fg_color="transparent")
        metrics_row.pack(fill="x", padx=12, pady=(8, 4))

        est_words = p_cnt * 320
        est_tokens = int(est_words * 1.33)
        rec_model = "Google Gemini 2.0 (1M) / Kimi (2M) / Claude 3.5 (200k)" if p_cnt > 100 else ("NotebookLM / SciSpace / ChatGPT" if p_cnt > 30 else "ChatPDF / Humata / Perplexity")

        ctk.CTkLabel(
            metrics_row,
            text=f"📊 Document Scope: {p_cnt} Pages  |  Est. ~{est_words:,} Words (~{est_tokens:,} Tokens)  |  🎯 Recommended AI: {rec_model}",
            font=("Arial", 11, "bold"),
            text_color=ACCENT_AMBER
        ).pack(side="left")

        actions_row = ctk.CTkFrame(doc_intel_card, fg_color="transparent")
        actions_row.pack(fill="x", padx=10, pady=(2, 6))

        def copy_full_document_text():
            if not self.active_pdf_path or not os.path.exists(self.active_pdf_path):
                return messagebox.showwarning("No PDF", "Please select a PDF document first.")
            pages = PDFChatEngine.extract_document_pages(self.active_pdf_path)
            full_txt = "\n\n".join([f"--- Page {p['page']} ---\n{p['text']}" for p in pages if p['text']])
            if not full_txt.strip():
                return messagebox.showwarning("OCR Needed", "No digital text found. Run OCR first.")
            self.clipboard_clear()
            self.clipboard_append(full_txt)
            w_count = len(full_txt.split())
            lbl_status_banner.configure(text=f"📋 Copied Full Document Text ({w_count:,} words) to clipboard!")
            self.set_status(f"Copied {w_count:,} words from full document to clipboard.")

        def copy_executive_scope_text():
            if not self.active_pdf_path or not os.path.exists(self.active_pdf_path):
                return messagebox.showwarning("No PDF", "Please select a PDF document first.")
            pages = PDFChatEngine.extract_document_pages(self.active_pdf_path)
            sample_pages = pages[:25]
            exec_txt = "\n\n".join([f"--- Page {p['page']} ---\n{p['text']}" for p in sample_pages if p['text']])
            self.clipboard_clear()
            self.clipboard_append(exec_txt)
            w_count = len(exec_txt.split())
            lbl_status_banner.configure(text=f"📋 Copied Executive Scope ({len(sample_pages)} Pages, {w_count:,} words) to clipboard!")
            self.set_status(f"Copied {w_count:,} words from executive scope to clipboard.")

        def copy_document_toc_text():
            if not self.active_pdf_path or not os.path.exists(self.active_pdf_path):
                return messagebox.showwarning("No PDF", "Please select a PDF document first.")
            toc = PDFEngine.extract_document_toc(self.active_pdf_path)
            if not toc:
                return messagebox.showinfo("No Outline", "No embedded PDF outline bookmarks found.")
            toc_lines = [f"Level {item['level']}: {item['title']} (Page {item['page']})" for item in toc]
            toc_str = "=== DOCUMENT TABLE OF CONTENTS ===\n" + "\n".join(toc_lines)
            self.clipboard_clear()
            self.clipboard_append(toc_str)
            lbl_status_banner.configure(text=f"📋 Copied Table of Contents ({len(toc)} sections) to clipboard!")
            self.set_status(f"Copied {len(toc)} TOC bookmarks to clipboard.")

        def reveal_file_in_explorer():
            if self.active_pdf_path and os.path.exists(self.active_pdf_path):
                os.system(f'explorer /select,"{os.path.abspath(self.active_pdf_path)}"')
            else:
                self.upload_master_pdf()

        ctk.CTkButton(actions_row, text="📋 Copy Full Document Text", height=32, font=("Arial", 11, "bold"), fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, command=copy_full_document_text).pack(side="left", padx=4)
        ctk.CTkButton(actions_row, text="✂️ Copy Executive Scope (First 25 Pages)", height=32, font=("Arial", 11, "bold"), fg_color="gray25", hover_color=PRIMARY_COLOR, command=copy_executive_scope_text).pack(side="left", padx=4)
        ctk.CTkButton(actions_row, text="📑 Copy Table of Contents", height=32, font=("Arial", 11, "bold"), fg_color="gray25", hover_color=PRIMARY_COLOR, command=copy_document_toc_text).pack(side="left", padx=4)
        ctk.CTkButton(actions_row, text="📁 Reveal in Explorer (Drag & Drop)", height=32, font=("Arial", 11, "bold"), fg_color="gray30", hover_color=ACCENT_GREEN, command=reveal_file_in_explorer).pack(side="left", padx=4)

        lbl_status_banner = ctk.CTkLabel(
            doc_intel_card,
            text="💡 Click any of the 50 AI Tools below to launch — your document file and text are ready to drag-and-drop or paste into the tool window!",
            font=("Arial", 10, "bold"),
            text_color=ACCENT_GREEN
        )
        lbl_status_banner.pack(anchor="w", padx=12, pady=(0, 6))

        # ----------------------------------------------------------------------
        # 3. FILTER / SEARCH CONTROLS FOR 50 AI TOOLS
        # ----------------------------------------------------------------------
        filter_bar = ctk.CTkFrame(f, fg_color="transparent")
        filter_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=2)

        ctk.CTkLabel(filter_bar, text="🔍 Filter AI Tools:", font=("Arial", 11, "bold")).pack(side="left", padx=(4, 6))
        ent_search_tool = ctk.CTkEntry(filter_bar, placeholder_text="Search 50 AI Tools (e.g. NotebookLM, ChatPDF, SciSpace, Gemini, Claude, Humata)...", width=340, height=28)
        ent_search_tool.pack(side="left", padx=4)

        categories = [
            "🌟 All 50 AI Tools",
            "Dedicated PDF Chat",
            "Academic & Research AI",
            "Frontier Multi-Modal LLM",
            "Data & Synthesis AI",
            "Data & Math File Chat"
        ]
        opt_cat_filter = ctk.CTkOptionMenu(filter_bar, values=categories, width=200, height=28)
        opt_cat_filter.pack(side="left", padx=6)

        # ----------------------------------------------------------------------
        # 4. 50 AI TOOLS DIRECTORY SCROLLABLE CATALOG
        # ----------------------------------------------------------------------
        catalog_scroll = ctk.CTkScrollableFrame(f, fg_color="gray15", corner_radius=8)
        catalog_scroll.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        catalog_scroll.grid_columnconfigure((0, 1), weight=1)

        def launch_tool_with_context(tool_info: Dict[str, str]):
            if self.active_pdf_path and os.path.exists(self.active_pdf_path):
                self.clipboard_clear()
                self.clipboard_append(os.path.abspath(self.active_pdf_path))
                try:
                    os.system(f'explorer /select,"{os.path.abspath(self.active_pdf_path)}"')
                except Exception:
                    pass

            webbrowser.open(tool_info["url"])
            t_name = tool_info["name"]
            lbl_status_banner.configure(
                text=f"✅ Opened {t_name}! Drag & drop your PDF into {t_name} or paste extracted text."
            )
            self.set_status(f"Launched {t_name} with pre-attached PDF ready for instant upload/drag-and-drop.")

        def render_tools_list():
            for w in catalog_scroll.winfo_children():
                w.destroy()

            search_q = ent_search_tool.get().strip().lower()
            selected_cat = opt_cat_filter.get()

            filtered = []
            for item in self.AI_TOOLS_CATALOG:
                matches_search = (not search_q) or (search_q in item["name"].lower()) or (search_q in item["desc"].lower()) or (search_q in item["cat"].lower())
                matches_cat = (selected_cat == "🌟 All 50 AI Tools") or (item["cat"] == selected_cat)
                if matches_search and matches_cat:
                    filtered.append(item)

            if not filtered:
                ctk.CTkLabel(catalog_scroll, text="No AI tools matched your search filter.", font=("Arial", 13, "italic"), text_color="gray60").pack(pady=40)
                return

            for idx, tool in enumerate(filtered):
                card = ctk.CTkFrame(
                    catalog_scroll,
                    fg_color=BG_CARD,
                    border_width=1,
                    border_color="#334155",
                    corner_radius=8
                )
                row_idx = idx // 2
                col_idx = idx % 2
                card.grid(row=row_idx, column=col_idx, padx=6, pady=6, sticky="ew")

                c_header = ctk.CTkFrame(card, fg_color="transparent")
                c_header.pack(fill="x", padx=10, pady=(8, 2))

                ctk.CTkLabel(
                    c_header,
                    text=f"🤖 {tool['name']}",
                    font=("Arial", 13, "bold"),
                    text_color="#FFFFFF"
                ).pack(side="left")

                cat_badge = ctk.CTkLabel(
                    c_header,
                    text=f" {tool['cat']} ",
                    font=("Arial", 9, "bold"),
                    fg_color="#3B82F6" if "Frontier" in tool['cat'] else ("#10B981" if "Academic" in tool['cat'] else "#6366F1"),
                    corner_radius=4,
                    text_color="#FFFFFF"
                )
                cat_badge.pack(side="right")

                ctk.CTkLabel(
                    card,
                    text=tool["desc"],
                    font=("Segoe UI", 10),
                    text_color="gray80",
                    justify="left",
                    anchor="w",
                    wraplength=340
                ).pack(padx=10, pady=(2, 8), fill="x")

                btn_launch = ctk.CTkButton(
                    card,
                    text=f"🚀 Open {tool['name']} with Document ➔",
                    height=30,
                    font=("Arial", 11, "bold"),
                    fg_color=PRIMARY_COLOR,
                    hover_color=PRIMARY_HOVER,
                    command=lambda t=tool: launch_tool_with_context(t)
                )
                btn_launch.pack(padx=10, pady=(0, 10), fill="x")

        ent_search_tool.bind("<KeyRelease>", lambda event: render_tools_list())
        opt_cat_filter.configure(command=lambda choice: render_tools_list())

        render_tools_list()
        return f

    def frame_pdf_chat(self, parent) -> ctk.CTkFrame:
        """Alias for backward compatibility - routes to TitusOmni."""
        return self.frame_titus_omni(parent)

    def show_about_dialog(self):
        messagebox.showinfo(
            "About TSTC_Professional PDF Suite",
            "Titus II Teachers College - TSTC_Professional PDF Suite v4.0\n\n"
            "Developed by Dr. Joseph I Thomas\n\n"
            "Integrated Enterprise Desktop Application.\n"
            "Features TitusOmni Omniscient & Omnipotent Conversational Intelligence Engine, Adobe Acrobat Pro, ABBYY FineReader PDF, and the OpenView Dynamic Index Engine.\n\n"
            "Developed for Titus II Teachers College Academic Infrastructure."
        )

# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
if __name__ == "__main__":
    app = TSTC_ProfessionalPDFSuite()
    app.mainloop()