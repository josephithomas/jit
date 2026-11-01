# -*- coding: utf-8 -*-
"""
Titus II Teachers College - TSTC_Professional PDF Suite v5.0 (Adobe Acrobat Studio Edition)
Studio GUI Frames Mixin:
1. PDF Spaces (Intelligent Workspaces Hub, Universal Ingestion, Dashboard, Audio Briefing)
2. Advanced Acrobat AI Assistant (Multi-File Cross-Mining, Clickable Citations, Custom Personas)
3. Adobe Express Premium Studio (Slide Decks, Infographics, Dossiers & Brand Kits)
4. Acrobat Sign (Electronic Signatures, SHA-256 Stamp & Audit Certificates)
5. Version Control Comparison (Side-by-Side Visual Diff & Change Logs)
6. Advanced Legal Redaction (Regex Sanitisation, Pixel Burnout & Metadata Scrub)
7. Enterprise Admin & Audit Console (Role Management & Tamper-Evident Trail)
Developed by Dr. Joseph I Thomas
"""

import os
import sys
import re
import json
import time
import uuid
import datetime
import threading
import webbrowser
from typing import List, Dict, Any, Tuple, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk

import fitz  # PyMuPDF
from studio_engines import (
    PDFSpaceEngine,
    AcrobatAIEngine,
    ExpressStudioEngine,
    AcrobatProEngine,
    AuditLogger
)

# Styling Constants
PRIMARY_COLOR = "#6D28D9"      # Royal Purple
PRIMARY_HOVER = "#5B21B6"
SECONDARY_COLOR = "#0F172A"    # Deep Navy
ACCENT_GREEN = "#10B981"       # Emerald
ACCENT_GREEN_HOVER = "#059669"
BG_DARK = "#1E293B"
BG_CARD = "#334155"
TEXT_LIGHT = "#F8FAFC"
ACCENT_AMBER = "#F59E0B"


class StudioFramesMixin:
    """Mixin containing all Adobe Acrobat Studio GUI Frames and workflows."""

    # ==========================================================================
    # 1. PDF SPACES (INTELLIGENT WORKSPACES HUB)
    # ==========================================================================
    def frame_pdf_spaces(self, parent) -> ctk.CTkFrame:
        """PDF Spaces — Collaborative Multi-File Knowledge Hub & Universal Ingestion."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View Workspace", getattr(self, "active_space_name", "Default Space"), "Accessed PDF Spaces Hub")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        if not hasattr(self, "space_documents"):
            self.space_documents = []
        if not hasattr(self, "active_space_name"):
            self.active_space_name = "Institutional Curriculum & Policy Space"
        if not hasattr(self, "space_role"):
            self.space_role = "Contributor"
        if not hasattr(self, "space_dashboard_data"):
            self.space_dashboard_data = {}
        if not hasattr(self, "audio_narration_stopped"):
            self.audio_narration_stopped = [False]

        # Top Control Bar
        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        r1 = ctk.CTkFrame(top_bar, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            r1,
            text=f"🌐 PDF Spaces Hub: {self.active_space_name}",
            font=("Arial", 16, "bold"),
            text_color=ACCENT_AMBER
        ).pack(side="left")

        # Role Selector Tag
        role_frame = ctk.CTkFrame(r1, fg_color="transparent")
        role_frame.pack(side="right")
        ctk.CTkLabel(role_frame, text="Active Role:", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 4))

        def on_role_change(choice: str):
            self.space_role = choice
            AuditLogger.log_event(self.space_role, "Role Changed", self.active_space_name, f"Switched role to {choice}")
            messagebox.showinfo("Role Updated", f"Workspace permission set to: {choice}")

        opt_role = ctk.CTkOptionMenu(role_frame, values=["Contributor (Full)", "Reviewer (Chat Only)", "Read-Only (View Only)"], width=170, command=on_role_change)
        opt_role.set("Contributor (Full)")
        opt_role.pack(side="left", padx=4)

        # Action Buttons Row
        r2 = ctk.CTkFrame(top_bar, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 8))

        def add_files_dialog():
            if self.space_role == "Read-Only (View Only)":
                return messagebox.showwarning("Permission Denied", "Read-Only role cannot add documents to Space.")
            file_paths = filedialog.askopenfilenames(
                title="Universal Document Ingestion (Select up to 100 files)",
                filetypes=[
                    ("All Supported Files", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.csv;*.pptx;*.txt;*.md;*.srt;*.vtt"),
                    ("PDF Documents", "*.pdf"),
                    ("Word Documents", "*.docx;*.doc"),
                    ("Excel Spreadsheets", "*.xlsx;*.xls;*.csv"),
                    ("PowerPoint Decks", "*.pptx"),
                    ("Transcripts & Text", "*.txt;*.md;*.srt;*.vtt")
                ]
            )
            if file_paths:
                def worker():
                    added = 0
                    for fp in file_paths:
                        try:
                            doc_data = PDFSpaceEngine.parse_universal_file(fp)
                            self.space_documents.append(doc_data)
                            added += 1
                        except Exception as ex:
                            print(f"Error parsing {fp}: {ex}")
                    self.space_dashboard_data = PDFSpaceEngine.generate_smart_dashboard(self.active_space_name, self.space_documents)
                    AuditLogger.log_event(self.space_role, "Ingest Files", self.active_space_name, f"Added {added} files")

                self.run_async_task(worker, on_complete=lambda _: refresh_views(), status_msg=f"Ingesting {len(file_paths)} documents...")

        def add_url_dialog():
            if self.space_role == "Read-Only (View Only)":
                return messagebox.showwarning("Permission Denied", "Read-Only role cannot add URLs to Space.")
            dlg = ctk.CTkInputDialog(text="Enter live webpage URL to ingest into PDF Space:", title="Live URL Ingestion")
            target_url = dlg.get_input()
            if target_url and target_url.strip().startswith("http"):
                def worker():
                    doc_data = PDFSpaceEngine.parse_live_url(target_url.strip())
                    self.space_documents.append(doc_data)
                    self.space_dashboard_data = PDFSpaceEngine.generate_smart_dashboard(self.active_space_name, self.space_documents)
                    AuditLogger.log_event(self.space_role, "Ingest URL", target_url.strip(), "Added live web resource")

                self.run_async_task(worker, on_complete=lambda _: refresh_views(), status_msg="Fetching and indexing live URL...")

        def save_space_project():
            p = filedialog.asksaveasfilename(defaultextension=".pdfspace", filetypes=[("PDF Space Project", "*.pdfspace"), ("JSON File", "*.json")])
            if p:
                state = {
                    "space_name": self.active_space_name,
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "documents": self.space_documents,
                    "dashboard": self.space_dashboard_data
                }
                with open(p, "w", encoding="utf-8") as f_out:
                    json.dump(state, f_out, indent=2)
                AuditLogger.log_event(self.space_role, "Save Space", self.active_space_name, f"Exported project to {os.path.basename(p)}")
                messagebox.showinfo("Space Saved", f"PDF Space project saved successfully to:\n{p}")

        def load_space_project():
            p = filedialog.askopenfilename(filetypes=[("PDF Space Project", "*.pdfspace;*.json")])
            if p:
                with open(p, "r", encoding="utf-8") as f_in:
                    state = json.load(f_in)
                self.active_space_name = state.get("space_name", "Loaded Space")
                self.space_documents = state.get("documents", [])
                self.space_dashboard_data = state.get("dashboard", {})
                if not self.space_dashboard_data and self.space_documents:
                    self.space_dashboard_data = PDFSpaceEngine.generate_smart_dashboard(self.active_space_name, self.space_documents)
                refresh_views()
                messagebox.showinfo("Space Loaded", f"Loaded Space '{self.active_space_name}' with {len(self.space_documents)} documents!")

        def export_dossier_html():
            if not self.space_documents:
                return messagebox.showwarning("Empty Space", "Please add documents to the Space before exporting a dossier.")
            p = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("Interactive HTML Dossier", "*.html")])
            if p:
                PDFSpaceEngine.export_space_dossier_html(self.active_space_name, self.space_dashboard_data, self.space_documents, p)
                AuditLogger.log_event(self.space_role, "Export HTML Dossier", self.active_space_name, f"Exported to {p}")
                if messagebox.askyesno("Exported", f"Interactive HTML Dossier generated!\nOpen in web browser now?"):
                    webbrowser.open(f"file:///{os.path.abspath(p)}")

        def export_dossier_pdf():
            if not self.space_documents:
                return messagebox.showwarning("Empty Space", "Please add documents to the Space before exporting a dossier.")
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Intelligence Dossier", "*.pdf")])
            if p:
                PDFSpaceEngine.export_space_dossier_pdf(self.active_space_name, self.space_dashboard_data, self.space_documents, p)
                AuditLogger.log_event(self.space_role, "Export PDF Dossier", self.active_space_name, f"Exported to {p}")
                messagebox.showinfo("Exported", f"Publication-quality PDF Space Dossier generated at:\n{p}")

        ctk.CTkButton(r2, text="➕ Add Files (Up to 100)", command=add_files_dialog, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, width=150, height=28, font=("Arial", 11, "bold")).pack(side="left", padx=3)
        ctk.CTkButton(r2, text="🌐 Ingest URL", command=add_url_dialog, fg_color="#0284C7", width=110, height=28, font=("Arial", 11, "bold")).pack(side="left", padx=3)
        ctk.CTkButton(r2, text="💾 Save Space", command=save_space_project, fg_color="gray30", width=100, height=28).pack(side="left", padx=3)
        ctk.CTkButton(r2, text="📂 Open Space", command=load_space_project, fg_color="gray30", width=100, height=28).pack(side="left", padx=3)
        ctk.CTkButton(r2, text="📄 Export PDF Dossier", command=export_dossier_pdf, fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER, width=140, height=28, font=("Arial", 11, "bold")).pack(side="right", padx=3)
        ctk.CTkButton(r2, text="🌐 Export HTML Dossier", command=export_dossier_html, fg_color="gray35", width=140, height=28).pack(side="right", padx=3)

        # Tabview for Dashboard / Document Inventory / Audio Narration
        tabview = ctk.CTkTabview(f, fg_color=BG_DARK)
        tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        tab_dash = tabview.add("📊 Smart Insight Dashboard")
        tab_repo = tabview.add("📁 Multi-File Repository Hub")
        tab_audio = tabview.add("🎙️ Executive Audio Briefing")

        # --- TAB 1: SMART DASHBOARD ---
        tab_dash.grid_columnconfigure(0, weight=1)
        tab_dash.grid_rowconfigure(1, weight=1)

        dash_scroll = ctk.CTkScrollableFrame(tab_dash, fg_color="transparent")
        dash_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Stats Cards Container
        stats_frame = ctk.CTkFrame(dash_scroll, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10))

        lbl_stat_docs = ctk.CTkLabel(stats_frame, text="0", font=("Arial", 22, "bold"), text_color=ACCENT_AMBER)
        lbl_stat_pages = ctk.CTkLabel(stats_frame, text="0", font=("Arial", 22, "bold"), text_color=ACCENT_GREEN)
        lbl_stat_words = ctk.CTkLabel(stats_frame, text="0", font=("Arial", 22, "bold"), text_color="#38BDF8")

        for idx, (lbl_widget, title) in enumerate([(lbl_stat_docs, "Documents"), (lbl_stat_pages, "Indexed Pages"), (lbl_stat_words, "Total Words")]):
            c = ctk.CTkFrame(stats_frame, fg_color=BG_CARD, corner_radius=8, width=180, height=75)
            c.pack(side="left", padx=6, fill="both", expand=True)
            c.pack_propagate(False)
            lbl_widget.master = c
            lbl_widget.pack(pady=(10, 0))
            ctk.CTkLabel(c, text=title, font=("Arial", 11, "bold"), text_color="gray70").pack()

        # Synthesis Box
        synth_card = ctk.CTkFrame(dash_scroll, fg_color=BG_CARD, corner_radius=8)
        synth_card.pack(fill="x", pady=8, padx=4)
        ctk.CTkLabel(synth_card, text="📊 Executive Collective Synthesis", font=("Arial", 13, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=12, pady=(10, 4))

        txt_synthesis = ctk.CTkTextbox(synth_card, height=140, font=("Segoe UI", 11), wrap="word", fg_color="gray15")
        txt_synthesis.pack(fill="x", padx=12, pady=(0, 12))

        # Takeaways Box
        takeaways_card = ctk.CTkFrame(dash_scroll, fg_color=BG_CARD, corner_radius=8)
        takeaways_card.pack(fill="x", pady=8, padx=4)
        ctk.CTkLabel(takeaways_card, text="🎯 Key Strategic Takeaways", font=("Arial", 13, "bold"), text_color=ACCENT_GREEN).pack(anchor="w", padx=12, pady=(10, 4))
        takeaways_container = ctk.CTkFrame(takeaways_card, fg_color="transparent")
        takeaways_container.pack(fill="x", padx=12, pady=(0, 10))

        # Roadmap Box
        action_card = ctk.CTkFrame(dash_scroll, fg_color=BG_CARD, corner_radius=8)
        action_card.pack(fill="x", pady=8, padx=4)
        ctk.CTkLabel(action_card, text="🚀 Predictive Action Goals & Checklist", font=("Arial", 13, "bold"), text_color="#38BDF8").pack(anchor="w", padx=12, pady=(10, 4))
        action_container = ctk.CTkFrame(action_card, fg_color="transparent")
        action_container.pack(fill="x", padx=12, pady=(0, 10))

        # --- TAB 2: MULTI-FILE REPOSITORY HUB ---
        tab_repo.grid_columnconfigure(0, weight=1)
        tab_repo.grid_rowconfigure(0, weight=1)

        repo_scroll = ctk.CTkScrollableFrame(tab_repo, fg_color="transparent")
        repo_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # --- TAB 3: AUDIO BRIEFING NARRATION ---
        tab_audio.grid_columnconfigure(0, weight=1)
        tab_audio.grid_rowconfigure(1, weight=1)

        audio_top = ctk.CTkFrame(tab_audio, fg_color="transparent")
        audio_top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(audio_top, text="🎙️ Automated Executive Audio Overview (2-Speaker Script & SAPI Playback)", font=("Arial", 13, "bold"), text_color=ACCENT_AMBER).pack(side="left")

        def play_audio():
            self.audio_narration_stopped[0] = False
            script_text = txt_audio_script.get("1.0", "end").strip()
            if not script_text:
                return messagebox.showwarning("Empty Script", "Audio script is empty. Please generate dashboard first.")
            threading.Thread(target=lambda: PDFSpaceEngine.play_audio_narration(script_text, self.audio_narration_stopped), daemon=True).start()
            messagebox.showinfo("Audio Playing", "Audio narration started! You can continue working in the suite.")

        def stop_audio():
            self.audio_narration_stopped[0] = True
            messagebox.showinfo("Audio Stopped", "Voice narration stopped.")

        def export_audio_script():
            p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Script", "*.txt"), ("Markdown", "*.md")])
            if p:
                with open(p, "w", encoding="utf-8") as f_out:
                    f_out.write(txt_audio_script.get("1.0", "end"))
                messagebox.showinfo("Saved", f"Audio briefing script saved to:\n{p}")

        ctk.CTkButton(audio_top, text="▶️ Play Audio (TTS)", command=play_audio, fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER, width=130).pack(side="right", padx=4)
        ctk.CTkButton(audio_top, text="⏹️ Stop", command=stop_audio, fg_color="crimson", width=80).pack(side="right", padx=4)
        ctk.CTkButton(audio_top, text="💾 Export Script", command=export_audio_script, fg_color="gray30", width=110).pack(side="right", padx=4)

        txt_audio_script = ctk.CTkTextbox(tab_audio, font=("Segoe UI", 11), wrap="word", fg_color="gray15")
        txt_audio_script.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def refresh_views():
            if not self.space_dashboard_data and self.space_documents:
                self.space_dashboard_data = PDFSpaceEngine.generate_smart_dashboard(self.active_space_name, self.space_documents)

            # Update Stats
            d_data = self.space_dashboard_data
            lbl_stat_docs.configure(text=str(d_data.get("total_docs", len(self.space_documents))))
            lbl_stat_pages.configure(text=str(d_data.get("total_pages", sum(d.get("page_count", 0) for d in self.space_documents))))
            lbl_stat_words.configure(text=f"{d_data.get('total_words', sum(d.get('word_count', 0) for d in self.space_documents)):,}")

            # Update Synthesis
            txt_synthesis.delete("1.0", "end")
            txt_synthesis.insert("1.0", d_data.get("executive_synthesis", "No summary generated."))

            # Update Takeaways
            for w in takeaways_container.winfo_children():
                w.destroy()
            for t in d_data.get("key_takeaways", []):
                r = ctk.CTkFrame(takeaways_container, fg_color="transparent")
                r.pack(fill="x", pady=2)
                ctk.CTkLabel(r, text="✓", font=("Arial", 12, "bold"), text_color=ACCENT_GREEN).pack(side="left", padx=(0, 6))
                ctk.CTkLabel(r, text=t, font=("Segoe UI", 11), text_color=TEXT_LIGHT, justify="left", wraplength=650).pack(side="left", fill="x", expand=True)

            # Update Action Checklist
            for w in action_container.winfo_children():
                w.destroy()
            for a in d_data.get("action_goals", []):
                chk = ctk.CTkCheckBox(action_container, text=a, font=("Segoe UI", 11), text_color=TEXT_LIGHT)
                chk.pack(anchor="w", pady=3)

            # Update Repo List
            for w in repo_scroll.winfo_children():
                w.destroy()

            if not self.space_documents:
                ctk.CTkLabel(repo_scroll, text="No documents in this Space yet. Click '➕ Add Files' to load up to 100 files.", font=("Arial", 12, "italic"), text_color="gray60").pack(pady=40)
            else:
                for idx, doc in enumerate(self.space_documents):
                    card = ctk.CTkFrame(repo_scroll, fg_color=BG_CARD, corner_radius=6)
                    card.pack(fill="x", pady=4, padx=4)

                    c_head = ctk.CTkFrame(card, fg_color="transparent")
                    c_head.pack(fill="x", padx=10, pady=8)

                    ctk.CTkLabel(c_head, text=f"📄 {doc.get('name', 'File')}", font=("Arial", 12, "bold"), text_color=TEXT_LIGHT).pack(side="left")

                    fmt = doc.get("format", "PDF")
                    fmt_color = "#6D28D9" if fmt=="PDF" else ("#2563EB" if fmt in ["DOCX","DOC"] else ("#059669" if fmt in ["XLSX","CSV"] else "#0284C7"))
                    ctk.CTkLabel(c_head, text=f" {fmt} ", font=("Arial", 10, "bold"), fg_color=fmt_color, corner_radius=4, text_color="#FFFFFF").pack(side="left", padx=8)

                    ctk.CTkLabel(c_head, text=f"Pages: {doc.get('page_count', 1)} | Words: {doc.get('word_count', 0):,} | Size: {doc.get('size_kb', 0)} KB", font=("Segoe UI", 10), text_color="gray70").pack(side="left", padx=8)

                    def remove_doc(target_id=doc.get("id")):
                        self.space_documents = [d for d in self.space_documents if d.get("id") != target_id]
                        self.space_dashboard_data = PDFSpaceEngine.generate_smart_dashboard(self.active_space_name, self.space_documents)
                        refresh_views()

                    def open_in_viewer(target_path=doc.get("path")):
                        if target_path and target_path.lower().endswith(".pdf") and os.path.exists(target_path):
                            self.load_pdf_document(target_path)
                            messagebox.showinfo("Document Loaded", f"Loaded '{os.path.basename(target_path)}' into Master PDF Canvas!")
                        else:
                            messagebox.showinfo("Document Info", f"Resource path:\n{target_path}\nExtracted text is actively indexed in PDF Space.")

                    ctk.CTkButton(c_head, text="🗑️ Remove", width=75, height=24, fg_color="crimson", font=("Arial", 10), command=remove_doc).pack(side="right", padx=2)
                    ctk.CTkButton(c_head, text="👁️ Open", width=65, height=24, fg_color=PRIMARY_COLOR, font=("Arial", 10), command=open_in_viewer).pack(side="right", padx=2)

            # Update Audio Script
            txt_audio_script.delete("1.0", "end")
            txt_audio_script.insert("1.0", PDFSpaceEngine.generate_audio_briefing_script(self.active_space_name, d_data))

        refresh_views()
        return f

    # ==========================================================================
    # 2. ADVANCED ACROBAT AI ASSISTANT & PERSONAS
    # ==========================================================================
    def frame_acrobat_ai(self, parent) -> ctk.CTkFrame:
        """Advanced Acrobat AI Assistant — Cross-File Deep Mining & Custom Personas."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View AI Assistant", "Cross-File AI", "Opened Advanced Acrobat AI")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(2, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # Top Control Bar
        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        r1 = ctk.CTkFrame(top_bar, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(r1, text="🤖 Advanced Acrobat AI Assistant | Multi-File Mining", font=("Arial", 16, "bold"), text_color=ACCENT_AMBER).pack(side="left")

        # Privacy Firewall Badge
        ctk.CTkLabel(
            r1,
            text=" 🔒 Enterprise Privacy Firewall Active (Zero Retention) ",
            font=("Arial", 10, "bold"),
            fg_color="#065F46",
            text_color="#34D399",
            corner_radius=6
        ).pack(side="right")

        # Persona & Knowledge Base Selector Row
        r2 = ctk.CTkFrame(top_bar, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(r2, text="AI Persona:", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 4))
        personas_list = list(AcrobatAIEngine.PERSONAS.keys())
        opt_persona = ctk.CTkOptionMenu(r2, values=personas_list, width=280)
        opt_persona.pack(side="left", padx=4)

        def connect_folder_kb():
            d = filedialog.askdirectory(title="Select Enterprise Knowledge Base Document Archive")
            if d:
                def worker():
                    added = 0
                    for root, _, files in os.walk(d):
                        for file in files:
                            ext = os.path.splitext(file)[1].lower()
                            if ext in [".pdf", ".docx", ".xlsx", ".txt", ".pptx"]:
                                full_p = os.path.join(root, file)
                                try:
                                    doc_data = PDFSpaceEngine.parse_universal_file(full_p)
                                    self.space_documents.append(doc_data)
                                    added += 1
                                except Exception:
                                    pass
                    self.space_dashboard_data = PDFSpaceEngine.generate_smart_dashboard(self.active_space_name, self.space_documents)
                    AuditLogger.log_event(self.space_role, "Connect Archive", os.path.basename(d), f"Indexed {added} archive files")

                self.run_async_task(worker, on_complete=lambda _: messagebox.showinfo("Knowledge Base Connected", f"Successfully indexed enterprise folder with multi-file cross-mining!"), status_msg="Indexing enterprise document archive...")

        ctk.CTkButton(r2, text="🏢 Connect Enterprise Folder KB", command=connect_folder_kb, fg_color="gray30", hover_color=PRIMARY_COLOR, width=210, height=28).pack(side="left", padx=8)

        # Quick Actions Bar
        actions_bar = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=6)
        actions_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=2)

        def run_preset_query(p_text: str):
            ent_query.delete(0, "end")
            ent_query.insert(0, p_text)
            execute_query()

        ctk.CTkButton(actions_bar, text="⚖️ Cross-Audit Liabilities", command=lambda: run_preset_query("Scrutinize all documents for contractual liabilities, compliance risks, and obligations."), fg_color="gray25", hover_color=PRIMARY_COLOR, height=26).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(actions_bar, text="🔍 Discrepancy Finder", command=lambda: run_preset_query("Cross-reference all loaded documents to find conflicting terms, data discrepancies, or timeline variations."), fg_color="gray25", hover_color=PRIMARY_COLOR, height=26).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(actions_bar, text="📊 Multi-Doc Executive Synthesis", command=lambda: run_preset_query("Provide a structured cross-file executive briefing with citations [Doc: filename, Page: X]."), fg_color="gray25", hover_color=PRIMARY_COLOR, height=26).pack(side="left", padx=3, pady=3)

        # Chat Conversation Stream
        chat_scroll = ctk.CTkScrollableFrame(f, fg_color="gray15", corner_radius=8)
        chat_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # Input Row
        input_bar = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=8)
        input_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        ent_query = ctk.CTkEntry(input_bar, placeholder_text="Ask across all documents in this Space (e.g., 'Compare curriculum policies and cite source pages')...", height=38, font=("Segoe UI", 12))
        ent_query.pack(side="left", fill="x", expand=True, padx=8, pady=6)

        def execute_query():
            q = ent_query.get().strip()
            if not q:
                return
            ent_query.delete(0, "end")

            # Append User Bubble
            user_frame = ctk.CTkFrame(chat_scroll, fg_color="#5B21B6", border_width=1, border_color="#7C3AED", corner_radius=8)
            user_frame.pack(anchor="e", pady=6, padx=(60, 10))
            ctk.CTkLabel(user_frame, text="👤 You (Space Query)", font=("Arial", 10, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=10, pady=(6, 2))
            ctk.CTkLabel(user_frame, text=q, font=("Segoe UI", 11), text_color="#FFFFFF", wraplength=480, justify="left").pack(padx=10, pady=(0, 8))

            selected_persona = opt_persona.get()

            def worker():
                # If no space documents, try creating virtual document from master PDF
                docs_to_query = list(getattr(self, "space_documents", []))
                if not docs_to_query and getattr(self, "active_pdf_path", None):
                    docs_to_query = [PDFSpaceEngine.parse_universal_file(self.active_pdf_path)]

                ans, citations = AcrobatAIEngine.query_cross_file_intelligence(docs_to_query, q, selected_persona)
                return ans, citations

            def on_done(result):
                ans_text, citations = result
                ai_frame = ctk.CTkFrame(chat_scroll, fg_color=BG_DARK, border_width=1, border_color="#334155", corner_radius=8)
                ai_frame.pack(anchor="w", pady=6, padx=(10, 60), fill="none")

                ctk.CTkLabel(ai_frame, text=f"🤖 Advanced Acrobat AI ({selected_persona.split()[0]})", font=("Arial", 10, "bold"), text_color=ACCENT_GREEN).pack(anchor="w", padx=10, pady=(6, 2))
                ctk.CTkLabel(ai_frame, text=ans_text, font=("Segoe UI", 11), text_color="#FFFFFF", wraplength=520, justify="left").pack(padx=10, pady=(2, 6))

                # Click-Through Footnotes Bar
                if citations:
                    cit_box = ctk.CTkFrame(ai_frame, fg_color="transparent")
                    cit_box.pack(anchor="w", padx=8, pady=(0, 8))
                    ctk.CTkLabel(cit_box, text="Source Footnotes (Click to Jump):", font=("Arial", 9, "italic"), text_color="gray70").pack(side="left", padx=(0, 4))

                    for c in citations[:6]:
                        d_name = c["doc_name"]
                        d_path = c["doc_path"]
                        p_num = c["page"]

                        def jump_to_citation(path=d_path, page=p_num):
                            if path and os.path.exists(path) and path.lower().endswith(".pdf"):
                                if getattr(self, "active_pdf_path", None) != path:
                                    self.load_pdf_document(path)
                                self.jump_to_page(page - 1)
                                messagebox.showinfo("Citation Jump", f"Navigated to: {os.path.basename(path)} (Page {page})")
                            else:
                                messagebox.showinfo("Source Reference", f"Referenced Document:\n{d_name}\nPage: {page}\nPath: {path}")

                        btn_cit = ctk.CTkButton(
                            cit_box,
                            text=f"📄 {d_name[:16]}.. (P.{p_num})",
                            height=20,
                            font=("Arial", 9, "bold"),
                            fg_color=BG_CARD,
                            hover_color=PRIMARY_COLOR,
                            command=jump_to_citation
                        )
                        btn_cit.pack(side="left", padx=2)

                AuditLogger.log_event(self.space_role, "AI Query", selected_persona, f"Query: {q[:50]}")

            self.run_async_task(worker, on_complete=on_done, status_msg="Mining multi-file repository with AI Persona...")

        ent_query.bind("<Return>", lambda _: execute_query())
        btn_send = ctk.CTkButton(input_bar, text="🚀 Ask AI Assistant", command=execute_query, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, width=140, height=36, font=("Arial", 12, "bold"))
        btn_send.pack(side="right", padx=8, pady=6)

        return f

    # ==========================================================================
    # 3. ADOBE EXPRESS PREMIUM STUDIO
    # ==========================================================================
    def frame_express_studio(self, parent) -> ctk.CTkFrame:
        """Adobe Express Premium — Creative Presentation, Infographic & Design Studio."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View Express Studio", "Express Creative", "Opened Adobe Express Studio")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # Header
        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        ctk.CTkLabel(top_bar, text="🎨 Adobe Express Studio | Presentation Decks & Infographic Cards", font=("Arial", 16, "bold"), text_color=ACCENT_AMBER).pack(side="left", padx=12, pady=10)

        # Split Layout: Left Controls, Right Preview/Export
        body = ctk.CTkFrame(f, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left_p = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=8)
        left_p.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=0)

        ctk.CTkLabel(left_p, text="⚙️ Design Configuration & Content", font=("Arial", 13, "bold"), text_color=TEXT_LIGHT).pack(anchor="w", padx=14, pady=(12, 6))

        # Title Entry
        ctk.CTkLabel(left_p, text="Deck / Report Title:", font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=(6, 2))
        ent_title = ctk.CTkEntry(left_p, width=320)
        ent_title.insert(0, "Institutional Teacher Education Framework 2026")
        ent_title.pack(anchor="w", padx=14, fill="x")

        # Subtitle
        ctk.CTkLabel(left_p, text="Subtitle / Organization:", font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=(6, 2))
        ent_subtitle = ctk.CTkEntry(left_p, width=320)
        ent_subtitle.insert(0, "Titus II Teachers College • Executive Strategic Review")
        ent_subtitle.pack(anchor="w", padx=14, fill="x")

        # Brand Kit Selector
        ctk.CTkLabel(left_p, text="🎨 Brand Kit & Color Palette:", font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=(8, 2))
        opt_brand = ctk.CTkOptionMenu(left_p, values=list(ExpressStudioEngine.BRAND_KITS.keys()))
        opt_brand.pack(anchor="w", padx=14, fill="x")

        # Canvas Preset Selector
        ctk.CTkLabel(left_p, text="📐 Canvas Aspect Ratio & Preset:", font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=(8, 2))
        opt_canvas = ctk.CTkOptionMenu(left_p, values=list(ExpressStudioEngine.CANVAS_PRESETS.keys()))
        opt_canvas.pack(anchor="w", padx=14, fill="x")

        # Source Content Selector
        ctk.CTkLabel(left_p, text="📝 Content Extraction Source:", font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=(8, 2))

        txt_content = ctk.CTkTextbox(left_p, height=160, font=("Segoe UI", 10), wrap="word", fg_color="gray15")
        txt_content.pack(fill="both", expand=True, padx=14, pady=(2, 12))

        def load_active_doc_summary():
            if hasattr(self, "space_dashboard_data") and self.space_dashboard_data.get("executive_synthesis"):
                txt_content.delete("1.0", "end")
                txt_content.insert("1.0", self.space_dashboard_data["executive_synthesis"])
            elif getattr(self, "active_pdf_path", None):
                pages = PDFChatEngine.extract_document_pages(self.active_pdf_path)
                s, _ = PDFChatEngine.query_local_bm25(pages, "executive summary and key objectives")
                txt_content.delete("1.0", "end")
                txt_content.insert("1.0", s)

        ctk.CTkButton(left_p, text="📥 Pull Text from Active PDF / Space", command=load_active_doc_summary, fg_color="gray30", height=26).pack(anchor="w", padx=14, pady=(0, 12))
        load_active_doc_summary()

        # Right Panel: Export Options & Visual Cards
        right_p = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=8)
        right_p.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=0)

        ctk.CTkLabel(right_p, text="🚀 Direct Export & Conversion Studio", font=("Arial", 13, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=14, pady=(12, 10))

        # Presentation Deck Export Card
        c1 = ctk.CTkFrame(right_p, fg_color=BG_CARD, corner_radius=8)
        c1.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(c1, text="📽️ 16:9 Presentation Slide Deck", font=("Arial", 12, "bold"), text_color=TEXT_LIGHT).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(c1, text="Generates a widescreen presentation PDF complete with branded cover, 3-card metric slides, and typography.", font=("Segoe UI", 10), text_color="gray80", justify="left", wraplength=280).pack(anchor="w", padx=10, pady=(0, 8))

        def export_slide_deck():
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Presentation Slide Deck PDF", "*.pdf")])
            if p:
                slides = [
                    {"title": "1. Executive Institutional Vision", "points": [("Strategic Scope", "Unified governance and teacher education benchmarks."), ("Core Metrics", "Attributed data points across all institutional departments."), ("Next Action", "Deploy digital sign-off via Acrobat Sign.")]},
                    {"title": "2. Curriculum Alignment & Pedagogy", "points": [("Bloom's Taxonomy", "Structured cognitive and pedagogical outcomes."), ("Assessment", "Continuous formative and summative rubrics."), ("Verification", "Complete compliance with NCTE guidelines.")]},
                    {"title": "3. Strategic Action Roadmap", "points": [("Milestone 1", "Complete multi-file cross-audit."), ("Milestone 2", "Finalize signed legal briefing package."), ("Milestone 3", "Publish interactive dossier.")]}
                ]
                ExpressStudioEngine.generate_presentation_slide_deck_pdf(ent_title.get(), ent_subtitle.get(), slides, opt_brand.get(), p)
                AuditLogger.log_event(self.space_role, "Export Slide Deck", ent_title.get(), f"Saved to {os.path.basename(p)}")
                messagebox.showinfo("Exported", f"Widescreen Presentation Slide Deck created at:\n{p}")

        ctk.CTkButton(c1, text="📽️ Export Presentation Slides (.pdf)", command=export_slide_deck, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, height=30, font=("Arial", 11, "bold")).pack(fill="x", padx=10, pady=(0, 10))

        # Infographic Card Export
        c2 = ctk.CTkFrame(right_p, fg_color=BG_CARD, corner_radius=8)
        c2.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(c2, text="📊 Visual Infographic Summary Card", font=("Arial", 12, "bold"), text_color=TEXT_LIGHT).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(c2, text="Formats document takeaways into an executive KPI infographic with metric badges.", font=("Segoe UI", 10), text_color="gray80", justify="left", wraplength=280).pack(anchor="w", padx=10, pady=(0, 8))

        def export_infographic():
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Infographic Summary PDF", "*.pdf")])
            if p:
                stats = [("100%", "Compliance"), ("15+", "Disciplines"), ("98.4%", "Pass Ratio"), ("5★", "Accredited")]
                takeaways = [
                    "Standardized institutional curricula across all academic programs.",
                    "Robust cross-file attribution and compliance metrics.",
                    "Active deployment of digital verification and e-signatures."
                ]
                ExpressStudioEngine.generate_infographic_card_pdf(ent_title.get(), stats, takeaways, opt_brand.get(), opt_canvas.get(), p)
                AuditLogger.log_event(self.space_role, "Export Infographic", ent_title.get(), f"Saved to {os.path.basename(p)}")
                messagebox.showinfo("Exported", f"Executive Infographic Card created at:\n{p}")

        ctk.CTkButton(c2, text="📊 Export Infographic Card (.pdf)", command=export_infographic, fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER, height=30, font=("Arial", 11, "bold")).pack(fill="x", padx=10, pady=(0, 10))

        return f

    # ==========================================================================
    # 4. ACROBAT SIGN (E-SIGNATURES & AUDIT CERTIFICATES)
    # ==========================================================================
    def frame_acrobat_sign(self, parent) -> ctk.CTkFrame:
        """Acrobat Sign — Interactive E-Signature Pad, Field Placement & Audit Certificate."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View Acrobat Sign", "E-Signature Studio", "Opened Acrobat Sign")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # Header
        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        ctk.CTkLabel(top_bar, text="✍️ Acrobat Sign | E-Signature Workflows & SHA-256 Audit Trail", font=("Arial", 16, "bold"), text_color=ACCENT_AMBER).pack(side="left", padx=12, pady=10)

        body = ctk.CTkFrame(f, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left Panel: Signature Pad (Drawing & Typing)
        left_p = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=8)
        left_p.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=0)

        ctk.CTkLabel(left_p, text="1. Create Digital Signature", font=("Arial", 13, "bold"), text_color=TEXT_LIGHT).pack(anchor="w", padx=14, pady=(12, 6))

        # Canvas Signature Pad
        sig_canvas = Canvas(left_p, width=380, height=140, bg="#FFFFFF", highlightthickness=1, highlightbackground="#6D28D9")
        sig_canvas.pack(padx=14, pady=4)

        # Drawing state
        draw_points = []
        def on_draw(event):
            x, y = event.x, event.y
            if draw_points:
                x0, y0 = draw_points[-1]
                sig_canvas.create_line(x0, y0, x, y, width=2.5, fill="#0F172A", capstyle="round", smooth=True)
            draw_points.append((x, y))

        def on_release(event):
            draw_points.clear()

        sig_canvas.bind("<B1-Motion>", on_draw)
        sig_canvas.bind("<ButtonRelease-1>", on_release)

        def clear_canvas():
            sig_canvas.delete("all")
            draw_points.clear()

        btn_clear = ctk.CTkButton(left_p, text="🧹 Clear Signature Pad", command=clear_canvas, fg_color="gray30", height=24, width=150)
        btn_clear.pack(anchor="w", padx=14, pady=4)

        # Signer Information
        ctk.CTkLabel(left_p, text="2. Signer Attestation Details", font=("Arial", 13, "bold"), text_color=TEXT_LIGHT).pack(anchor="w", padx=14, pady=(12, 4))

        ctk.CTkLabel(left_p, text="Signer Full Name:", font=("Arial", 10, "bold")).pack(anchor="w", padx=14, pady=(2, 0))
        ent_signer_name = ctk.CTkEntry(left_p)
        ent_signer_name.insert(0, "Dr. Joseph I Thomas")
        ent_signer_name.pack(fill="x", padx=14, pady=2)

        ctk.CTkLabel(left_p, text="Email Address:", font=("Arial", 10, "bold")).pack(anchor="w", padx=14, pady=(2, 0))
        ent_signer_email = ctk.CTkEntry(left_p)
        ent_signer_email.insert(0, "principal@tituscollege.edu")
        ent_signer_email.pack(fill="x", padx=14, pady=2)

        ctk.CTkLabel(left_p, text="Official Title / Capacity:", font=("Arial", 10, "bold")).pack(anchor="w", padx=14, pady=(2, 0))
        ent_signer_title = ctk.CTkEntry(left_p)
        ent_signer_title.insert(0, "Principal & Institutional Director")
        ent_signer_title.pack(fill="x", padx=14, pady=2)

        # Right Panel: Placement & Signing Execution
        right_p = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=8)
        right_p.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=0)

        ctk.CTkLabel(right_p, text="3. Target Placement & Sealing", font=("Arial", 13, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=14, pady=(12, 6))

        doc_name = os.path.basename(self.active_pdf_path) if self.active_pdf_path else "No Master PDF Loaded"
        total_p = len(self.pdf_doc) if self.pdf_doc else 0
        ctk.CTkLabel(right_p, text=f"Target Document: {doc_name} ({total_p} pages)", font=("Segoe UI", 11), text_color="gray70").pack(anchor="w", padx=14, pady=2)

        ctk.CTkLabel(right_p, text="Target Page Number:", font=("Arial", 10, "bold")).pack(anchor="w", padx=14, pady=(8, 2))
        ent_page_num = ctk.CTkEntry(right_p, width=120)
        ent_page_num.insert(0, str(total_p if total_p > 0 else 1))
        ent_page_num.pack(anchor="w", padx=14)

        ctk.CTkLabel(right_p, text="Stamp Location Preset:", font=("Arial", 10, "bold")).pack(anchor="w", padx=14, pady=(8, 2))
        opt_loc = ctk.CTkOptionMenu(right_p, values=["Bottom Right Corner", "Bottom Left Corner", "Center Bottom"])
        opt_loc.pack(anchor="w", padx=14, fill="x")

        # Execution Button
        def execute_sign():
            if not self.check_master_pdf_loaded():
                return

            out_p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Signed PDF Document", "*.pdf")])
            if not out_p:
                return

            p_target = int(ent_page_num.get().strip()) - 1 if ent_page_num.get().strip().isdigit() else 0
            loc_choice = opt_loc.get()

            # Coordinates on A4 (595 x 842)
            if "Right" in loc_choice:
                rect = (330, 680, 550, 750)
            elif "Left" in loc_choice:
                rect = (45, 680, 265, 750)
            else:
                rect = (190, 680, 410, 750)

            def worker():
                res = AcrobatProEngine.apply_electronic_signature(
                    self.active_pdf_path,
                    out_p,
                    p_target,
                    rect,
                    ent_signer_name.get().strip(),
                    ent_signer_email.get().strip(),
                    ent_signer_title.get().strip()
                )
                AuditLogger.log_event(self.space_role, "Acrobat Sign", os.path.basename(self.active_pdf_path), f"Signed document GUID: {res.get('guid')}")
                return res

            def on_done(res):
                messagebox.showinfo("Document Sealed", f"Document signed and sealed successfully!\n\nTransaction GUID: {res.get('guid')}\nSHA-256 Fingerprint: {res.get('sha256')[:24]}...\nAudit Certificate appended!")
                if messagebox.askyesno("Open Signed PDF", "Would you like to open the signed document in the suite now?"):
                    self.load_pdf_document(out_p)

            self.run_async_task(worker, on_complete=on_done, status_msg="Applying electronic signature & generating audit certificate...")

        btn_sign = ctk.CTkButton(
            right_p,
            text="✍️ Sign & Seal Document with Audit Trail",
            command=execute_sign,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            height=40,
            font=("Arial", 12, "bold")
        )
        btn_sign.pack(fill="x", padx=14, pady=20)

        return f

    # ==========================================================================
    # 5. VERSION CONTROL DOCUMENT COMPARISON (DIFF ENGINE)
    # ==========================================================================
    def frame_doc_compare(self, parent) -> ctk.CTkFrame:
        """Version Control Comparison — Side-by-Side Visual Diff & Change Log Report."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View Document Compare", "Diff Engine", "Opened Version Control Compare")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        ctk.CTkLabel(top_bar, text="🔍 Version Control Comparison | Side-by-Side Diff Engine", font=("Arial", 16, "bold"), text_color=ACCENT_AMBER).pack(side="left", padx=12, pady=10)

        body = ctk.CTkFrame(f, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # File Selectors Bar
        sel_bar = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=8)
        sel_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 8))

        doc_a_var = [getattr(self, "active_pdf_path", "")]
        doc_b_var = [""]

        lbl_a = ctk.CTkLabel(sel_bar, text=f"Document A (Original): {os.path.basename(doc_a_var[0]) if doc_a_var[0] else 'None Selected'}", font=("Segoe UI", 10, "bold"), text_color="#38BDF8")
        lbl_a.pack(side="left", padx=10, pady=8)

        def pick_doc_a():
            p = filedialog.askopenfilename(filetypes=[("PDF Document", "*.pdf")])
            if p:
                doc_a_var[0] = p
                lbl_a.configure(text=f"Document A (Original): {os.path.basename(p)}")

        ctk.CTkButton(sel_bar, text="📂 Select A", command=pick_doc_a, width=80, height=24, fg_color="gray30").pack(side="left", padx=4)

        lbl_b = ctk.CTkLabel(sel_bar, text="Document B (Revision): None Selected", font=("Segoe UI", 10, "bold"), text_color=ACCENT_GREEN)
        lbl_b.pack(side="left", padx=(20, 10), pady=8)

        def pick_doc_b():
            p = filedialog.askopenfilename(filetypes=[("PDF Document", "*.pdf")])
            if p:
                doc_b_var[0] = p
                lbl_b.configure(text=f"Document B (Revision): {os.path.basename(p)}")

        ctk.CTkButton(sel_bar, text="📂 Select B", command=pick_doc_b, width=80, height=24, fg_color="gray30").pack(side="left", padx=4)

        # Results Scrollable Frame
        diff_scroll = ctk.CTkScrollableFrame(body, fg_color=BG_DARK, corner_radius=8)
        diff_scroll.grid(row=1, column=0, sticky="nsew")

        # Stats Header
        diff_stats_frame = ctk.CTkFrame(diff_scroll, fg_color="transparent")
        diff_stats_frame.pack(fill="x", pady=6)

        lbl_sim = ctk.CTkLabel(diff_stats_frame, text="Similarity: --", font=("Arial", 12, "bold"), text_color=TEXT_LIGHT)
        lbl_sim.pack(side="left", padx=10)

        lbl_add = ctk.CTkLabel(diff_stats_frame, text="Added: --", font=("Arial", 12, "bold"), text_color=ACCENT_GREEN)
        lbl_add.pack(side="left", padx=10)

        lbl_del = ctk.CTkLabel(diff_stats_frame, text="Deleted: --", font=("Arial", 12, "bold"), text_color="crimson")
        lbl_del.pack(side="left", padx=10)

        lbl_mod = ctk.CTkLabel(diff_stats_frame, text="Modified: --", font=("Arial", 12, "bold"), text_color=ACCENT_AMBER)
        lbl_mod.pack(side="left", padx=10)

        diff_data_holder = [{}]

        def export_diff_report():
            if not diff_data_holder[0]:
                return messagebox.showwarning("No Diff", "Please run comparison first.")
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Comparison Audit Report PDF", "*.pdf")])
            if p:
                AcrobatProEngine.export_comparison_report_pdf(diff_data_holder[0], p)
                AuditLogger.log_event(self.space_role, "Export Diff Report", f"{diff_data_holder[0].get('doc_a_name')} vs {diff_data_holder[0].get('doc_b_name')}", f"Saved report to {p}")
                messagebox.showinfo("Exported", f"Comparison Change Log Report saved to:\n{p}")

        btn_exp_diff = ctk.CTkButton(diff_stats_frame, text="📄 Export Change Log Report (.pdf)", command=export_diff_report, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, height=26, font=("Arial", 10, "bold"))
        btn_exp_diff.pack(side="right", padx=10)

        diff_entries_box = ctk.CTkFrame(diff_scroll, fg_color="transparent")
        diff_entries_box.pack(fill="both", expand=True, pady=4)

        def run_compare():
            if not doc_a_var[0] or not doc_b_var[0]:
                return messagebox.showwarning("Select Documents", "Please select both Document A and Document B to compare.")

            def worker():
                res = AcrobatProEngine.compare_pdf_versions(doc_a_var[0], doc_b_var[0])
                diff_data_holder[0] = res
                AuditLogger.log_event(self.space_role, "Compare Versions", os.path.basename(doc_a_var[0]), f"Compared with {os.path.basename(doc_b_var[0])}")
                return res

            def on_done(res):
                lbl_sim.configure(text=f"Similarity: {res['similarity_percent']}%")
                lbl_add.configure(text=f"Added: +{res['additions_count']}")
                lbl_del.configure(text=f"Deleted: -{res['deletions_count']}")
                lbl_mod.configure(text=f"Modified: ~{res['modifications_count']}")

                for w in diff_entries_box.winfo_children():
                    w.destroy()

                for op in res.get("diff_ops", [])[:40]:
                    t = op["type"]
                    row = ctk.CTkFrame(diff_entries_box, fg_color=BG_CARD, corner_radius=4)
                    row.pack(fill="x", pady=3, padx=4)

                    if t == "ADDED":
                        ctk.CTkLabel(row, text=" [+] ADDED ", font=("Arial", 9, "bold"), fg_color="#065F46", text_color="#34D399", corner_radius=3).pack(side="left", padx=6, pady=4)
                        txt = " | ".join(op.get("lines_b", []))
                        ctk.CTkLabel(row, text=txt, font=("Segoe UI", 10), text_color="#FFFFFF", wraplength=650, justify="left").pack(side="left", fill="x", expand=True, padx=6)
                    elif t == "DELETED":
                        ctk.CTkLabel(row, text=" [-] DELETED ", font=("Arial", 9, "bold"), fg_color="#7F1D1D", text_color="#F87171", corner_radius=3).pack(side="left", padx=6, pady=4)
                        txt = " | ".join(op.get("lines_a", []))
                        ctk.CTkLabel(row, text=txt, font=("Segoe UI", 10), text_color="#FFFFFF", wraplength=650, justify="left").pack(side="left", fill="x", expand=True, padx=6)
                    elif t == "MODIFIED":
                        ctk.CTkLabel(row, text=" [~] MODIFIED ", font=("Arial", 9, "bold"), fg_color="#78350F", text_color="#FBBF24", corner_radius=3).pack(side="left", padx=6, pady=4)
                        txt = f"Was: {' | '.join(op.get('lines_a', []))}\nNow: {' | '.join(op.get('lines_b', []))}"
                        ctk.CTkLabel(row, text=txt, font=("Segoe UI", 10), text_color="#FFFFFF", wraplength=650, justify="left").pack(side="left", fill="x", expand=True, padx=6)

            self.run_async_task(worker, on_complete=on_done, status_msg="Running deep version control comparison engine...")

        ctk.CTkButton(sel_bar, text="🔍 Compare Documents", command=run_compare, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, width=160, height=28, font=("Arial", 11, "bold")).pack(side="right", padx=10)

        return f

    # ==========================================================================
    # 6. ADVANCED LEGAL REDACTION & DATA SANITISATION
    # ==========================================================================
    def frame_legal_redact(self, parent) -> ctk.CTkFrame:
        """Advanced Legal Redaction — Regex Pattern Sanitisation & Pixel Burnout."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View Legal Redact", "Redaction Studio", "Opened Legal Redaction Studio")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        ctk.CTkLabel(top_bar, text="🛡️ Advanced Legal Redaction | Deep Data Sanitisation Studio", font=("Arial", 16, "bold"), text_color=ACCENT_AMBER).pack(side="left", padx=12, pady=10)

        body = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        doc_name = os.path.basename(self.active_pdf_path) if self.active_pdf_path else "No Master PDF Loaded"
        ctk.CTkLabel(body, text=f"Target Document: {doc_name}", font=("Segoe UI", 12, "bold"), text_color=TEXT_LIGHT).pack(anchor="w", padx=14, pady=(12, 6))

        # Checkbox Patterns
        ctk.CTkLabel(body, text="Select Sensitive Data Entities to Permanently Redact:", font=("Arial", 11, "bold"), text_color=ACCENT_AMBER).pack(anchor="w", padx=14, pady=(6, 4))

        pattern_vars = {}
        for pat_name in list(AcrobatProEngine.REDACT_PATTERNS.keys()):
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(body, text=f"☑️ Redact {pat_name}", variable=var, font=("Segoe UI", 11))
            chk.pack(anchor="w", padx=20, pady=3)
            pattern_vars[pat_name] = var

        # Custom Keywords
        ctk.CTkLabel(body, text="Custom Sensitive Keywords / Names (comma-separated):", font=("Arial", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
        ent_custom_kw = ctk.CTkEntry(body, placeholder_text="e.g., Confidential, John Doe, Internal Only, Project Titan", width=450)
        ent_custom_kw.pack(anchor="w", padx=14, fill="x")

        # Metadata Sanitisation Checkbox
        var_sanitize_meta = ctk.BooleanVar(value=True)
        chk_meta = ctk.CTkCheckBox(body, text="🔒 Strip Document Metadata & Author/Producer Properties", variable=var_sanitize_meta, font=("Segoe UI", 11))
        chk_meta.pack(anchor="w", padx=14, pady=10)

        def execute_redaction():
            if not self.check_master_pdf_loaded():
                return

            out_p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Sanitized Redacted PDF", "*.pdf")])
            if not out_p:
                return

            selected_pats = [name for name, var in pattern_vars.items() if var.get()]
            kws = [k.strip() for k in ent_custom_kw.get().split(",") if k.strip()]

            def worker():
                res = AcrobatProEngine.apply_advanced_legal_redaction(
                    self.active_pdf_path,
                    out_p,
                    selected_pats,
                    kws,
                    var_sanitize_meta.get()
                )
                AuditLogger.log_event(self.space_role, "Legal Redaction", os.path.basename(self.active_pdf_path), f"Redacted {res.get('total_redactions')} entities")
                return res

            def on_done(res):
                breakdown = "\n".join([f"• {k}: {v} redacted" for k, v in res.get("pattern_hits", {}).items() if v > 0])
                msg = f"Legal Data Sanitisation Complete!\n\nTotal Entities Burned Out: {res.get('total_redactions')}\n\n{breakdown}\n\nSaved to:\n{out_p}"
                messagebox.showinfo("Sanitisation Complete", msg)
                if messagebox.askyesno("Load Redacted Document", "Would you like to open the sanitized document in the viewer?"):
                    self.load_pdf_document(out_p)

            self.run_async_task(worker, on_complete=on_done, status_msg="Permanently redacting sensitive entities and sanitising metadata...")

        btn_exec_redact = ctk.CTkButton(
            body,
            text="██ Permanently Burn-Out Sensitive Entities & Sanitize PDF",
            command=execute_redaction,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            height=42,
            font=("Arial", 13, "bold")
        )
        btn_exec_redact.pack(fill="x", padx=14, pady=20)

        return f

    # ==========================================================================
    # 7. ENTERPRISE ADMIN & AUDIT CONSOLE
    # ==========================================================================
    def frame_admin_console(self, parent) -> ctk.CTkFrame:
        """Enterprise Admin Console — Governance, Role Provisioning & Tamper-Evident Logs."""
        AuditLogger.log_event(getattr(self, "space_role", "Contributor"), "View Admin Console", "Enterprise Governance", "Accessed Admin Console")

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=8)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        ctk.CTkLabel(top_bar, text="👥 Enterprise Admin Console | Compliance & Audit Trail", font=("Arial", 16, "bold"), text_color=ACCENT_AMBER).pack(side="left", padx=12, pady=10)

        def export_audit_csv():
            logs = AuditLogger.get_all_logs()
            if not logs:
                return messagebox.showwarning("Empty", "Audit log is empty.")
            p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
            if p:
                import csv
                with open(p, "w", newline="", encoding="utf-8") as f_out:
                    writer = csv.DictWriter(f_out, fieldnames=["id", "timestamp", "role", "action", "document", "details"])
                    writer.writeheader()
                    writer.writerows(logs)
                messagebox.showinfo("Exported", f"Audit trail exported to:\n{p}")

        ctk.CTkButton(top_bar, text="💾 Export Audit Trail (.csv)", command=export_audit_csv, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, width=170, height=28).pack(side="right", padx=12)

        # Audit Logs Viewer
        logs_scroll = ctk.CTkScrollableFrame(f, fg_color=BG_DARK, corner_radius=8)
        logs_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        logs = AuditLogger.get_all_logs()
        if not logs:
            ctk.CTkLabel(logs_scroll, text="No enterprise activity logged yet.", font=("Arial", 12, "italic"), text_color="gray60").pack(pady=40)
        else:
            for log in logs[:100]:
                r = ctk.CTkFrame(logs_scroll, fg_color=BG_CARD, corner_radius=4)
                r.pack(fill="x", pady=2, padx=4)

                ctk.CTkLabel(r, text=log.get("timestamp", ""), font=("Courier", 10), text_color="gray70").pack(side="left", padx=8, pady=4)
                ctk.CTkLabel(r, text=f"[{log.get('role', 'User')}]", font=("Arial", 10, "bold"), text_color=ACCENT_AMBER).pack(side="left", padx=4)
                ctk.CTkLabel(r, text=log.get("action", ""), font=("Arial", 10, "bold"), text_color=ACCENT_GREEN).pack(side="left", padx=6)
                ctk.CTkLabel(r, text=f"• {log.get('document', '')}", font=("Segoe UI", 10), text_color=TEXT_LIGHT).pack(side="left", padx=6)
                ctk.CTkLabel(r, text=f"({log.get('details', '')})", font=("Segoe UI", 9, "italic"), text_color="gray70").pack(side="left", padx=6)

        return f