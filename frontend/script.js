document.getElementById("testDate").valueAsDate = new Date();

let selectedFiles = [];
let currentDocxFile = null;
const BASE_URL = "https://ai-test-generator-2hsf.onrender.com";

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
  } else {
    boardGroup.classList.add("hidden");
  }
});

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
  } else {
    fd.append("short_groups", "1");
  }

  fd.append("short_total", document.getElementById("shortTotal").value);
  fd.append("short_attempt", document.getElementById("shortAttempt").value);
  fd.append("long_total", document.getElementById("longTotal").value);
  fd.append("long_attempt", document.getElementById("longAttempt").value);
  fd.append("long_q_marks", document.getElementById("longMarks").value);

  return fd;
}

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
    btn.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing & Processing...';
    pContainer.classList.remove("hidden");

    let percent = 0;
    pFill.style.width = "0%";
    pPercent.innerText = "0%";
    pText.innerText = "Extracting AI Data...";

    simProgress = setInterval(() => {
      if (percent < 90) {
        percent += Math.floor(Math.random() * 4) + 1;
        if (percent > 90) percent = 90;

        pFill.style.width = percent + "%";
        pPercent.innerText = percent + "%";

        if (percent > 30) pText.innerText = "Drafting Questions & Sections...";
        if (percent > 65) pText.innerText = "Formatting MS Word Document...";
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

      clearInterval(simProgress);
      pFill.style.width = "100%";
      pPercent.innerText = "100%";
      pText.innerText = "Test Paper Ready!";

      setTimeout(() => {
        openPreviewModal(currentDocxFile);
        pContainer.classList.add("hidden");
        btn.disabled = false;
        btn.innerHTML =
          '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Build Interactive Test Paper</span>';
      }, 800);
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

function openPreviewModal(docxFilename) {
  const modal = document.getElementById("previewModal");
  const iframe = document.getElementById("docPreviewFrame");
  const loader = document.getElementById("iframeLoader");

  modal.classList.remove("hidden");
  iframe.classList.add("hidden");
  loader.classList.remove("hidden");

  // 🔥 DOUBLE CACHE BUSTER: ?t=Date.now() forces Microsoft to fetch the NEW file!
  const fileUrl = `${BASE_URL}/get-file/${docxFilename}`;
  const viewerUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}&t=${Date.now()}`;

  iframe.src = viewerUrl;

  iframe.onload = function () {
    setTimeout(() => {
      loader.classList.add("hidden");
      iframe.classList.remove("hidden");
    }, 1500);
  };
}

const closeBtn = document.getElementById("closeModalBtn");
if (closeBtn) {
  closeBtn.addEventListener("click", () => {
    document.getElementById("previewModal").classList.add("hidden");
    document.getElementById("docPreviewFrame").src = "";
  });
}

const wordBtn = document.getElementById("downloadWordBtn");
if (wordBtn) {
  wordBtn.addEventListener("click", () => {
    if (!currentDocxFile) return;
    const url = `${BASE_URL}/get-file/${currentDocxFile}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = currentDocxFile;
    document.body.appendChild(a);
    a.click();
    a.remove();
  });
}

const refineBtn = document.getElementById("aiRefineBtn");
if (refineBtn) {
  refineBtn.addEventListener("click", () => {
    const promptInput = document.getElementById("aiRefinePrompt");
    if (!promptInput || !promptInput.value)
      return alert("Please type an instruction first!");
    alert(
      "AI Editor is processing your request...\n\n(This will dynamically update the DOCX in the next feature patch!)",
    );
  });
}
