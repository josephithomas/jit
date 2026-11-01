with open("b64_logo.txt", "r") as f:
    b64 = f.read().strip()

with open("book_wishlist_app.py", "r", encoding="utf-8") as f:
    content = f.read()

import_str = "import uuid\n\nTITUS_LOGO_B64 = '''" + b64 + "'''\n"
content = content.replace("import uuid", import_str)

old_icon_code = """        # Add Titus icon
        try:
            self.root.iconbitmap("app_icon.ico")
        except Exception as e:
            print(f"Icon not found: {e}")"""

new_icon_code = """        # Add baked Titus icon
        try:
            img = tk.PhotoImage(data=TITUS_LOGO_B64)
            self.root.iconphoto(True, img)
        except Exception as e:
            print(f"Icon not found: {e}")"""

content = content.replace(old_icon_code, new_icon_code)

with open("book_wishlist_app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Injected successfully.")
