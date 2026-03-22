document.getElementById("testDate").valueAsDate = new Date();

let selectedFiles = [];
let currentAiData = null;

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
      '<i class="fa-solid fa-eye"></i> <span>Generate True A4 Preview</span>';
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
// FORM DATA BUILDER
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
// RENDER TRUE A4 HTML PREVIEW
// ==========================================
function renderA4Paper(data) {
  const acadName =
    document.getElementById("academyName").value.toUpperCase() ||
    "ACADEMY NAME";
  const subj = document.getElementById("subject").value || "Subject";
  const cls = document.getElementById("className").value || "Class";
  const syll = document.getElementById("syllabus").value || "Syllabus";

  const dateObj = new Date(document.getElementById("testDate").value);
  const formattedDate = dateObj.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const time = document.getElementById("timeAllowed").value || "60";

  // Clean text function similar to Python backend
  const cT = (text) => (text ? text.replace(/^\d+[\.\)]\s*/, "").trim() : "");

  let html = `
    <div class="header-info">
        <h1>${acadName}</h1>
        <p>${subj} &nbsp;|&nbsp; ${cls} &nbsp;|&nbsp; ${syll}</p>
    </div>
    <div class="student-info">
        <span>Name: ____________________</span>
        <span>Date: ${formattedDate}</span>
        <span>Time: <u>${time} Min</u></span>
        <span>Max Marks: <u>Calculated</u></span>
    </div>
  `;

  if (data.mcqs && data.mcqs.length > 0) {
    html += `<h3 style="margin-top:20px;">Multiple Choice Questions</h3><ol style="margin-left: 25px; margin-bottom: 30px;">`;
    data.mcqs.forEach((m) => {
      let q = cT(m.q_en || m.question || "");
      if (m.q_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right; font-size:16px;">${m.q_ur}</span><div style="clear:both;"></div>`;
      html += `<li style="margin-bottom: 15px; padding-left: 5px;">
               <b>${q}</b><br>
               <table style="width:100%; margin-top:5px; table-layout:fixed;">
                <tr>
                 <td>A) ${cT(m.a_en || m.a)} ${m.a_ur ? '<span dir="rtl" style="float:right; font-family:\'Jameel Noori Nastaleeq\'">' + m.a_ur + "</span>" : ""}</td>
                 <td>B) ${cT(m.b_en || m.b)} ${m.b_ur ? '<span dir="rtl" style="float:right; font-family:\'Jameel Noori Nastaleeq\'">' + m.b_ur + "</span>" : ""}</td>
                </tr>
                <tr>
                 <td>C) ${cT(m.c_en || m.c)} ${m.c_ur ? '<span dir="rtl" style="float:right; font-family:\'Jameel Noori Nastaleeq\'">' + m.c_ur + "</span>" : ""}</td>
                 <td>D) ${cT(m.d_en || m.d)} ${m.d_ur ? '<span dir="rtl" style="float:right; font-family:\'Jameel Noori Nastaleeq\'">' + m.d_ur + "</span>" : ""}</td>
                </tr>
               </table>
               </li>`;
    });
    html += `</ol>`;
  }

  if (data.short_qs && data.short_qs.length > 0) {
    html += `<h3 style="margin-top:20px;">Short Questions</h3><ol style="margin-left: 25px; margin-bottom: 30px;">`;
    data.short_qs.forEach((sq) => {
      let q = cT(sq.text_en || sq.text || "");
      if (sq.text_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right; font-size:16px;">${sq.text_ur}</span><div style="clear:both;"></div>`;
      html += `<li style="margin-bottom: 12px; padding-left: 5px;"><b>${q}</b></li>`;
    });
    html += `</ol>`;
  }

  if (data.long_qs && data.long_qs.length > 0) {
    html += `<h3 style="margin-top:20px;">Long Questions</h3><ol style="margin-left: 25px; margin-bottom: 20px;">`;
    data.long_qs.forEach((lq) => {
      let q = cT(lq.text_en || lq.text || "");
      q = q.replace(/\\n/g, "<br>");
      if (lq.text_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right; font-size:16px;">${lq.text_ur}</span><div style="clear:both;"></div>`;
      html += `<li style="margin-bottom: 20px; padding-left: 5px;"><b>${q}</b></li>`;
    });
    html += `</ol>`;
  }

  document.getElementById("paperLoader").classList.add("hidden");
  document.getElementById("paperContent").innerHTML = html;
}

// ==========================================
// STEP 1: GENERATE PREVIEW (API CALL)
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
    const pMsg = document.getElementById("progressText");

    btn.disabled = true;
    btn.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin"></i> Reading files & extracting logic...';
    pContainer.classList.remove("hidden");

    // Realistic Progress Messaging
    let step = 0;
    const messages = [
      "Reading Source Files...",
      "AI is analyzing context...",
      "Structuring Test JSON...",
    ];
    const progInt = setInterval(() => {
      step = (step + 1) % messages.length;
      pMsg.innerText = messages[step];
    }, 2000);

    try {
      const response = await fetch(`${BASE_URL}/generate-preview`, {
        method: "POST",
        body: fd,
      });
      if (!response.ok) throw new Error(await response.text());

      currentAiData = await response.json();

      // Switch to Preview UI
      document.getElementById("inputState").classList.add("hidden");
      document.getElementById("previewState").classList.remove("hidden");
      document.getElementById("rightPanelTitle").innerText =
        "Review & Edit Test Paper";
      document.getElementById("rightPanelBadge").innerText = "Interactive Mode";

      renderA4Paper(currentAiData);
    } catch (error) {
      console.error(error);
      alert("Error: " + error.message);
    } finally {
      clearInterval(progInt);
      btn.disabled = false;
      btn.innerHTML =
        '<i class="fa-solid fa-eye"></i> <span>Generate True A4 Preview</span>';
      pContainer.classList.add("hidden");
    }
  });

// ==========================================
// LIVE AI EDITOR (REFINE PREVIEW)
// ==========================================
document.getElementById("aiRefineBtn").addEventListener("click", async () => {
  const promptInput = document.getElementById("aiRefinePrompt");
  const prompt = promptInput.value.trim();
  if (!prompt) return alert("Please type an instruction first!");

  const btn = document.getElementById("aiRefineBtn");
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating...';

  document.getElementById("paperContent").innerHTML = "";
  document.getElementById("paperLoader").classList.remove("hidden");

  const fd = new FormData();
  fd.append("ai_data_json", JSON.stringify(currentAiData));
  fd.append("refine_prompt", prompt);

  try {
    const response = await fetch(`${BASE_URL}/refine-preview`, {
      method: "POST",
      body: fd,
    });
    if (!response.ok) throw new Error(await response.text());
    currentAiData = await response.json();
    renderA4Paper(currentAiData);
    promptInput.value = ""; // clear input
  } catch (error) {
    alert("Failed to refine: " + error.message);
    renderA4Paper(currentAiData); // restore old view
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Update';
  }
});

// ==========================================
// STEP 2: INSTANT DOWNLOADS
// ==========================================
async function downloadWordDocument() {
  if (!currentAiData) return;
  const btn = document.getElementById("downloadWordBtn");
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
  fd.append(
    "long_q_marks",
    document.getElementById("examPattern").value === "board"
      ? document.getElementById("longMarks").value
      : "5",
  );
  fd.append("generate_answer_key", "no");
  fd.append("ai_data_json", JSON.stringify(currentAiData));

  try {
    const response = await fetch(`${BASE_URL}/generate-word`, {
      method: "POST",
      body: fd,
    });
    if (!response.ok) throw new Error(await response.text());
    const blob = await response.blob();
    const cls = document
      .getElementById("className")
      .value.replace(/[\\/:*?"<>|]/g, "-");
    const sub = document
      .getElementById("subject")
      .value.replace(/[\\/:*?"<>|]/g, "-");
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${cls}_${sub}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert("Download failed: " + error.message);
  } finally {
    btn.innerHTML = '<i class="fa-solid fa-file-word"></i> Download Word';
    btn.disabled = false;
  }
}

// 🔥 INSTANT PDF FIX USING HTML2PDF.JS 🔥
function downloadPdfDocument() {
  if (!currentAiData) return;
  const btn = document.getElementById("downloadPdfBtn");
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving PDF...';
  btn.disabled = true;

  const element = document.getElementById("a4Paper");
  const cls = document
    .getElementById("className")
    .value.replace(/[\\/:*?"<>|]/g, "-");
  const sub = document
    .getElementById("subject")
    .value.replace(/[\\/:*?"<>|]/g, "-");

  const opt = {
    margin: 0.2, // Tiny margin so A4 design fits perfectly
    filename: `${cls}_${sub}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
  };

  // Magic line that fixes your PDF Render crash!
  html2pdf()
    .set(opt)
    .from(element)
    .save()
    .then(() => {
      btn.innerHTML = '<i class="fa-solid fa-file-pdf"></i> Instant PDF Export';
      btn.disabled = false;
    });
}

document
  .getElementById("downloadWordBtn")
  .addEventListener("click", downloadWordDocument);
document
  .getElementById("downloadPdfBtn")
  .addEventListener("click", downloadPdfDocument);

// BACK BUTTON
document.getElementById("backToEditBtn").addEventListener("click", () => {
  document.getElementById("previewState").classList.add("hidden");
  document.getElementById("inputState").classList.remove("hidden");
  document.getElementById("rightPanelTitle").innerText =
    "Source Material & AI Magic";
  document.getElementById("rightPanelBadge").innerText = "Text, PDFs & Images";
});
