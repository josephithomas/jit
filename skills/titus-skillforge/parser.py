"""
Universal Document and Asset Parser for SkillForge.
Extracts clean, structured text from PDFs, Word docs, PowerPoint, images, and text formats.
"""

from __future__ import annotations
import os
import io
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Try PyMuPDF (pymupdf / fitz) or pypdf
try:
    import pymupdf as fitz
    HAVE_PYMUPDF = True
except ImportError:
    try:
        import fitz
        HAVE_PYMUPDF = True
    except ImportError:
        HAVE_PYMUPDF = False

try:
    import pypdf
    HAVE_PYPDF = True
except ImportError:
    HAVE_PYPDF = False

# Try python-docx
try:
    import docx
    HAVE_DOCX = True
except ImportError:
    HAVE_DOCX = False

# Try python-pptx
try:
    from pptx import Presentation
    HAVE_PPTX = True
except ImportError:
    HAVE_PPTX = False

# Try PIL and pytesseract
try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

try:
    import pytesseract
    common_tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
    ]
    for p in common_tesseract_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break
    HAVE_PYTESSERACT = True
except ImportError:
    HAVE_PYTESSERACT = False


class DocumentParser:
    """Robust extractor for multi-modal files."""

    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.pptx': 'pptx',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.webp': 'image',
        '.bmp': 'image',
        '.tiff': 'image',
        '.txt': 'text',
        '.md': 'text',
        '.markdown': 'text',
        '.rst': 'text',
        '.json': 'text',
        '.yaml': 'text',
        '.yml': 'text',
        '.py': 'text',
        '.js': 'text',
        '.ts': 'text',
        '.html': 'text',
        '.csv': 'text',
        '.xml': 'text',
        '.sh': 'text',
        '.ps1': 'text'
    }

    @classmethod
    def parse_file(cls, file_bytes: bytes, filename: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
        ext = Path(filename).suffix.lower()
        file_type = cls.SUPPORTED_EXTENSIONS.get(ext, 'unknown')

        if file_type == 'pdf':
            return cls._parse_pdf(file_bytes, filename)
        elif file_type == 'docx':
            return cls._parse_docx(file_bytes, filename)
        elif file_type == 'pptx':
            return cls._parse_pptx(file_bytes, filename)
        elif file_type == 'image':
            return cls._parse_image(file_bytes, filename)
        elif file_type == 'text':
            return cls._parse_text(file_bytes, filename)
        else:
            try:
                text = file_bytes.decode('utf-8', errors='replace')
                return {
                    'text': text,
                    'filename': filename,
                    'format': 'text-fallback',
                    'metadata': {'char_count': len(text), 'word_count': len(text.split())}
                }
            except Exception as e:
                return {
                    'text': f"[Error reading file {filename}: unsupported format {ext} ({e})]",
                    'filename': filename,
                    'format': 'unsupported',
                    'metadata': {'error': str(e)}
                }

    @classmethod
    def _parse_pdf(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text_parts = []
        page_count = 0
        metadata: Dict[str, Any] = {}

        if HAVE_PYMUPDF:
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                page_count = len(doc)
                metadata = doc.metadata or {}
                for page_idx in range(page_count):
                    page = doc[page_idx]
                    page_text = page.get_text("text")
                    if page_text.strip():
                        text_parts.append(f"--- Page {page_idx + 1} ---\n{page_text.strip()}")
                doc.close()
            except Exception as e:
                text_parts.append(f"[PyMuPDF extraction note: {e}]")

        if not text_parts and HAVE_PYPDF:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                page_count = len(reader.pages)
                metadata = reader.metadata or {}
                for idx, page in enumerate(reader.pages):
                    pt = page.extract_text()
                    if pt and pt.strip():
                        text_parts.append(f"--- Page {idx + 1} ---\n{pt.strip()}")
            except Exception as e:
                text_parts.append(f"[pypdf fallback note: {e}]")

        full_text = "\n\n".join(text_parts).strip()
        if not full_text:
            full_text = f"[PDF file '{filename}' contains {page_count} pages but no extractable text layer was found.]"

        return {
            'text': full_text,
            'filename': filename,
            'format': 'pdf',
            'metadata': {
                'pages': page_count,
                'char_count': len(full_text),
                'word_count': len(full_text.split()),
                'doc_metadata': {k: str(v) for k, v in metadata.items() if v}
            }
        }

    @classmethod
    def _parse_docx(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        if not HAVE_DOCX:
            return {
                'text': f"[Error: python-docx not available for reading {filename}]",
                'filename': filename,
                'format': 'docx',
                'metadata': {'error': 'python-docx not installed'}
            }

        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            content_blocks = []
            
            for p in doc.paragraphs:
                txt = p.text.strip()
                if not txt:
                    continue
                style_name = p.style.name.lower() if p.style else ""
                if 'heading 1' in style_name:
                    content_blocks.append(f"# {txt}")
                elif 'heading 2' in style_name:
                    content_blocks.append(f"## {txt}")
                elif 'heading 3' in style_name:
                    content_blocks.append(f"### {txt}")
                elif 'list' in style_name:
                    content_blocks.append(f"- {txt}")
                else:
                    content_blocks.append(txt)

            for table_idx, table in enumerate(doc.tables):
                table_lines = [f"\n[Table {table_idx + 1}]"]
                for row in table.rows:
                    row_cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                    table_lines.append("| " + " | ".join(row_cells) + " |")
                content_blocks.append("\n".join(table_lines))

            full_text = "\n\n".join(content_blocks).strip()
            return {
                'text': full_text,
                'filename': filename,
                'format': 'docx',
                'metadata': {
                    'paragraphs': len(doc.paragraphs),
                    'tables': len(doc.tables),
                    'word_count': len(full_text.split()),
                    'char_count': len(full_text)
                }
            }
        except Exception as e:
            return {
                'text': f"[Error reading Word document {filename}: {e}]",
                'filename': filename,
                'format': 'docx',
                'metadata': {'error': str(e)}
            }

    @classmethod
    def _parse_pptx(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        if not HAVE_PPTX:
            return {
                'text': f"[Error: python-pptx not available for reading {filename}]",
                'filename': filename,
                'format': 'pptx',
                'metadata': {'error': 'python-pptx not installed'}
            }

        try:
            prs = Presentation(io.BytesIO(file_bytes))
            slide_blocks = []
            for idx, slide in enumerate(prs.slides):
                slide_texts = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            t = paragraph.text.strip()
                            if t:
                                slide_texts.append(t)
                if slide_texts:
                    slide_blocks.append(f"## Slide {idx + 1}\n" + "\n".join(f"- {t}" for t in slide_texts))

            full_text = "\n\n".join(slide_blocks).strip()
            return {
                'text': full_text,
                'filename': filename,
                'format': 'pptx',
                'metadata': {
                    'slides': len(prs.slides),
                    'word_count': len(full_text.split())
                }
            }
        except Exception as e:
            return {
                'text': f"[Error reading PowerPoint {filename}: {e}]",
                'filename': filename,
                'format': 'pptx',
                'metadata': {'error': str(e)}
            }

    @classmethod
    def _parse_image(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        extracted_text = ""
        ocr_engine = "none"

        if HAVE_PIL:
            try:
                img = Image.open(io.BytesIO(file_bytes))
                width, height = img.size
                image_info = f"Image '{filename}': {width}x{height} px, format {img.format}, mode {img.mode}"
                
                if HAVE_PYTESSERACT:
                    try:
                        extracted_text = pytesseract.image_to_string(img).strip()
                        if extracted_text:
                            ocr_engine = "pytesseract"
                    except Exception as e:
                        extracted_text = ""
                        image_info += f" (Tesseract OCR skipped: {e})"
                
                if not extracted_text:
                    extracted_text = f"[{image_info}. Ready for browser-side OCR (Tesseract.js) or multimodal analysis.]"

                return {
                    'text': extracted_text,
                    'filename': filename,
                    'format': 'image',
                    'metadata': {
                        'dimensions': f"{width}x{height}",
                        'ocr_engine': ocr_engine,
                        'word_count': len(extracted_text.split())
                    }
                }
            except Exception as e:
                return {
                    'text': f"[Error opening image {filename}: {e}]",
                    'filename': filename,
                    'format': 'image',
                    'metadata': {'error': str(e)}
                }

        return {
            'text': f"[Image uploaded: {filename}]",
            'filename': filename,
            'format': 'image',
            'metadata': {}
        }

    @classmethod
    def _parse_text(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        text = ""
        used_enc = "utf-8"

        for enc in encodings:
            try:
                text = file_bytes.decode(enc)
                used_enc = enc
                break
            except UnicodeDecodeError:
                continue

        if not text:
            text = file_bytes.decode('utf-8', errors='replace')
            used_enc = 'utf-8-replace'

        return {
            'text': text.strip(),
            'filename': filename,
            'format': 'text',
            'metadata': {
                'encoding': used_enc,
                'char_count': len(text),
                'word_count': len(text.split()),
                'line_count': len(text.splitlines())
            }
        }
