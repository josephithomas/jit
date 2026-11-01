"""File classifier, category mapper, and preset organizer definitions."""
import os
import datetime
from typing import Dict, List, Tuple

# Universal extension to category dictionary
CATEGORY_MAP: Dict[str, str] = {
    # Documents
    '.pdf': 'Documents',
    '.doc': 'Documents',
    '.docx': 'Documents',
    '.odt': 'Documents',
    '.rtf': 'Documents',
    '.txt': 'Documents',
    '.md': 'Documents',
    '.tex': 'Documents',
    '.epub': 'Documents',
    '.mobi': 'Documents',
    '.azw3': 'Documents',

    # Spreadsheets
    '.xlsx': 'Spreadsheets',
    '.xls': 'Spreadsheets',
    '.csv': 'Spreadsheets',
    '.ods': 'Spreadsheets',
    '.tsv': 'Spreadsheets',

    # Presentations
    '.pptx': 'Presentations',
    '.ppt': 'Presentations',
    '.odp': 'Presentations',
    '.key': 'Presentations',

    # Images
    '.jpg': 'Images',
    '.jpeg': 'Images',
    '.png': 'Images',
    '.gif': 'Images',
    '.webp': 'Images',
    '.svg': 'Images',
    '.bmp': 'Images',
    '.tiff': 'Images',
    '.tif': 'Images',
    '.ico': 'Images',
    '.raw': 'Images',
    '.cr2': 'Images',
    '.nef': 'Images',
    '.heic': 'Images',
    '.psd': 'Images',
    '.ai': 'Images',

    # Audio
    '.mp3': 'Audio',
    '.wav': 'Audio',
    '.flac': 'Audio',
    '.aac': 'Audio',
    '.ogg': 'Audio',
    '.m4a': 'Audio',
    '.wma': 'Audio',
    '.opus': 'Audio',
    '.mid': 'Audio',
    '.midi': 'Audio',

    # Video
    '.mp4': 'Video',
    '.mkv': 'Video',
    '.avi': 'Video',
    '.mov': 'Video',
    '.wmv': 'Video',
    '.flv': 'Video',
    '.webm': 'Video',
    '.m4v': 'Video',
    '.mpeg': 'Video',
    '.mpg': 'Video',

    # Archives
    '.zip': 'Archives',
    '.rar': 'Archives',
    '.7z': 'Archives',
    '.tar': 'Archives',
    '.gz': 'Archives',
    '.bz2': 'Archives',
    '.xz': 'Archives',
    '.iso': 'Archives',

    # Code & Development
    '.py': 'Development',
    '.pyw': 'Development',
    '.js': 'Development',
    '.jsx': 'Development',
    '.ts': 'Development',
    '.tsx': 'Development',
    '.html': 'Development',
    '.htm': 'Development',
    '.css': 'Development',
    '.scss': 'Development',
    '.json': 'Development',
    '.xml': 'Development',
    '.yaml': 'Development',
    '.yml': 'Development',
    '.sql': 'Development',
    '.c': 'Development',
    '.cpp': 'Development',
    '.h': 'Development',
    '.hpp': 'Development',
    '.cs': 'Development',
    '.java': 'Development',
    '.kt': 'Development',
    '.go': 'Development',
    '.rs': 'Development',
    '.php': 'Development',
    '.rb': 'Development',
    '.sh': 'Development',
    '.bat': 'Development',
    '.ps1': 'Development',

    # Executables & Installers
    '.exe': 'Executables',
    '.msi': 'Executables',
    '.apk': 'Executables',
    '.dmg': 'Executables',
    '.appx': 'Executables',

    # Fonts
    '.ttf': 'Fonts',
    '.otf': 'Fonts',
    '.woff': 'Fonts',
    '.woff2': 'Fonts',
}

CATEGORY_ICONS = {
    'Documents': '📄',
    'Spreadsheets': '📊',
    'Presentations': '📽️',
    'Images': '🖼️',
    'Audio': '🎵',
    'Video': '🎬',
    'Archives': '📦',
    'Development': '💻',
    'Executables': '⚙️',
    'Fonts': '🔤',
    'Others': '📁'
}

def get_file_category(filename: str) -> str:
    """Returns the broad human-friendly category for a given filename."""
    _, ext = os.path.splitext(filename.lower())
    return CATEGORY_MAP.get(ext, 'Others')

def format_file_size(size_bytes: int) -> str:
    """Formats bytes to a readable string (e.g. 4.2 MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_size_bracket(size_bytes: int) -> str:
    """Returns size classification folder name."""
    if size_bytes < 100 * 1024:
        return "Tiny (< 100 KB)"
    elif size_bytes < 1024 * 1024:
        return "Small (100 KB - 1 MB)"
    elif size_bytes < 50 * 1024 * 1024:
        return "Medium (1 MB - 50 MB)"
    elif size_bytes < 500 * 1024 * 1024:
        return "Large (50 MB - 500 MB)"
    else:
        return "Huge (> 500 MB)"

def get_date_brackets(timestamp: float) -> Dict[str, str]:
    """Generates various date breakdown representations for a file."""
    dt = datetime.datetime.fromtimestamp(timestamp)
    month_name = dt.strftime("%B")
    quarter = (dt.month - 1) // 3 + 1
    return {
        'year': str(dt.year),
        'month': f"{dt.month:02d}-{month_name}",
        'year_month': f"{dt.year}/{dt.month:02d}-{month_name}",
        'quarter': f"{dt.year}-Q{quarter}",
        'date': dt.strftime("%Y-%m-%d"),
        'year_quarter': f"{dt.year}/Q{quarter}"
    }

def get_alphabetical_bucket(filename: str, group_mode: str = 'groups') -> str:
    """Returns alphabetical bucket (A-E or single letter)."""
    clean_name = os.path.basename(filename).strip().upper()
    if not clean_name:
        return 'Others'
    first_char = clean_name[0]
    if not first_char.isalpha():
        return '0-9 & Symbols'

    if group_mode == 'single':
        return first_char

    if first_char in 'ABCDE':
        return 'A - E'
    elif first_char in 'FGHIJ':
        return 'F - J'
    elif first_char in 'KLMNO':
        return 'K - O'
    elif first_char in 'PQRST':
        return 'P - T'
    elif first_char in 'UVWXYZ':
        return 'U - Z'
    return '0-9 & Symbols'

