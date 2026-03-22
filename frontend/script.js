document.getElementById("testDate").valueAsDate = new Date();

const networkStatus = document.getElementById("networkStatus");
const networkText = document.getElementById("networkText");
const generateBtn = document.getElementById("generateBtn");
const generatePdfBtn = document.getElementById("generatePdfBtn");

// ==========================================
// NETWORK STATUS
// ==========================================
function updateOnlineStatus() {
  if (navigator.onLine) {
    networkStatus.classList.remove("offline");
    networkText.innerText = "System Online";
    generateBtn.disabled = false;
    generatePdfBtn.disabled = false;
    generateBtn.innerHTML =
      '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Generate Word (.docx)</span>';
    generatePdfBtn.innerHTML =
      '<i class="fa-solid fa-file-pdf"></i> <span>Export as PDF</span>';
  } else {
    networkStatus.classList.add("offline");
    networkText.innerText = "Offline - Check Internet";
    generateBtn.disabled = true;
    generatePdfBtn.disabled = true;
    generateBtn.innerHTML =
      '<i class="fa-solid fa-wifi"></i> <span>No Internet</span>';
    generatePdfBtn.innerHTML =
      '<i class="fa-solid fa-wifi"></i> <span>No Internet</span>';
  }
}
window.addEventListener("online", updateOnlineStatus);
window.addEventListener("offline", updateOnlineStatus);
updateOnlineStatus();

// ==========================================
// SMART UI: EXAM PATTERN LOGIC
// ==========================================
document.getElementById("examPattern").addEventListener("change", function (e) {
  const boardOptions = document.getElementById("boardExtraOptions");
  if (e.target.value === "board") {
    boardOptions.classList.remove("hidden");
  } else {
    boardOptions.classList.add("hidden");
  }
});

// ==========================================
// FILE DRAG & DROP + CLIPBOARD PASTE
// ==========================================
let selectedFiles = [];
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const previewContainer = document.getElementById("previewContainer");

document.addEventListener("paste", (e) => {
  const items = (e.clipboardData || e.originalEvent.clipboardData).items;
  let filesAdded = false;

  for (let index in items) {
    const item = items[index];
    if (item.kind === "file" && item.type.startsWith("image/")) {
      const blob = item.getAsFile();
      if (selectedFiles.length >= 10) {
        alert("Maximum 10 files allowed at once.");
        break;
      }
      const file = new File([blob], `pasted_screenshot_${Date.now()}.png`, {
        type: item.type,
      });
      selectedFiles.push(file);
      filesAdded = true;
    }
  }

  if (filesAdded) {
    renderPreviews();
    dropZone.classList.add("dragover");
    setTimeout(() => dropZone.classList.remove("dragover"), 300);
  }
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
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    handleFiles(e.dataTransfer.files);
  }
});

fileInput.addEventListener("change", (e) => {
  handleFiles(e.target.files);
  fileInput.value = "";
});

function handleFiles(files) {
  for (let i = 0; i < files.length; i++) {
    if (selectedFiles.length >= 10) {
      alert("Maximum 10 files allowed at once.");
      break;
    }
    selectedFiles.push(files[i]);
  }
  renderPreviews();
}

function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderPreviews();
}

function renderPreviews() {
  if (selectedFiles.length > 0) {
    previewContainer.classList.remove("hidden");
  } else {
    previewContainer.classList.add("hidden");
  }

  previewContainer.innerHTML = "";
  selectedFiles.forEach((file, index) => {
    const item = document.createElement("div");
    item.className = "preview-item";

    const removeBtn = document.createElement("button");
    removeBtn.className = "remove-file-btn";
    removeBtn.innerHTML = "X";
    removeBtn.onclick = (e) => {
      e.stopPropagation();
      removeFile(index);
    };
    item.appendChild(removeBtn);

    if (file.type.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      item.appendChild(img);
    } else if (file.type === "application/pdf") {
      const icon = document.createElement("i");
      icon.className = "fa-solid fa-file-pdf pdf-icon";
      const name = document.createElement("div");
      name.className = "file-name";
      name.innerText = file.name;
      item.appendChild(icon);
      item.appendChild(name);
    } else {
      const icon = document.createElement("i");
      icon.className = "fa-solid fa-file unknown-icon";
      const name = document.createElement("div");
      name.className = "file-name";
      name.innerText = file.name;
      item.appendChild(icon);
      item.appendChild(name);
    }
    previewContainer.appendChild(item);
  });
}

// ==========================================
// SMART PROGRESS BAR
// ==========================================
let countdownInterval = null;
let simulatedProgress = null;

function startProgressBar() {
  const pContainer = document.getElementById("progressContainer");
  const pFill = document.getElementById("progressBar");
  const pText = document.getElementById("progressPercent");
  const pMsg = document.getElementById("progressText");

  pContainer.classList.remove("hidden");
  pFill.classList.remove("error-bar", "success-bar");
  pFill.style.width = "0%";
  pText.innerText = "0%";
  pMsg.innerText = "Extracting text and analyzing logic...";

  let progress = 0;
  let stuckAt90Count = 0;

  if (simulatedProgress) clearInterval(simulatedProgress);
  simulatedProgress = setInterval(() => {
    if (progress < 90) {
      progress += Math.floor(Math.random() * 5) + 1;
      if (progress > 90) progress = 90;

      pFill.style.width = progress + "%";
      pText.innerText = progress + "%";

      if (progress > 40 && progress <= 70)
        pMsg.innerText = "Structuring MCQ and Short Questions...";
      if (progress > 70 && progress < 90)
        pMsg.innerText = "Formatting Document Layout...";
    } else if (progress === 90) {
      stuckAt90Count++;
      if (stuckAt90Count === 6)
        pMsg.innerHTML =
          "Generating questions... AI is doing deep analysis <i class='fa-solid fa-spinner fa-spin'></i>";
      if (stuckAt90Count === 18)
        pMsg.innerHTML =
          "Almost there! Large data takes a bit longer... <i class='fa-solid fa-spinner fa-spin'></i>";
    }
  }, 800);
}

function completeProgressBar(isPdf = false) {
  clearInterval(simulatedProgress);
  const pFill = document.getElementById("progressBar");
  const pText = document.getElementById("progressPercent");
  const pMsg = document.getElementById("progressText");

  pFill.classList.add("success-bar");
  pFill.style.width = "100%";
  pText.innerText = "100%";

  setTimeout(() => {
    pMsg.innerText = isPdf
      ? "PDF Ready! Downloading..."
      : "Completed! Downloading...";
    setTimeout(() => {
      document.getElementById("progressContainer").classList.add("hidden");
      pFill.classList.remove("success-bar");
      pFill.style.width = "0%";
      document.getElementById("bookText").value = "";
      document.getElementById("syllabus").value = "";
      selectedFiles = [];
      renderPreviews();
    }, 2500);
  }, 600);
}

function errorProgressBar(msg) {
  if (simulatedProgress) clearInterval(simulatedProgress);
  const pFill = document.getElementById("progressBar");
  pFill.classList.add("error-bar");
  pFill.style.width = "100%";
  document.getElementById("progressPercent").innerText = "Paused";
  document.getElementById("progressText").innerHTML =
    `<span style='color:#dc2626;'>${msg}</span>`;
}
// ==========================================
// ✅ BUILD FORM DATA
// ==========================================
function buildFormData(exportType = "docx") {
  const textVal = document.getElementById("bookText").value.trim();

  const formData = new FormData();
  formData.append("academy_name", document.getElementById("academyName").value);
  formData.append("subject", document.getElementById("subject").value);
  formData.append("class_name", document.getElementById("className").value);
  formData.append("test_date", document.getElementById("testDate").value);
  formData.append(
    "time_allowed",
    document.getElementById("timeAllowed").value + " min",
  );
  formData.append("syllabus", document.getElementById("syllabus").value);
  formData.append("bilingual", document.getElementById("bilingual").value);
  formData.append(
    "template_style",
    document.getElementById("templateStyle").value,
  );

  const examPattern = document.getElementById("examPattern").value;
  formData.append("exam_pattern", examPattern);

  // Agar board hai toh extra groups bhejey ga, warna 1 group bhejey ga
  if (examPattern === "board") {
    formData.append(
      "short_groups",
      document.getElementById("shortGroups").value,
    );
  } else {
    formData.append("short_groups", "1");
  }

  formData.append("short_total", document.getElementById("shortTotal").value);
  formData.append(
    "short_attempt",
    document.getElementById("shortAttempt").value,
  );
  formData.append("long_total", document.getElementById("longTotal").value);
  formData.append("long_attempt", document.getElementById("longAttempt").value);
  formData.append("long_q_marks", document.getElementById("longMarks").value);

  formData.append(
    "magic_prompt",
    document.getElementById("magicPrompt").value.trim(),
  );
  formData.append(
    "generate_answer_key",
    document.getElementById("generateAnswerKey").checked ? "yes" : "no",
  );
  formData.append("text", textVal);

  selectedFiles.forEach((file) => {
    formData.append("files", file);
  });

  return formData;
}

// ==========================================
// MAIN GENERATION API CALL
// ==========================================
const BASE_URL = "https://ai-test-generator-2hsf.onrender.com";

async function processTestGeneration(
  formData,
  isAutoRetry = false,
  isPdf = false,
) {
  const statusArea = document.getElementById("statusArea");
  const endpoint = isPdf
    ? `${BASE_URL}/generate-pdf`
    : `${BASE_URL}/generate-test`;
  const fileExt = isPdf ? "pdf" : "docx";

  generateBtn.disabled = true;
  generatePdfBtn.disabled = true;

  if (isPdf) {
    generatePdfBtn.innerHTML = isAutoRetry
      ? '<i class="fa-solid fa-rotate-right fa-spin"></i> <span>Retrying...</span>'
      : '<i class="fa-solid fa-spinner fa-spin"></i> <span>Generating PDF...</span>';
  } else {
    generateBtn.innerHTML = isAutoRetry
      ? '<i class="fa-solid fa-rotate-right fa-spin"></i> <span>Retrying Now...</span>'
      : '<i class="fa-solid fa-spinner fa-spin"></i> <span>Generating...</span>';
  }

  statusArea.classList.add("hidden");
  if (countdownInterval) clearInterval(countdownInterval);
  if (!isAutoRetry) startProgressBar();
  else {
    document.getElementById("progressText").innerText =
      "Restarting AI analysis...";
    document.getElementById("progressBar").classList.remove("error-bar");
  }

  try {
    const response = await fetch(endpoint, { method: "POST", body: formData });

    if (!response.ok) {
      const errText = await response.text();
      if (errText.includes("RATE_LIMIT_WAIT")) {
        let waitSeconds = 45;
        const match = errText.match(/RATE_LIMIT_WAIT:(\d+)/);
        if (match) waitSeconds = parseInt(match[1]);

        errorProgressBar(`API Limit Hit. Waiting...`);

        countdownInterval = setInterval(() => {
          waitSeconds--;
          document.getElementById("progressText").innerHTML =
            `⚠️ API Limit. <b style='color:#dc2626;'>Auto-retrying in ${waitSeconds}s</b>`;
          document.getElementById("progressPercent").innerText =
            waitSeconds + "s";
          if (waitSeconds <= 0) {
            clearInterval(countdownInterval);
            processTestGeneration(formData, true, isPdf);
          }
        }, 1000);
        return;
      }
      throw new Error(`Server Error: ${errText}`);
    }

    const blob = await response.blob();
    const classVal = document.getElementById("className").value.trim();
    const subjectVal = document.getElementById("subject").value.trim();
    const syllabusVal = document.getElementById("syllabus").value.trim();
    const cleanStr = (str) => str.replace(/[\\/:*?"<>|]/g, "-");
    const filename = `${cleanStr(classVal)} ${cleanStr(subjectVal)} ${cleanStr(syllabusVal)}.${fileExt}`;

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    completeProgressBar(isPdf);

    generateBtn.disabled = false;
    generatePdfBtn.disabled = false;
    generateBtn.innerHTML =
      '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Generate Another Test</span>';
    generatePdfBtn.innerHTML =
      '<i class="fa-solid fa-file-pdf"></i> <span>Export as PDF</span>';
  } catch (error) {
    console.error("Error:", error);
    errorProgressBar("Failed to generate.");
    statusArea.classList.remove("hidden");
    statusArea.classList.add("error");
    document.getElementById("statusMessage").innerText =
      `❌ Error: ${error.message}`;

    generateBtn.disabled = false;
    generatePdfBtn.disabled = false;
    generateBtn.innerHTML =
      '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Generate AI Test Paper</span>';
    generatePdfBtn.innerHTML =
      '<i class="fa-solid fa-file-pdf"></i> <span>Export as PDF</span>';
  }
}

document.getElementById("testForm").addEventListener("submit", function (e) {
  e.preventDefault();
  if (!navigator.onLine) return alert("No internet connection.");
  const textVal = document.getElementById("bookText").value.trim();
  if (!textVal && selectedFiles.length === 0)
    return alert("⚠️ Please provide Source Material before generating!");
  processTestGeneration(buildFormData("docx"), false, false);
});

document
  .getElementById("generatePdfBtn")
  .addEventListener("click", function () {
    if (!navigator.onLine) return alert("No internet connection.");
    const textVal = document.getElementById("bookText").value.trim();
    if (!textVal && selectedFiles.length === 0)
      return alert("⚠️ Please provide Source Material before generating!");
    processTestGeneration(buildFormData("pdf"), false, true);
  });
