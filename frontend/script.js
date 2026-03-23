document.getElementById("testDate").valueAsDate = new Date();

let selectedFiles = [];
let currentDocxFile = null;
let currentPdfFile = null;
let currentAiData = null;

const BASE_URL = "https://ai-test-generator-2hsf.onrender.com";

// ==========================================
// UI & NETWORK STATE
// ==========================================
function updateOnlineStatus() {
  const status = document.getElementById("networkStatus");
  const text = document.getElementById("networkText");
  const btn = document.getElementById("generateTestBtn");
  if (navigator.onLine) {
    status.classList.remove("offline");
    text.innerText = "System Online";
    btn.disabled = false;
    btn.innerHTML =
      '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Build Interactive Test Paper</span>';
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
  fd.append("bilingual", document.getElementById("bilingual").value);
  fd.append("generate_answer_key", "no");

  const pattern = document.getElementById("examPattern").value;
  fd.append("exam_pattern", pattern);
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
    fd.append("long_q_marks", document.getElementById("longMarks").value);
  } else {
    fd.append("short_groups", "1");
    fd.append("short_total", "8");
    fd.append("short_attempt", "5");
    fd.append("long_total", "3");
    fd.append("long_attempt", "2");
    fd.append("long_q_marks", "5");
  }
  return fd;
}

// ==========================================
// RENDER HTML PREVIEW (Matches Word Format)
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

  const cT = (text) => (text ? text.replace(/^\d+[\.\)]\s*/, "").trim() : "");

  let html = `
    <div class="a4-header-block">
        <h1>${acadName}</h1>
        <p>${subj} &nbsp;&nbsp;|&nbsp;&nbsp; ${cls} &nbsp;&nbsp;|&nbsp;&nbsp; ${syll}</p>
    </div>
    <div class="a4-student-info">
        <span>Name: ________________________</span>
        <span>Date: ${formattedDate}</span>
        <span>Time: <u>${time} Min</u></span>
        <span>Max Marks: <u>Calc...</u></span>
    </div>
  `;

  if (data.mcqs && data.mcqs.length > 0) {
    html += `<h3>Multiple Choice Questions</h3><ol>`;
    data.mcqs.forEach((m) => {
      let q = cT(m.q_en || m.question || "");
      if (m.q_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right; font-size:16px;">${m.q_ur}</span><div style="clear:both;"></div>`;
      html += `<li><b>${q}</b><br>
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
    html += `<h3>Short Questions</h3><ol>`;
    data.short_qs.forEach((sq) => {
      let q = cT(sq.text_en || sq.text || "");
      if (sq.text_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right; font-size:16px;">${sq.text_ur}</span><div style="clear:both;"></div>`;
      html += `<li><b>${q}</b></li>`;
    });
    html += `</ol>`;
  }

  if (data.long_qs && data.long_qs.length > 0) {
    html += `<h3>Long Questions</h3><ol>`;
    data.long_qs.forEach((lq) => {
      let q = cT(lq.text_en || lq.text || "");
      q = q.replace(/\\n/g, "<br>");
      if (lq.text_ur)
        q += `<br><span dir="rtl" style="font-family:'Jameel Noori Nastaleeq', Arial; float:right; font-size:16px;">${lq.text_ur}</span><div style="clear:both;"></div>`;
      html += `<li><b>${q}</b></li>`;
    });
    html += `</ol>`;
  }

  document.getElementById("paperContentArea").innerHTML = html;
}

// ==========================================
// MAIN PROCESS: GENERATE TEST
// ==========================================
let simProgress = null;

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

    const btn = document.getElementById("generateTestBtn");
    const pContainer = document.getElementById("progressContainer");
    const pFill = document.getElementById("progressBar");
    const pText = document.getElementById("progressText");
    const pPercent = document.getElementById("progressPercent");

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
    pContainer.classList.remove("hidden");

    // Percentage Progress Bar Animation
    let percent = 0;
    pFill.style.width = "0%";
    pPercent.innerText = "0%";
    pText.innerText = "Extracting AI Data...";

    simProgress = setInterval(() => {
      if (percent < 85) {
        percent += Math.floor(Math.random() * 4) + 1;
        pFill.style.width = percent + "%";
        pPercent.innerText = percent + "%";
        if (percent > 30) pText.innerText = "Drafting Questions...";
        if (percent > 60) pText.innerText = "Formatting Word & PDF Files...";
      }
    }, 600);

    try {
      const response = await fetch(`${BASE_URL}/process-test`, {
        method: "POST",
        body: fd,
      });
      if (!response.ok) throw new Error(await response.text());

      const data = await response.json();
      currentDocxFile = data.docx_filename;
      currentPdfFile = data.pdf_filename;
      currentAiData = data.ai_data;

      // Complete Progress
      clearInterval(simProgress);
      pFill.style.width = "100%";
      pPercent.innerText = "100%";
      pText.innerText = "Test Ready!";

      // Show Modal
      setTimeout(() => {
        renderA4Paper(currentAiData);
        document.getElementById("previewModal").classList.remove("hidden");

        // Reset Progress UI for next time
        pContainer.classList.add("hidden");
        btn.disabled = false;
        btn.innerHTML =
          '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Build Interactive Test Paper</span>';
      }, 500);
    } catch (error) {
      clearInterval(simProgress);
      pFill.style.background = "var(--error)";
      pText.innerText = "Error Occurred";
      alert("Error: " + error.message);
      btn.disabled = false;
      btn.innerHTML =
        '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Try Again</span>';
    }
  });

// ==========================================
// MODAL CLOSE LOGIC
// ==========================================
document.getElementById("closeModalBtn").addEventListener("click", () => {
  document.getElementById("previewModal").classList.add("hidden");
});

// ==========================================
// DOWNLOAD HANDLERS
// ==========================================
async function downloadFile(filename, isPdf) {
  if (!filename) {
    if (isPdf) {
      // Fallback: If backend libreoffice failed, use html2pdf!
      alert("Server PDF conversion skipped. Generating Client-Side PDF...");
      const element = document.getElementById("paperContentArea");
      const cls = document
        .getElementById("className")
        .value.replace(/[\\/:*?"<>|]/g, "-");
      const sub = document
        .getElementById("subject")
        .value.replace(/[\\/:*?"<>|]/g, "-");
      html2pdf()
        .set({
          margin: 0.2,
          filename: `${cls}_${sub}.pdf`,
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
        })
        .from(element)
        .save();
    }
    return;
  }

  // Direct download from backend
  const url = `${BASE_URL}/get-file/${filename}`;
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

document
  .getElementById("downloadWordBtn")
  .addEventListener("click", () => downloadFile(currentDocxFile, false));
document
  .getElementById("downloadPdfBtn")
  .addEventListener("click", () => downloadFile(currentPdfFile, true));

// ==========================================
// AI REFINE BUTTON (Coming in next update)
// ==========================================
document.getElementById("aiRefineBtn").addEventListener("click", () => {
  const prompt = document.getElementById("aiRefinePrompt").value;
  if (!prompt) return alert("Please type an instruction first!");
  alert(
    "AI Editor is currently processing... This will update the DOCX format in the next patch!",
  );
});
