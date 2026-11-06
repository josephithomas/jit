/**
 * Universal SkillForge Front-end Client.
 * Handles drag-and-drop, multi-format parsing, client-side OCR (Tesseract.js),
 * dynamic linting, cross-platform checks, and one-click installs.
 */

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const fileStatusContainer = document.getElementById("fileStatusContainer");
  const ocrStatusBar = document.getElementById("ocrStatusBar");
  const ocrStatusText = document.getElementById("ocrStatusText");

  const rawTextInput = document.getElementById("rawTextInput");
  const clearTextBtn = document.getElementById("clearTextBtn");
  const skillNameInput = document.getElementById("skillNameInput");
  const descriptionInput = document.getElementById("descriptionInput");
  const boundarySelect = document.getElementById("boundarySelect");
  const synthesizeBtn = document.getElementById("synthesizeBtn");

  const scoreDisplay = document.getElementById("scoreDisplay");
  const scoreBadge = document.getElementById("scoreBadge");
  const tokenDisplay = document.getElementById("tokenDisplay");
  const wordsDisplay = document.getElementById("wordsDisplay");
  const compatBadges = document.getElementById("compatBadges");
  const linterNotifications = document.getElementById("linterNotifications");

  const viewRawBtn = document.getElementById("viewRawBtn");
  const viewPreviewBtn = document.getElementById("viewPreviewBtn");
  const outputMarkdown = document.getElementById("outputMarkdown");
  const previewContainer = document.getElementById("previewContainer");

  const copyBtn = document.getElementById("copyBtn");
  const downloadMdBtn = document.getElementById("downloadMdBtn");
  const downloadZipBtn = document.getElementById("downloadZipBtn");
  const installBtn = document.getElementById("installBtn");

  const quickTemplateBtn = document.getElementById("quickTemplateBtn");
  const blueprintsModal = document.getElementById("blueprintsModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const blueprintsList = document.getElementById("blueprintsList");

  const installModal = document.getElementById("installModal");
  const closeInstallModalBtn = document.getElementById("closeInstallModalBtn");
  const installToAntigravityBtn = document.getElementById("installToAntigravityBtn");
  const installToClaudeBtn = document.getElementById("installToClaudeBtn");
  const installToWorkspaceBtn = document.getElementById("installToWorkspaceBtn");
  const installResultAlert = document.getElementById("installResultAlert");

  let currentSkillName = "universal-skill";
  let activeTab = "editor";

  fetchTemplates();
  populateInitialSkill();

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  });

  async function handleFiles(files) {
    for (const file of files) {
      showFileStatus(file.name, "uploading", "Processing...");

      const isImage = file.type.startsWith("image/") || /\.(png|jpe?g|webp|bmp)$/i.test(file.name);

      if (isImage && window.Tesseract) {
        showOcrStatus(`Extracting text from image '${file.name}' via client-side OCR...`);
        try {
          const ocrResult = await Tesseract.recognize(file, "eng", {
            logger: (m) => {
              if (m.status === "recognizing text") {
                showOcrStatus(`OCR on '${file.name}': ${Math.round(m.progress * 100)}%`);
              }
            }
          });
          const ocrText = (ocrResult.data && ocrResult.data.text) ? ocrResult.data.text.trim() : "";
          if (ocrText.length > 15) {
            appendRawText(`\n\n--- Extracted from Image: ${file.name} ---\n${ocrText}`);
            showFileStatus(file.name, "success", `OCR extracted ${ocrText.split(/\s+/).length} words`);
            hideOcrStatus();
            continue;
          }
        } catch (ocrErr) {
          console.warn("Client OCR error:", ocrErr);
        }
        hideOcrStatus();
      }

      try {
        const formData = new FormData();
        formData.append("file", file);

        const resp = await fetch("/api/upload", {
          method: "POST",
          body: formData
        });

        if (!resp.ok) {
          throw new Error(`Server returned ${resp.status}`);
        }

        const data = await resp.json();
        const extracted = data.text || "";
        const wordCount = data.metadata ? data.metadata.word_count || extracted.split(/\s+/).length : 0;

        appendRawText(`\n\n--- Document Ingested: ${file.name} (${data.format}) ---\n${extracted}`);
        showFileStatus(file.name, "success", `${data.format.toUpperCase()} parsed (${wordCount} words)`);
      } catch (err) {
        showFileStatus(file.name, "error", `Failed: ${err.message}`);
      }
    }
  }

  function appendRawText(newText) {
    const existing = rawTextInput.value.trim();
    if (existing) {
      rawTextInput.value = existing + newText;
    } else {
      rawTextInput.value = newText.trim();
    }
    triggerSynthesize();
  }

  function showFileStatus(filename, state, message) {
    fileStatusContainer.classList.remove("hidden");
    const chip = document.createElement("div");
    chip.className = "flex items-center justify-between bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs";
    
    let iconClass = "text-indigo-400";
    let iconName = "file";
    if (state === "success") {
      iconClass = "text-emerald-400";
      iconName = "check-circle";
    } else if (state === "error") {
      iconClass = "text-red-400";
      iconName = "alert-circle";
    }

    chip.innerHTML = `
      <div class="flex items-center space-x-2 truncate">
        <i data-lucide="${iconName}" class="w-3.5 h-3.5 ${iconClass}"></i>
        <span class="font-medium text-slate-200 truncate">${escapeHtml(filename)}</span>
      </div>
      <span class="text-[10px] text-slate-400 ml-2 whitespace-nowrap">${escapeHtml(message)}</span>
    `;
    fileStatusContainer.appendChild(chip);
    if (window.lucide) lucide.createIcons();
  }

  function showOcrStatus(msg) {
    ocrStatusBar.classList.remove("hidden");
    ocrStatusText.textContent = msg;
  }

  function hideOcrStatus() {
    ocrStatusBar.classList.add("hidden");
  }

  clearTextBtn.addEventListener("click", () => {
    rawTextInput.value = "";
    fileStatusContainer.innerHTML = "";
    fileStatusContainer.classList.add("hidden");
  });

  synthesizeBtn.addEventListener("click", triggerSynthesize);

  async function triggerSynthesize() {
    const text = rawTextInput.value.trim();
    if (!text) {
      alert("Please enter prompt text, upload a document, or choose a blueprint first.");
      return;
    }

    synthesizeBtn.disabled = true;
    synthesizeBtn.innerHTML = `
      <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
      <span>Synthesizing Spec...</span>
    `;

    const platforms = Array.from(document.querySelectorAll(".platform-check:checked")).map((el) => el.value);

    try {
      const resp = await fetch("/api/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_text: text,
          skill_name: skillNameInput.value.trim() || undefined,
          description: descriptionInput.value.trim() || undefined,
          target_platforms: platforms,
          boundary_level: boundarySelect.value
        })
      });

      if (!resp.ok) {
        throw new Error(`HTTP Error ${resp.status}`);
      }

      const res = await resp.json();
      currentSkillName = res.name;
      outputMarkdown.value = res.markdown;

      updateValidationUI(res.validation);

      if (activeTab === "preview") {
        renderPreview();
      }
    } catch (e) {
      alert("Synthesis failed: " + e.message);
    } finally {
      synthesizeBtn.disabled = false;
      synthesizeBtn.innerHTML = `
        <i data-lucide="wand-2" class="w-4 h-4"></i>
        <span>Synthesize Universal SKILL.md</span>
      `;
      if (window.lucide) lucide.createIcons();
    }
  }

  let lintTimeout = null;
  outputMarkdown.addEventListener("input", () => {
    clearTimeout(lintTimeout);
    lintTimeout = setTimeout(async () => {
      try {
        const resp = await fetch("/api/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ markdown: outputMarkdown.value })
        });
        if (resp.ok) {
          const res = await resp.json();
          updateValidationUI(res.validation);
        }
      } catch (err) {
        console.warn("Live validation error:", err);
      }
    }, 400);
  });

  function updateValidationUI(val) {
    if (!val) return;

    const score = val.score || 0;
    scoreDisplay.textContent = score;

    let grade = "A+";
    let gradeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    if (score < 50) {
      grade = "F";
      gradeClass = "bg-red-500/10 text-red-400 border-red-500/30";
    } else if (score < 70) {
      grade = "C";
      gradeClass = "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
    } else if (score < 85) {
      grade = "B";
      gradeClass = "bg-blue-500/10 text-blue-400 border-blue-500/30";
    }
    scoreBadge.className = `w-10 h-10 rounded-xl border flex items-center justify-center font-bold text-sm ${gradeClass}`;
    scoreBadge.textContent = grade;

    if (val.stats) {
      wordsDisplay.textContent = val.stats.word_count || 0;
      tokenDisplay.textContent = `~${val.stats.token_estimate || 0}`;
    }

    if (val.compatibility) {
      compatBadges.innerHTML = "";
      for (const [plat, info] of Object.entries(val.compatibility)) {
        const badge = document.createElement("span");
        if (info.compatible) {
          badge.className = "text-[10px] bg-slate-800 text-emerald-400 px-1.5 py-0.5 rounded font-mono border border-emerald-500/30";
          badge.textContent = `${plat.capitalize()} ✓`;
        } else {
          badge.className = "text-[10px] bg-slate-800 text-red-400 px-1.5 py-0.5 rounded font-mono border border-red-500/30";
          badge.textContent = `${plat.capitalize()} ✗`;
        }
        compatBadges.appendChild(badge);
      }
    }

    linterNotifications.innerHTML = "";
    const issues = val.issues || [];
    const warnings = val.warnings || [];

    if (issues.length === 0 && warnings.length === 0) {
      linterNotifications.classList.add("hidden");
    } else {
      linterNotifications.classList.remove("hidden");
      issues.forEach((iss) => {
        const div = document.createElement("div");
        div.className = "bg-red-950/40 border border-red-800/60 text-red-300 rounded-lg p-2 text-xs flex items-center gap-2";
        div.innerHTML = `<i data-lucide="alert-octagon" class="w-3.5 h-3.5 text-red-400 flex-shrink-0"></i> <span>${escapeHtml(iss)}</span>`;
        linterNotifications.appendChild(div);
      });
      warnings.forEach((warn) => {
        const div = document.createElement("div");
        div.className = "bg-yellow-950/30 border border-yellow-800/50 text-yellow-300 rounded-lg p-2 text-xs flex items-center gap-2";
        div.innerHTML = `<i data-lucide="info" class="w-3.5 h-3.5 text-yellow-400 flex-shrink-0"></i> <span>${escapeHtml(warn)}</span>`;
        linterNotifications.appendChild(div);
      });
      if (window.lucide) lucide.createIcons();
    }
  }

  viewRawBtn.addEventListener("click", () => {
    activeTab = "editor";
    viewRawBtn.className = "px-3 py-1 rounded-md bg-indigo-600 text-white font-medium transition";
    viewPreviewBtn.className = "px-3 py-1 rounded-md text-slate-400 hover:text-white transition";
    outputMarkdown.classList.remove("hidden");
    previewContainer.classList.add("hidden");
  });

  viewPreviewBtn.addEventListener("click", () => {
    activeTab = "preview";
    viewPreviewBtn.className = "px-3 py-1 rounded-md bg-indigo-600 text-white font-medium transition";
    viewRawBtn.className = "px-3 py-1 rounded-md text-slate-400 hover:text-white transition";
    outputMarkdown.classList.add("hidden");
    previewContainer.classList.remove("hidden");
    renderPreview();
  });

  function renderPreview() {
    if (window.marked) {
      previewContainer.innerHTML = marked.parse(outputMarkdown.value);
    }
  }

  copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(outputMarkdown.value);
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> Copied!`;
    if (window.lucide) lucide.createIcons();
    setTimeout(() => {
      copyBtn.innerHTML = originalText;
      if (window.lucide) lucide.createIcons();
    }, 2000);
  });

  downloadMdBtn.addEventListener("click", () => {
    const blob = new Blob([outputMarkdown.value], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "SKILL.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  downloadZipBtn.addEventListener("click", async () => {
    try {
      const resp = await fetch("/api/export/zip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_text: outputMarkdown.value,
          skill_name: currentSkillName
        })
      });
      if (!resp.ok) throw new Error("Export failed");
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${currentSkillName}-skill-package.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Failed to export ZIP package: " + e.message);
    }
  });

  installBtn.addEventListener("click", () => {
    installResultAlert.classList.add("hidden");
    installModal.classList.remove("hidden");
  });

  closeInstallModalBtn.addEventListener("click", () => {
    installModal.classList.add("hidden");
  });

  async function performInstall(target) {
    installResultAlert.className = "p-3 rounded-lg text-xs font-mono bg-indigo-950/50 text-indigo-300 border border-indigo-800/60";
    installResultAlert.classList.remove("hidden");
    installResultAlert.textContent = `Installing '${currentSkillName}' into ${target}...`;

    try {
      const resp = await fetch("/api/install", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skill_name: currentSkillName,
          markdown: outputMarkdown.value,
          target: target
        })
      });

      const res = await resp.json();
      if (res.success) {
        installResultAlert.className = "p-3 rounded-lg text-xs font-mono bg-emerald-950/50 text-emerald-300 border border-emerald-800/60";
        installResultAlert.textContent = `✓ Successfully installed to: ${res.installed_path || res.installed_paths?.join(", ")}`;
      } else {
        throw new Error(res.detail || "Install failed");
      }
    } catch (err) {
      installResultAlert.className = "p-3 rounded-lg text-xs font-mono bg-red-950/50 text-red-300 border border-red-800/60";
      installResultAlert.textContent = `✗ Error: ${err.message}`;
    }
  }

  installToAntigravityBtn.addEventListener("click", () => performInstall("antigravity"));
  installToClaudeBtn.addEventListener("click", () => performInstall("claude"));
  installToWorkspaceBtn.addEventListener("click", () => performInstall("workspace"));

  quickTemplateBtn.addEventListener("click", () => {
    blueprintsModal.classList.remove("hidden");
  });

  closeModalBtn.addEventListener("click", () => {
    blueprintsModal.classList.add("hidden");
  });

  async function fetchTemplates() {
    try {
      const resp = await fetch("/api/templates");
      if (resp.ok) {
        const data = await resp.json();
        renderBlueprints(data.templates || []);
      }
    } catch (e) {
      console.warn("Could not fetch blueprints:", e);
    }
  }

  function renderBlueprints(templates) {
    blueprintsList.innerHTML = "";
    templates.forEach((t) => {
      const card = document.createElement("button");
      card.className = "text-left bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/50 p-3.5 rounded-xl transition flex flex-col justify-between";
      card.innerHTML = `
        <div>
          <span class="text-[10px] uppercase font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">${escapeHtml(t.category)}</span>
          <h4 class="text-sm font-semibold text-white mt-1.5">${escapeHtml(t.name)}</h4>
          <p class="text-[11px] text-slate-400 mt-1 line-clamp-3">${escapeHtml(t.sample_text.split("\n")[1] || "")}</p>
        </div>
        <div class="mt-3 text-[11px] text-indigo-400 flex items-center gap-1 font-medium">
          <span>Apply Blueprint</span>
          <i data-lucide="arrow-right" class="w-3 h-3"></i>
        </div>
      `;
      card.addEventListener("click", () => {
        rawTextInput.value = t.sample_text;
        skillNameInput.value = t.id;
        boundarySelect.value = t.boundary || "standard";
        blueprintsModal.classList.add("hidden");
        triggerSynthesize();
      });
      blueprintsList.appendChild(card);
    });
    if (window.lucide) lucide.createIcons();
  }

  function populateInitialSkill() {
    rawTextInput.value = `Standard Operating Procedure: Universal Agent Task Executor
Purpose: Execute complex automation and analysis workflows autonomously across project workspaces.
Workflow:
1. Ingest context, inspect existing configuration, and identify task constraints.
2. Formulate step-by-step execution strategy with verifiable checkpoints.
3. Apply changes with minimal diffs and verify system integrity.
4. Run automated test suites and validation linting.
5. Deliver clean summary of completed actions and artifacts.
Boundaries:
- Never overwrite customer credentials or bypass security policies.
- Preserve all existing comments and documentation.`;
    triggerSynthesize();
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  String.prototype.capitalize = function () {
    return this.charAt(0).toUpperCase() + this.slice(1);
  };
});
