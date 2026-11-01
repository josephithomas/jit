"""Deep content inspector for reading PDF text, Word docs, EXIF metadata, and plain text."""
import os
import re
from typing import Dict, Any, Optional

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

try:
    import docx
except ImportError:
    docx = None

try:
    from PIL import Image, ExifTags
except ImportError:
    Image = None
    ExifTags = None


class ContentInspector:
    """Extracts text content and rich metadata from documents and media."""

    @staticmethod
    def extract_text(file_path: str, max_chars: int = 15000) -> str:
        """Extracts text from PDF, DOCX, TXT, or code files safely."""
        if not os.path.isfile(file_path):
            return ""

        _, ext = os.path.splitext(file_path.lower())

        # 1. PDF extraction
        if ext == '.pdf':
            if fitz is None:
                return ""
            try:
                text_parts = []
                doc = fitz.open(file_path)
                # Inspect first 5 pages max for speed
                pages_to_check = min(len(doc), 5)
                for i in range(pages_to_check):
                    page_text = doc[i].get_text()
                    if page_text:
                        text_parts.append(page_text)
                    if sum(len(p) for p in text_parts) >= max_chars:
                        break
                doc.close()
                return "\n".join(text_parts)[:max_chars]
            except Exception:
                return ""

        # 2. Word .docx extraction
        elif ext == '.docx':
            if docx is None:
                return ""
            try:
                doc = docx.Document(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return "\n".join(paragraphs)[:max_chars]
            except Exception:
                return ""

        # 3. Plain text / Markdown / Code
        elif ext in ('.txt', '.md', '.csv', '.json', '.xml', '.html', '.log', '.py', '.js', '.yaml', '.yml', '.rtf'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(max_chars)
            except Exception:
                return ""

        return ""

    @staticmethod
    def extract_image_metadata(file_path: str) -> Dict[str, Any]:
        """Extracts camera model, date taken, and dimensions from images."""
        info = {
            'width': 0,
            'height': 0,
            'dimensions': '',
            'camera': '',
            'date_taken': ''
        }
        if not Image:
            return info

        _, ext = os.path.splitext(file_path.lower())
        if ext not in ('.jpg', '.jpeg', '.png', '.tiff', '.webp', '.bmp'):
            return info

        try:
            with Image.open(file_path) as img:
                info['width'], info['height'] = img.size
                info['dimensions'] = f"{img.size[0]}x{img.size[1]}"

                exif = img.getexif()
                if exif and ExifTags:
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if tag_name == 'Model' and isinstance(value, str):
                            info['camera'] = value.strip()
                        elif tag_name == 'DateTime' and isinstance(value, str):
                            info['date_taken'] = value.strip().replace(':', '-')
        except Exception:
            pass

        return info

    @classmethod
    def matches_content_query(cls, file_path: str, query: str, is_regex: bool = False) -> bool:
        """Checks if document contains the given keyword or regex pattern."""
        if not query:
            return True
        text = cls.extract_text(file_path)
        if not text:
            return False

        if is_regex:
            try:
                return bool(re.search(query, text, re.IGNORECASE))
            except re.error:
                return False
        else:
            return query.lower() in text.lower()

