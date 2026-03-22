document.getElementById("testDate").valueAsDate = new Date();

let selectedFiles = [];
let currentAiData = null; // Stores AI JSON to avoid recalling Gemini
let countdownInterval = null;
let simulatedProgress = null;

// ==========================================
// UI & NETWORK STATE
// ==========================================
function updateOnlineStatus() {
  const status = document.getElementById("networkStatus");
  const text = document.getElementById("networkText");
  const btn = document.getElementById("generatePreviewBtn");
  if (navigator.onLine) {
    status.classList.remove("offline");
    text.innerText = "System Online";
    btn.disabled = false;
    btn.innerHTML =
      '<i class="fa-solid fa-eye"></i> <span>Generate Test Preview</span>';
  } else {
    status.classList.add("offline");
    text.innerText = "Offline";
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-wifi"></i> <span>No Internet</span>';
  }
}
window.addEventListener("online", updateOnlineStatus);
window.addEventListener("offline", updateOnlineStatus);
updateOnlineStatus();

document.getElementById("examPattern").addEventListener("change", function (e) {
  const boardGroup = document.getElementById("boardConfigGroup");
  if (e.target.value === "board") {
    boardGroup.classList.remove("hidden");
    [
      "shortTotal",
      "shortAttempt",
      "longTotal",
      "longAttempt",
      "longMarks",
    ].forEach((id) => (document.getElementById(id).required = true));
  } else {
    boardGroup.classList.add("hidden");
    [
      "shortTotal",
      "shortAttempt",
      "longTotal",
      "longAttempt",
      "longMarks",
    ].forEach((id) => (document.getElementById(id).required = false));
  }
});

// ==========================================
// DRAG & DROP FILES
// ==========================================
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const previewContainer = document.getElementById("previewContainer");

document.addEventListener("paste", (e) => {
  const items = (e.clipboardData || e.originalEvent.clipboardData).items;
  let filesAdded = false;
  for (let index in items) {
    if (
      items[index].kind === "file" &&
      items[index].type.startsWith("image/")
    ) {
      if (selectedFiles.length >= 10) return alert("Max 10 files.");
      selectedFiles.push(
        new File([items[index].getAsFile()], `pasted_${Date.now()}.png`, {
          type: items[index].type,
        }),
      );
      filesAdded = true;
    }
  }
  if (filesAdded) renderPreviews();
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () =>
  dropZone.classList.remove("dragover"),
);
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
});
fileInput.addEventListener("change", (e) => {
  handleFiles(e.target.files);
  fileInput.value = "";
});

function handleFiles(files) {
  for (let i = 0; i < files.length; i++) {
    if (selectedFiles.length >= 10) break;
    selectedFiles.push(files[i]);
  }
  renderPreviews();
}

function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderPreviews();
}

function renderPreviews() {
  previewContainer.classList.toggle("hidden", selectedFiles.length === 0);
  previewContainer.innerHTML = "";
  selectedFiles.forEach((file, index) => {
    const item = document.createElement("div");
    item.className = "preview-item";
    const btn = document.createElement("button");
    btn.className = "remove-file-btn";
    btn.innerHTML = "X";
    btn.onclick = (e) => {
      e.stopPropagation();
      removeFile(index);
    };
    item.appendChild(btn);

    if (file.type.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      item.appendChild(img);
    } else {
      const icon = document.createElement("i");
      icon.className = "fa-solid fa-file-pdf pdf-icon";
      item.appendChild(icon);
    }
    previewContainer.appendChild(item);
  });
}

// ==========================================
// BUILD FORM DATA
// ==========================================
function buildBaseFormData() {
  const fd = new FormData();
  const pattern = document.getElementById("examPattern").value;
  fd.append("exam_pattern", pattern);
  fd.append("bilingual", document.getElementById("bilingual").value);
  fd.append(
    "magic_prompt",
    document.getElementById("magicPrompt")
      ? document.getElementById("magicPrompt").value.trim()
      : "",
  );

  if (pattern === "board") {
    fd.append("short_groups", document.getElementById("shortGroups").value);
    fd.append("short_total", document.getElementById("shortTotal").value);
    fd.append("short_attempt", document.getElementById("shortAttempt").value);
    fd.append("long_total", document.getElementById("longTotal").value);
    fd.append("long_attempt", document.getElementById("longAttempt").value);
  } else {
    fd.append("short_groups", "1");
    fd.append("short_total", "8");
    fd.append("short_attempt", "5");
    fd.append("long_total", "3");
    fd.append("long_attempt", "2");
  }
  return fd;
}

// ==========================================
// RENDER PREVIEW HTML
// ==========================================
function renderPaperPreview(data) {
  let html = `<div style="text-align:center; border-bottom: 2px solid #cbd5e1; padding-bottom:10px; margin-bottom: 20px;">
                <h1 style="font-size: 24px;">${document.getElementById("academyName").value.toUpperCase() || "TEST PAPER"}</h1>
                <p><b>Subject:</b> ${document.getElementById("subject").value || "..."} | <b>Class:</b> ${document.getElementById("className").value || "..."}</p>
              </div>`;

  if (data.mcqs && data.mcqs.length > 0) {
    html += `<h3>Multiple Choice Questions</h3><ol style="margin-left: 20px; margin-bottom: 20px;">`;
    data.mcqs.forEach((m) => {
      let q = m.q_en || m.question || "";
      if (m.q_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right;">${m.q_ur}</span><div style="clear:both;"></div>`;
      html += `<li style="margin-bottom: 15px;"><b>${q}</b><br>
               A) ${m.a_en || m.a || ""} &nbsp;&nbsp; B) ${m.b_en || m.b || ""} <br>
               C) ${m.c_en || m.c || ""} &nbsp;&nbsp; D) ${m.d_en || m.d || ""} <br>
               <i style="color: #10b981;">Ans: ${m.answer || ""}</i></li>`;
    });
    html += `</ol>`;
  }

  if (data.short_qs && data.short_qs.length > 0) {
    html += `<h3>Short Questions</h3><ul style="margin-left: 20px; margin-bottom: 20px; list-style-type: none; padding:0;">`;
    data.short_qs.forEach((sq, i) => {
      let q = sq.text_en || sq.text || "";
      if (sq.text_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right;">${sq.text_ur}</span><div style="clear:both;"></div>`;
      html += `<li style="margin-bottom: 10px;"><b>Q${i + 1}:</b> ${q}</li>`;
    });
    html += `</ul>`;
  }

  if (data.long_qs && data.long_qs.length > 0) {
    html += `<h3>Long Questions</h3><ul style="margin-left: 20px; list-style-type: none; padding:0;">`;
    data.long_qs.forEach((lq, i) => {
      let q = lq.text_en || lq.text || "";
      q = q.replace(/\\n/g, "<br>"); // Handle part A and B formatting
      if (lq.text_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right;">${lq.text_ur}</span><div style="clear:both;"></div>`;
      html += `<li style="margin-bottom: 15px;"><b>Q${i + 1}:</b> ${q}</li>`;
    });
    html += `</ul>`;
  }

  document.getElementById("paperPreviewContent").innerHTML = html;
}

// ==========================================
// STEP 1: GENERATE PREVIEW (FORM SUBMIT)
// ==========================================
const BASE_URL = "https://ai-test-generator-2hsf.onrender.com";

document
  .getElementById("testForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!navigator.onLine) return alert("No internet connection.");
    const textVal = document.getElementById("bookText").value.trim();
    if (!textVal && selectedFiles.length === 0)
      return alert("⚠️ Please provide Source Material!");

    const fd = buildBaseFormData();
    fd.append("text", textVal);
    selectedFiles.forEach((file) => fd.append("files", file));

    const btn = document.getElementById("generatePreviewBtn");
    const pContainer = document.getElementById("progressContainer");
    const pFill = document.getElementById("progressBar");
    const pMsg = document.getElementById("progressText");

    btn.disabled = true;
    btn.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin"></i> Generating Preview...';
    pContainer.classList.remove("hidden");
    pFill.style.width = "50%";
    pMsg.innerText = "Extracting AI Data...";

    try {
      const response = await fetch(`${BASE_URL}/generate-preview`, {
        method: "POST",
        body: fd,
      });
      if (!response.ok) throw new Error(await response.text());

      currentAiData = await response.json(); // Save data globally!
      renderPaperPreview(currentAiData);

      // Switch UI State
      document.getElementById("inputState").classList.add("hidden");
      document.getElementById("previewState").classList.remove("hidden");
      document.getElementById("rightPanelTitle").innerText =
        "Review & Refine Test";
      document.getElementById("rightPanelBadge").innerText = "Interactive Mode";
    } catch (error) {
      console.error(error);
      alert("Error generating preview: " + error.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-eye"></i> Generate Test Preview';
      pContainer.classList.add("hidden");
    }
  });

// ==========================================
// STEP 2: DOWNLOAD (FAST EXPORT)
// ==========================================
async function downloadDocument(isPdf) {
  if (!currentAiData)
    return alert("No test data found. Generate preview first.");

  const btnId = isPdf ? "downloadPdfBtn" : "downloadWordBtn";
  const btn = document.getElementById(btnId);
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
  btn.disabled = true;

  const fd = buildBaseFormData();
  fd.append("academy_name", document.getElementById("academyName").value);
  fd.append("subject", document.getElementById("subject").value);
  fd.append("class_name", document.getElementById("className").value);
  fd.append("test_date", document.getElementById("testDate").value);
  fd.append(
    "time_allowed",
    document.getElementById("timeAllowed").value + " min",
  );
  fd.append("syllabus", document.getElementById("syllabus").value);
  fd.append("template_style", document.getElementById("templateStyle").value);
  if (document.getElementById("examPattern").value === "board") {
    fd.append("long_q_marks", document.getElementById("longMarks").value);
  } else {
    fd.append("long_q_marks", "5");
  }
  fd.append("generate_answer_key", "no");

  // MAGIC TRICK: Send the JSON string back so backend doesn't call AI again!
  fd.append("ai_data_json", JSON.stringify(currentAiData));

  try {
    const endpoint = isPdf
      ? `${BASE_URL}/generate-pdf`
      : `${BASE_URL}/generate-word`;
    const response = await fetch(endpoint, { method: "POST", body: fd });
    if (!response.ok) throw new Error(await response.text());

    const blob = await response.blob();
    const cleanStr = (str) => str.replace(/[\\/:*?"<>|]/g, "-");
    const ext = isPdf ? "pdf" : "docx";
    const filename = `${cleanStr(document.getElementById("className").value)}_${cleanStr(document.getElementById("subject").value)}.${ext}`;

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert("Download failed: " + error.message);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

document
  .getElementById("downloadWordBtn")
  .addEventListener("click", () => downloadDocument(false));
document
  .getElementById("downloadPdfBtn")
  .addEventListener("click", () => downloadDocument(true));

// BACK BUTTON
document.getElementById("backToEditBtn").addEventListener("click", () => {
  document.getElementById("previewState").classList.add("hidden");
  document.getElementById("inputState").classList.remove("hidden");
  document.getElementById("rightPanelTitle").innerText =
    "Source Material & AI Magic";
  document.getElementById("rightPanelBadge").innerText = "Text, PDFs & Images";
});

// AI REFINE BUTTON (Placeholder for now)
document.getElementById("aiRefineBtn").addEventListener("click", () => {
  const prompt = document.getElementById("aiRefinePrompt").value;
  if (!prompt) return alert("Please type an instruction first!");
  alert(
    "Interactive AI Refinement will be enabled in the next update! \nYour prompt: " +
      prompt,
  );
});
