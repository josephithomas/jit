import os
import sys
import subprocess

def install_dependencies():
    if getattr(sys, 'frozen', False):
        return
        
    missing = []
    try:
        import tkinterdnd2
    except ImportError:
        missing.append("tkinterdnd2")
    try:
        import keyboard
    except ImportError:
        missing.append("keyboard")
        
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print("Dependencies installed successfully. Restarting application...")
            os.execv(sys.executable, ['python', os.path.abspath(__file__)] + sys.argv[1:])
        except Exception as e:
            print(f"Failed to install dependencies: {e}")

install_dependencies()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import urllib.request
import urllib.parse
import webbrowser
import csv
from datetime import datetime
import uuid
import re
import keyboard
try:
    from tkinterdnd2 import DND_FILES, DND_TEXT, TkinterDnD
    DND_SUPPORTED = True
except ImportError:
    DND_SUPPORTED = False
import time

TITUS_LOGO_B64 = '''iVBORw0KGgoAAAANSUhEUgAAAEwAAABQCAYAAACzg5PLAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyFpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNS1jMDE0IDc5LjE1MTQ4MSwgMjAxMy8wMy8xMy0xMjowOToxNSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIChXaW5kb3dzKSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpCQUUyQThGRUM2MjQxMUU4QUE3MkIxMEI1RjQyNzYyMyIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpCQUUyQThGRkM2MjQxMUU4QUE3MkIxMEI1RjQyNzYyMyI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOkJBRTJBOEZDQzYyNDExRThBQTcyQjEwQjVGNDI3NjIzIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkJBRTJBOEZEQzYyNDExRThBQTcyQjEwQjVGNDI3NjIzIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+tSqaqgAANA9JREFUeNrEfAdgVVW2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'''

import os
import sys

# Ensure DATA_FILE is in the same directory as this script/exe
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(script_dir, "wishlist_v2.json")

class BookWishlistProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TSTC Book Wishlist Architect")
        
        # Add baked Titus icon
        try:
            img = tk.PhotoImage(data=TITUS_LOGO_B64)
            self.root.iconphoto(True, img)
        except Exception as e:
            print(f"Icon not found: {e}")
            
        self.root.geometry("1150x800")
        self.root.minsize(900, 600)
        
        self.books = []
        self.settings = {"location": "auto", "manual_loc": "", "theme": "default"}
        self.current_filter = "All"
        self.sort_reverse = False
        
        self.load_data()
        
        # 1. OS Menu Bar
        self.setup_os_menu()
        
        # 2. Main Tool & Action Bar (Top)
        self.setup_tool_bar()
        
        # Main content area
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 3. Navigation Bar (Left)
        self.setup_nav_bar()
        
        # Right Side (Content)
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_paned, weight=1)
        
        # 4. Search/Filter Bar
        self.setup_search_bar()
        
        # 5. Treeview (List of Books)
        self.setup_treeview()
        
        # 6. Information & Action Bar (Details Pane at Bottom)
        self.setup_details_pane()
        
        # 7. Status Information Bar (Very Bottom)
        self.setup_status_bar()
        self.setup_shortcuts()
        
        self.apply_theme(self.settings.get("theme", "default"))
        self.refresh_list()
        self.update_status("Application ready. Welcome to Book Wishlist Pro!")

    # --- Data Management ---
    def load_data(self):
        if os.path.exists(DATA_FILE):
            for attempt in range(5):
                try:
                    with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                        self.books = data.get("books", [])
                        self.settings = data.get("settings", self.settings)
                    break
                except PermissionError:
                    if attempt < 4:
                        time.sleep(0.5)
                    else:
                        print("Permission denied when loading data.")
                except Exception as e:
                    print(f"Error loading data: {e}")
                    break

    def save_data(self):
        tmp_file = DATA_FILE + ".tmp"
        for attempt in range(5):
            try:
                with open(tmp_file, 'w') as f:
                    json.dump({"books": self.books, "settings": self.settings}, f, indent=4)
                os.replace(tmp_file, DATA_FILE)
                return
            except PermissionError as e:
                if attempt < 4:
                    time.sleep(0.5)
                else:
                    messagebox.showerror("Error", f"Failed to save data: {e}\n\nThe file may be locked by another program or a background instance.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
                break

    # --- UI Setup ---
    def setup_os_menu(self):
        menubar = tk.Menu(self.root)
        
        # 8. File Menu (Import/Export)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Book", accelerator="Ctrl+N", command=self.clear_details)
        file_menu.add_separator()
        file_menu.add_command(label="Import from CSV...", accelerator="Ctrl+I", command=self.import_csv)
        file_menu.add_command(label="Export to CSV...", accelerator="Ctrl+E", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # 9. View Menu (Themes)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Light Theme", command=lambda: self.apply_theme("light"))
        view_menu.add_command(label="Dark Theme", command=lambda: self.apply_theme("dark"))
        view_menu.add_command(label="Default Theme", command=lambda: self.apply_theme("default"))
        menubar.add_cascade(label="View", menu=view_menu)
        
        # 10. Tools Menu (Statistics, Settings)
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Statistics Dashboard", accelerator="Ctrl+T", command=self.show_statistics)
        tools_menu.add_command(label="Location Settings...", command=self.show_settings)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # 11. Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Keyboard Shortcuts", accelerator="F1", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def setup_tool_bar(self):
        toolbar = ttk.Frame(self.root, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="➕ Add New (Ctrl+N)", command=self.clear_details).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="💾 Save Changes (Ctrl+S)", command=self.save_book_details).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="🗑️ Delete Selected (Del)", command=self.delete_book).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="🌐 Fetch Title Meta (Ctrl+M)", command=lambda: self.fetch_metadata("title")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="🌐 Fetch ISBN Meta", command=lambda: self.fetch_metadata("isbn")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(toolbar, text="📊 Statistics (Ctrl+T)", command=self.show_statistics).pack(side=tk.LEFT, padx=2, pady=2)

    def setup_nav_bar(self):
        nav_frame = ttk.Frame(self.main_paned, width=150)
        self.main_paned.add(nav_frame, weight=0)
        
        ttk.Label(nav_frame, text="Navigation", font=("Arial", 12, "bold")).pack(pady=10)
        
        categories = ["All", "Unread", "Reading", "Completed"]
        for cat in categories:
            btn = ttk.Button(nav_frame, text=cat, command=lambda c=cat: self.filter_by_category(c))
            btn.pack(fill=tk.X, padx=5, pady=2)

    def setup_search_bar(self):
        search_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(search_frame, weight=0)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search (Ctrl+F):").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.refresh_list)
        self.ent_search = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Clear", command=lambda: self.search_var.set("")).pack(side=tk.LEFT, padx=5)

    def setup_treeview(self):
        tree_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(tree_frame, weight=2)
        
        # 12. Multi-column Sortable Treeview
        columns = ("title", "author", "genre", "status", "rating", "added")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        headers = {"title": "Title", "author": "Author", "genre": "Genre", 
                   "status": "Status", "rating": "Rating", "added": "Date Added"}
        
        for col in columns:
            self.tree.heading(col, text=headers[col], command=lambda _col=col: self.sort_treeview(_col))
            self.tree.column(col, width=100)
        self.tree.column("title", width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # 13. Context Menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_book)
        self.context_menu.add_command(label="Fetch Metadata (Title)", command=lambda: self.fetch_metadata("title"))
        self.context_menu.add_command(label="Fetch Metadata (ISBN)", command=lambda: self.fetch_metadata("isbn"))
        self.tree.bind("<Button-3>", self.show_context_menu)

    def setup_details_pane(self):
        details_frame = ttk.LabelFrame(self.right_paned, text="Detailed Book Information & Actions")
        self.right_paned.add(details_frame, weight=1)
        
        # Left side for Info forms
        form_frame = ttk.Frame(details_frame)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Form fields
        self.cur_id = None
        
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_title = ttk.Entry(form_frame, width=40)
        self.ent_title.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(form_frame, text="Author:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_author = ttk.Entry(form_frame, width=40)
        self.ent_author.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(form_frame, text="ISBN:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ent_isbn = ttk.Entry(form_frame, width=40)
        self.ent_isbn.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(form_frame, text="Genre:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ent_genre = ttk.Entry(form_frame, width=40)
        self.ent_genre.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(form_frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.cbo_status = ttk.Combobox(form_frame, values=["Unread", "Reading", "Completed"], state="readonly")
        self.cbo_status.set("Unread")
        self.cbo_status.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(form_frame, text="Rating (1-5):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.cbo_rating = ttk.Combobox(form_frame, values=["Unrated", "1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"], state="readonly")
        self.cbo_rating.set("Unrated")
        self.cbo_rating.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(form_frame, text="Notes:").grid(row=6, column=0, sticky=tk.NW, pady=2)
        self.txt_notes = tk.Text(form_frame, width=30, height=4)
        self.txt_notes.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Right side for External Actions
        action_frame = ttk.Frame(details_frame)
        action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        
        ttk.Label(action_frame, text="14-19. External Actions", font=("Arial", 10, "bold")).pack(pady=5)
        self.search_title_only_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(action_frame, text="Search Title Only", variable=self.search_title_only_var).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="🛒 Buy Google (Alt+S)", command=lambda: self.open_link("shopping")).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="🛒 Buy Amazon (Alt+A)", command=lambda: self.open_link("amazon")).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="📖 Goodreads (Alt+G)", command=lambda: self.open_link("goodreads")).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="🏛️ Libraries (Alt+L)", command=lambda: self.open_link("libraries")).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="🏪 Bookstores (Alt+B)", command=lambda: self.open_link("bookstores")).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="🌍 WorldCat (Alt+W)", command=lambda: self.open_link("worldcat")).pack(fill=tk.X, pady=2)

    def setup_status_bar(self):
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready.")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.stats_label = ttk.Label(self.status_frame, text="Total Books: 0")
        self.stats_label.pack(side=tk.RIGHT, padx=5, pady=2)

    def setup_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.clear_details())
        self.root.bind("<Control-s>", lambda e: self.save_book_details())
        self.root.bind("<Delete>", lambda e: self.delete_book())
        self.root.bind("<Control-m>", lambda e: self.fetch_metadata("title"))
        self.root.bind("<Control-i>", lambda e: self.import_csv())
        self.root.bind("<Control-e>", lambda e: self.export_csv())
        self.root.bind("<Control-t>", lambda e: self.show_statistics())
        self.root.bind("<Control-f>", lambda e: self.ent_search.focus())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        
        self.root.bind("<Alt-s>", lambda e: self.open_link("shopping"))
        self.root.bind("<Alt-a>", lambda e: self.open_link("amazon"))
        self.root.bind("<Alt-g>", lambda e: self.open_link("goodreads"))
        self.root.bind("<Alt-l>", lambda e: self.open_link("libraries"))
        self.root.bind("<Alt-b>", lambda e: self.open_link("bookstores"))
        self.root.bind("<Alt-w>", lambda e: self.open_link("worldcat"))

        self.root.bind("<F1>", lambda e: self.show_shortcuts())

    def show_shortcuts(self):
        shortcuts_text = (
            "Keyboard Shortcuts:\n\n"
            "Ctrl+N: Add New Book / Clear Details\n"
            "Ctrl+S: Save Changes\n"
            "Delete: Delete Selected Book\n"
            "Ctrl+M: Fetch Metadata (Title)\n"
            "Ctrl+I: Import CSV\n"
            "Ctrl+E: Export CSV\n"
            "Ctrl+T: Show Statistics Dashboard\n"
            "Ctrl+F: Focus Search\n"
            "Ctrl+Q: Exit Application\n\n"
            "External Links:\n"
            "Alt+S: Buy on Google\n"
            "Alt+A: Buy on Amazon\n"
            "Alt+G: View on Goodreads\n"
            "Alt+L: Find in Libraries\n"
            "Alt+B: Find in Bookstores\n"
            "Alt+W: Search on WorldCat\n"
            "F1: Show this Shortcuts page\n"
        )
        messagebox.showinfo("Shortcuts", shortcuts_text)

    # --- Actions & Logic ---
    def filter_by_category(self, category):
        self.current_filter = category
        self.refresh_list()
        self.update_status(f"Filtered by: {category}")

    def refresh_list(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_query = self.search_var.get().lower()
        
        count = 0
        for book in self.books:
            if self.current_filter != "All" and book.get("status") != self.current_filter:
                continue
                
            if search_query and search_query not in book.get("title", "").lower() and search_query not in book.get("author", "").lower():
                continue
                
            self.tree.insert("", "end", iid=book["id"], values=(
                book.get("title", ""),
                book.get("author", ""),
                book.get("genre", ""),
                book.get("status", "Unread"),
                book.get("rating", "Unrated"),
                book.get("added_on", "")
            ))
            count += 1
            
        self.stats_label.config(text=f"Showing: {count} / Total: {len(self.books)}")

    def sort_treeview(self, col):
        # Retrieve items
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(reverse=self.sort_reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)
        self.sort_reverse = not self.sort_reverse
        self.update_status(f"Sorted by {col}")

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            book_id = selected[0]
            book = next((b for b in self.books if b["id"] == book_id), None)
            if book:
                self.cur_id = book_id
                self.ent_title.delete(0, tk.END)
                self.ent_title.insert(0, book.get("title", ""))
                self.ent_author.delete(0, tk.END)
                self.ent_author.insert(0, book.get("author", ""))
                if hasattr(self, 'ent_isbn'):
                    self.ent_isbn.delete(0, tk.END)
                    self.ent_isbn.insert(0, book.get("isbn", ""))
                self.ent_genre.delete(0, tk.END)
                self.ent_genre.insert(0, book.get("genre", ""))
                self.cbo_status.set(book.get("status", "Unread"))
                self.cbo_rating.set(book.get("rating", "Unrated"))
                self.txt_notes.delete("1.0", tk.END)
                self.txt_notes.insert(tk.END, book.get("notes", ""))

    def clear_details(self):
        self.cur_id = None
        self.tree.selection_remove(self.tree.selection())
        self.ent_title.delete(0, tk.END)
        self.ent_author.delete(0, tk.END)
        if hasattr(self, 'ent_isbn'):
            self.ent_isbn.delete(0, tk.END)
        self.ent_genre.delete(0, tk.END)
        self.cbo_status.set("Unread")
        self.cbo_rating.set("Unrated")
        self.txt_notes.delete("1.0", tk.END)
        self.update_status("Ready to add a new book.")

    def save_book_details(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Title is required!")
            return
            
        book_data = {
            "title": title,
            "author": self.ent_author.get().strip(),
            "isbn": self.ent_isbn.get().strip() if hasattr(self, 'ent_isbn') else "",
            "genre": self.ent_genre.get().strip(),
            "status": self.cbo_status.get(),
            "rating": self.cbo_rating.get(),
            "notes": self.txt_notes.get("1.0", tk.END).strip()
        }
        
        if self.cur_id: # Update
            for b in self.books:
                if b["id"] == self.cur_id:
                    b.update(book_data)
                    break
            self.update_status(f"Updated book: {title}")
        else: # Add new
            book_data["id"] = str(uuid.uuid4())
            book_data["added_on"] = datetime.now().strftime("%Y-%m-%d")
            self.books.append(book_data)
            self.cur_id = book_data["id"]
            self.update_status(f"Added new book: {title}")
            
        self.save_data()
        self.refresh_list()
        
        # re-select
        for item in self.tree.get_children():
            if item == self.cur_id:
                self.tree.selection_set(item)
                self.tree.see(item)
                break

    def delete_book(self):
        if not self.cur_id:
            messagebox.showwarning("Warning", "Select a book to delete.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            self.books = [b for b in self.books if b["id"] != self.cur_id]
            self.save_data()
            self.clear_details()
            self.refresh_list()
            self.update_status("Book deleted.")

    def fetch_metadata(self, query_type="title"):
        if query_type == "title":
            query = self.ent_title.get().strip()
            if not query:
                messagebox.showwarning("Warning", "Enter a title to fetch metadata.")
                return
            self.update_status("Fetching catalog details by Title...")
            url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(query)}&limit=1"
        else: # isbn
            query = self.ent_isbn.get().strip()
            if not query:
                messagebox.showwarning("Warning", "Enter an ISBN to fetch metadata.")
                return
            # Clean ISBN
            query = re.sub(r'[^0-9X]', '', query.upper())
            self.update_status(f"Fetching catalog details for ISBN: {query}...")
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data"
            
        self.root.update()
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if query_type == "title" and data.get("docs"):
                    doc = data["docs"][0]
                    author = doc.get("author_name", [""])[0]
                    subjects = doc.get("subject", [])
                    genre = ", ".join(subjects[:3]) if subjects else ""
                    isbn_list = doc.get("isbn", [])
                    isbn = isbn_list[0] if isbn_list else ""
                    
                    if not self.ent_author.get() and author: self.ent_author.insert(0, author)
                    if not self.ent_genre.get() and genre: self.ent_genre.insert(0, genre)
                    if hasattr(self, "ent_isbn") and not self.ent_isbn.get() and isbn: 
                        self.ent_isbn.insert(0, isbn)
                    self.update_status("Catalog details fetched successfully!")
                    
                elif query_type == "isbn" and data:
                    key = f"ISBN:{query}"
                    if key in data:
                        book_data = data[key]
                        title = book_data.get("title", "")
                        authors = book_data.get("authors", [])
                        author = authors[0]["name"] if authors else ""
                        subjects = book_data.get("subjects", [])
                        genre = ", ".join([s["name"] for s in subjects[:3]]) if subjects else ""
                        
                        if not self.ent_title.get() and title: self.ent_title.insert(0, title)
                        if not self.ent_author.get() and author: self.ent_author.insert(0, author)
                        if not self.ent_genre.get() and genre: self.ent_genre.insert(0, genre)
                        self.update_status("Catalog details fetched successfully!")
                    else:
                        self.update_status("ISBN not found in OpenLibrary.")
                else:
                    self.update_status("No catalog details found.")
        except Exception as e:
            self.update_status(f"Failed to fetch metadata: {e}")
            messagebox.showerror("Error", f"Failed to fetch catalog details: {e}")

    def handle_drop(self, event):
        data = event.data
        if not data: return
        
        files = self.root.tk.splitlist(data)
        for f in files:
            if os.path.isfile(f):
                ext = os.path.splitext(f)[1].lower()
                if ext == '.csv':
                    self.import_csv_file(f)
                else:
                    self.update_status(f"Unsupported file type for drop: {ext}")
            else:
                text = f.strip()
                clean_text = re.sub(r'[^0-9X]', '', text.upper())
                if len(clean_text) in [10, 13]:
                    self.clear_details()
                    self.ent_isbn.insert(0, clean_text)
                    self.fetch_metadata(query_type="isbn")
                else:
                    self.clear_details()
                    self.ent_title.insert(0, text)
                    self.fetch_metadata(query_type="title")

    def import_csv_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    title = row.get("title", "").strip()
                    if title:
                        new_book = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "author": row.get("author", ""),
                            "isbn": row.get("isbn", ""),
                            "genre": row.get("genre", ""),
                            "status": row.get("status", "Unread"),
                            "rating": row.get("rating", "Unrated"),
                            "notes": row.get("notes", ""),
                            "added_on": datetime.now().strftime("%Y-%m-%d")
                        }
                        self.books.append(new_book)
                        count += 1
            self.save_data()
            self.refresh_list()
            self.update_status(f"Imported {count} books from CSV.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.on_tree_select(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def import_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.import_csv_file(filepath)

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["title", "author", "isbn", "genre", "status", "rating", "notes", "added_on"])
                    for b in self.books:
                        writer.writerow([
                            b.get("title", ""), b.get("author", ""), b.get("isbn", ""), b.get("genre", ""), 
                            b.get("status", ""), b.get("rating", ""), b.get("notes", ""), b.get("added_on", "")
                        ])
                self.update_status("Exported to CSV successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {e}")

    def show_statistics(self):
        total = len(self.books)
        unread = sum(1 for b in self.books if b.get("status") == "Unread")
        reading = sum(1 for b in self.books if b.get("status") == "Reading")
        completed = sum(1 for b in self.books if b.get("status") == "Completed")
        
        stats = f"Total Books: {total}\n\nUnread: {unread}\nReading: {reading}\nCompleted: {completed}"
        messagebox.showinfo("Library Statistics", stats)

    def show_settings(self):
        loc = simpledialog.askstring("Settings", "Enter manual location (Leave empty for Auto IP detection):", 
                                     initialvalue=self.settings.get("manual_loc", ""))
        if loc is not None:
            self.settings["manual_loc"] = loc
            self.settings["location"] = "manual" if loc.strip() else "auto"
            self.save_data()
            self.update_status("Settings updated.")

    def show_about(self):
        messagebox.showinfo("About", "Book Wishlist Manager Professional\nVersion 2.0\nCreated with Python and Tkinter.")

    def apply_theme(self, theme_name):
        self.settings["theme"] = theme_name
        self.save_data()
        
        style = ttk.Style()
        if theme_name == "dark":
            self.root.configure(bg="#2d2d2d")
            style.theme_use('clam')
            style.configure(".", background="#2d2d2d", foreground="white", fieldbackground="#3d3d3d")
            style.configure("Treeview", background="#3d3d3d", foreground="white", fieldbackground="#3d3d3d")
            style.map("Treeview", background=[("selected", "#0078D7")])
            style.configure("TButton", background="#444", foreground="white")
        elif theme_name == "light":
            self.root.configure(bg="white")
            style.theme_use('clam')
            style.configure(".", background="white", foreground="black", fieldbackground="white")
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            style.map("Treeview", background=[("selected", "#0078D7")])
        else: # Default
            style.theme_use('default')
            
        self.update_status(f"Applied {theme_name} theme.")

    def update_status(self, msg):
        self.status_label.config(text=msg)

    def setup_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.clear_details())
        self.root.bind("<Control-s>", lambda e: self.save_book_details())
        self.root.bind("<Delete>", lambda e: self.delete_book())
        self.root.bind("<Control-d>", lambda e: self.delete_book())
        self.root.bind("<Control-m>", lambda e: self.fetch_metadata("title"))
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-i>", lambda e: self.import_csv())
        self.root.bind("<Control-e>", lambda e: self.export_csv())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-t>", lambda e: self.show_statistics())
        
        self.root.bind("<Alt-s>", lambda e: self.open_link("shopping"))
        self.root.bind("<Alt-a>", lambda e: self.open_link("amazon"))
        self.root.bind("<Alt-g>", lambda e: self.open_link("goodreads"))
        self.root.bind("<Alt-l>", lambda e: self.open_link("libraries"))
        self.root.bind("<Alt-b>", lambda e: self.open_link("bookstores"))
        self.root.bind("<Alt-w>", lambda e: self.open_link("worldcat"))
        self.root.bind("<F1>", lambda e: self.show_shortcuts())

    def focus_search(self):
        self.ent_search.focus_set()

    def show_shortcuts(self):
        shortcuts = (
            "Keyboard Shortcuts:\n\n"
            "Ctrl+N : Add New Book\n"
            "Ctrl+S : Save Changes\n"
            "Del / Ctrl+D : Delete Selected\n"
            "Ctrl+F : Focus Search\n"
            "Ctrl+M : Fetch Metadata\n"
            "Ctrl+I : Import CSV\n"
            "Ctrl+E : Export CSV\n"
            "Ctrl+T : View Statistics\n"
            "Ctrl+Q : Exit\n"
            "\nExternal Search Links:\n"
            "Alt+S : Buy on Google Shopping\n"
            "Alt+A : Buy on Amazon\n"
            "Alt+G : View on Goodreads\n"
            "Alt+L : Nearby Libraries\n"
            "Alt+B : Nearby Bookstores\n"
            "Alt+W : Search WorldCat\n"
            "\nF1 : Show This Help\n"
        )
        messagebox.showinfo("Shortcuts Help", shortcuts)

    # --- External Web Actions ---
    def open_link(self, action_type):
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        
        if not title:
            messagebox.showwarning("Warning", "Title is required for external search.")
            return
            
        if self.search_title_only_var.get():
            query_str = title
        else:
            query_str = f"{title} {author}".strip()
            
        query = urllib.parse.quote(query_str)
        
        if action_type == "shopping":
            url = f"https://www.google.com/search?tbm=shop&q={query}"
        elif action_type == "amazon":
            url = f"https://www.amazon.com/s?k={query}"
        elif action_type == "goodreads":
            url = f"https://www.goodreads.com/search?q={query}"
        elif action_type == "worldcat":
            url = f"https://www.worldcat.org/search?q={query}"
        elif action_type in ["libraries", "bookstores"]:
            # Handle Location
            loc = self.settings.get("manual_loc", "").strip()
            if not loc:
                try:
                    req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=3) as response:
                        data = json.loads(response.read().decode())
                        if data["status"] == "success":
                            loc = f"{data['city']}, {data['regionName']}"
                except:
                    loc = ""
            
            if self.search_title_only_var.get() or not author:
                book_str = title
            else:
                book_str = f"{title} by {author}"
                
            if loc:
                search_str = f"{action_type} near {loc} having {book_str}"
            else:
                search_str = f"{action_type} near me having {book_str}"
                
            search_query = urllib.parse.quote(search_str)
            url = f"https://www.google.com/search?q={search_query}"
            
        webbrowser.open(url)

if __name__ == "__main__":
    if DND_SUPPORTED:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        print("Note: tkinterdnd2 not installed. Drag and drop is disabled.")
        
    app = BookWishlistProApp(root)
    
    if DND_SUPPORTED:
        root.drop_target_register(DND_FILES, DND_TEXT)
        root.dnd_bind('<<Drop>>', app.handle_drop)
        
    root.mainloop()
