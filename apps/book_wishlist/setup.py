import sys
import os
import tkinterdnd2
from cx_Freeze import setup, Executable

# Find the tkinterdnd2 library path
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

# Dependencies
build_exe_options = {
    "packages": ["os", "tkinter", "json", "urllib", "webbrowser", "csv", "datetime", "uuid", "re", "keyboard", "tkinterdnd2"],
    "include_files": [(tkdnd_path, 'lib/tkinterdnd2/tkdnd')],
}

bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\BookWishlistPro",
}

base = None
if sys.platform == "win32":
    base = "gui"

setup(
    name="Book Wishlist Pro",
    version="1.0",
    description="A smart library catalog manager.",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[
        Executable(
            "book_wishlist_app.py", 
            base=base, 
            target_name="BookWishlistPro.exe",
            shortcut_name="Book Wishlist Pro",
            shortcut_dir="DesktopFolder"
        )
    ]
)
