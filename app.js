const modePresets = {
  Celadon: {
    positive: "celadon ceramic vessel, museum-grade product photography, glossy green glaze, fine crackle texture, clean neutral background, soft studio lighting, same exact object, coherent camera orbit, one intact vessel only, spout body arch-handle lid and knob must stay attached and rotate together, highly detailed",
    negative: "deformed vessel, repeated viewpoint, duplicate object, detached spout, detached handle, misaligned arch handle, wrong spout attachment, floating lid, broken ceramic, asymmetrical body, blur, low quality",
    views: [
      { name: "正面主视", hint: "标准产品主视图，器身正对镜头，壶嘴和提梁关系清楚。", horizontal: 0, vertical: 0, zoom: 3.2 },
      { name: "背面视图", hint: "标准背视图，突出器身背部轮廓，避免与正面重复。", horizontal: 180, vertical: 0, zoom: 3.2 },
      { name: "顶视图", hint: "标准俯视图，重点检查提梁、壶盖、壶嘴与壶身连接是否一致。", horizontal: 90, vertical: 55, zoom: 3.6 },
      { name: "三分之四视图", hint: "标准三分之四产品视角，兼顾器身体积与壶嘴方向。", horizontal: 45, vertical: 12, zoom: 3.2 }
    ]
  },
  Pet: {
    positive: "same pet, realistic animal portrait, consistent fur pattern, clean studio background, soft natural lighting, coherent camera orbit, stable anatomy, detailed eyes and fur, identity preserved",
    negative: "extra limbs, deformed anatomy, duplicate body parts, wrong fur pattern, mismatched face, blur, low quality",
    views: [
      { name: "正面", hint: "标准正面展示。", horizontal: 0, vertical: 0, zoom: 1.0 },
      { name: "左前", hint: "轻微左前视角。", horizontal: 330, vertical: 6, zoom: 1.0 },
      { name: "右前", hint: "轻微右前视角。", horizontal: 30, vertical: 6, zoom: 1.0 },
      { name: "侧面", hint: "标准侧面展示。", horizontal: 90, vertical: 0, zoom: 1.0 },
      { name: "背面", hint: "标准背面展示。", horizontal: 180, vertical: 0, zoom: 0.98 },
      { name: "俯视", hint: "轻微俯视。", horizontal: 0, vertical: 35, zoom: 1.02 }
    ]
  },
  Human: {
    positive: "same person, realistic portrait, consistent face identity, clean editorial background, soft cinematic lighting, coherent camera orbit, stable anatomy, detailed hair and fabric, high fidelity",
    negative: "bad anatomy, deformed face, mismatched limbs, duplicate body parts, blur, low quality",
    views: [
      { name: "正面", hint: "标准正面视角。", horizontal: 0, vertical: 0, zoom: 1.0 },
      { name: "左前", hint: "轻微左前视角。", horizontal: 330, vertical: 4, zoom: 1.02 },
      { name: "右前", hint: "轻微右前视角。", horizontal: 30, vertical: 4, zoom: 1.02 },
      { name: "侧面", hint: "标准侧面视角。", horizontal: 90, vertical: 0, zoom: 1.0 },
      { name: "背面", hint: "标准背面视角。", horizontal: 180, vertical: 0, zoom: 1.0 },
      { name: "俯视", hint: "轻微俯视。", horizontal: 0, vertical: 30, zoom: 1.04 }
    ]
  },
  Industrial: {
    positive: "industrial structure, engineered surfaces, technical product render, clean background, precise geometry, hard-surface detailing, controlled reflections, coherent camera orbit, structural consistency, high detail",
    negative: "warped geometry, broken structure, detached parts, extra parts, blur, low quality",
    views: [
      { name: "正面", hint: "标准正面展示。", horizontal: 0, vertical: 0, zoom: 1.0 },
      { name: "左前", hint: "左前产品角度。", horizontal: 315, vertical: 10, zoom: 0.98 },
      { name: "右前", hint: "右前产品角度。", horizontal: 45, vertical: 10, zoom: 0.98 },
      { name: "侧面", hint: "标准侧视图。", horizontal: 90, vertical: 0, zoom: 1.0 },
      { name: "背面", hint: "标准背视图。", horizontal: 180, vertical: 0, zoom: 1.0 },
      { name: "俯视", hint: "结构俯视图。", horizontal: 0, vertical: 50, zoom: 1.02 }
    ]
  },
  Architecture: {
    positive: "architectural subject, professional archviz, clean facade lines, balanced daylight, realistic materials, stable geometry, coherent camera orbit, controlled perspective, detailed surfaces, high detail",
    negative: "warped building, broken facade, impossible perspective, blur, low quality",
    views: [
      { name: "正立面", hint: "标准正立面。", horizontal: 0, vertical: 0, zoom: 0.95 },
      { name: "左前", hint: "左前透视角。", horizontal: 315, vertical: 12, zoom: 0.92 },
      { name: "右前", hint: "右前透视角。", horizontal: 45, vertical: 12, zoom: 0.92 },
      { name: "侧立面", hint: "侧向立面展示。", horizontal: 90, vertical: 6, zoom: 0.94 },
      { name: "背立面", hint: "背立面展示。", horizontal: 180, vertical: 6, zoom: 0.94 },
      { name: "鸟瞰", hint: "高位俯瞰。", horizontal: 0, vertical: 55, zoom: 0.9 }
    ]
  }
};

const modeSelect = document.querySelector("#mode");
const promptText = document.querySelector("#promptText");
const negativePromptText = document.querySelector("#negativePromptText");
const modeBadge = document.querySelector("#modeBadge");
const payloadPreview = document.querySelector("#payloadPreview");
const copyPromptButton = document.querySelector("#copyPrompt");
const resetViewsButton = document.querySelector("#resetViews");
const generateButton = document.querySelector("#generateButton");
const statusBox = document.querySelector("#statusBox");
const imageUpload = document.querySelector("#imageUpload");
const uploadPreview = document.querySelector("#uploadPreview");
const uploadEmpty = document.querySelector("#uploadEmpty");
const refreshGalleryButton = document.querySelector("#refreshGallery");
const totalPreview = document.querySelector("#totalPreview");
const totalEmpty = document.querySelector("#totalEmpty");
const sheetPreview = document.querySelector("#sheetPreview");
const sheetEmpty = document.querySelector("#sheetEmpty");
const singleGallery = document.querySelector("#singleGallery");
const singleEmpty = document.querySelector("#singleEmpty");
const viewControls = document.querySelector("#viewControls");

let uploadDataUrl = "";
let currentJobId = "";
let pollTimer = null;
let currentViews = [];
let currentResult = null;

Object.keys(modePresets).forEach((mode) => {
  const option = document.createElement("option");
  option.value = mode;
  option.textContent = mode;
  modeSelect.appendChild(option);
});

function setStatus(message, kind = "idle") {
  statusBox.textContent = message;
  statusBox.className = `status-box status-${kind}`;
}

function setImageState(imgEl, emptyEl, src) {
  if (!src) {
    imgEl.removeAttribute("src");
    imgEl.style.display = "none";
    emptyEl.style.display = "flex";
    return;
  }
  imgEl.onerror = () => {
    imgEl.style.display = "none";
    emptyEl.style.display = "flex";
  };
  imgEl.onload = () => {
    imgEl.style.display = "block";
    emptyEl.style.display = "none";
  };
  imgEl.src = `${src}${src.includes("?") ? "&" : "?"}t=${Date.now()}`;
}

function clearResults() {
  currentResult = null;
  setImageState(totalPreview, totalEmpty, "");
  setImageState(sheetPreview, sheetEmpty, "");
  singleGallery.innerHTML = "";
  singleEmpty.style.display = "flex";
}

function renderResult(job) {
  currentResult = job;
  setImageState(totalPreview, totalEmpty, job.total_url || "");
  setImageState(sheetPreview, sheetEmpty, job.sheet_url || "");

  singleGallery.innerHTML = "";
  const singles = Array.isArray(job.single_paths) ? job.single_paths : [];
  if (singles.length === 0) {
    singleEmpty.style.display = "flex";
    return;
  }

  singleEmpty.style.display = "none";
  singles.forEach((entry, index) => {
    const card = document.createElement("div");
    card.className = "thumb-card";

    const img = document.createElement("img");
    img.src = `${entry.url}?t=${Date.now()}`;

    const label = document.createElement("span");
    label.textContent = `${entry.name || `视角 ${index + 1}`} / 水平 ${entry.horizontal} / 垂直 ${entry.vertical} / 缩放 ${Number(entry.zoom).toFixed(1)}`;

    card.append(img, label);
    singleGallery.appendChild(card);
  });
}

function cloneViews(mode) {
  return modePresets[mode].views.map((view) => ({ ...view }));
}

function buildViewControls() {
  viewControls.innerHTML = "";
  currentViews.forEach((view, index) => {
    const card = document.createElement("div");
    card.className = "view-card";

    const title = document.createElement("h3");
    title.textContent = `视角 ${index + 1} · ${view.name}`;

    const hint = document.createElement("p");
    hint.textContent = view.hint;

    const hLabel = document.createElement("label");
    hLabel.textContent = "水平角度";
    const hInput = document.createElement("input");
    hInput.type = "range";
    hInput.min = "0";
    hInput.max = "360";
    hInput.step = "1";
    hInput.value = String(view.horizontal);
    const hValue = document.createElement("output");
    hValue.textContent = String(view.horizontal);

    const vLabel = document.createElement("label");
    vLabel.textContent = "垂直角度";
    const vInput = document.createElement("input");
    vInput.type = "range";
    vInput.min = "-90";
    vInput.max = "90";
    vInput.step = "1";
    vInput.value = String(view.vertical);
    const vValue = document.createElement("output");
    vValue.textContent = String(view.vertical);

    const zLabel = document.createElement("label");
    zLabel.textContent = "缩放倍率";
    const zInput = document.createElement("input");
    zInput.type = "range";
    zInput.min = "0.5";
    zInput.max = "6.0";
    zInput.step = "0.01";
    zInput.value = String(view.zoom);
    const zValue = document.createElement("output");
    zValue.textContent = Number(view.zoom).toFixed(2);

    hInput.addEventListener("input", () => {
      currentViews[index].horizontal = Number(hInput.value);
      hValue.textContent = hInput.value;
      render();
    });

    vInput.addEventListener("input", () => {
      currentViews[index].vertical = Number(vInput.value);
      vValue.textContent = vInput.value;
      render();
    });

    zInput.addEventListener("input", () => {
      currentViews[index].zoom = Number(zInput.value);
      zValue.textContent = Number(zInput.value).toFixed(2);
      render();
    });

    card.append(title, hint, hLabel, hInput, hValue, vLabel, vInput, vValue, zLabel, zInput, zValue);
    viewControls.appendChild(card);
  });
}

function getPayload() {
  return {
    mode: modeSelect.value,
    positive_prompt: promptText.value.trim(),
    negative_prompt: negativePromptText.value.trim(),
    views: currentViews.map((view) => ({
      name: view.name,
      horizontal: Number(view.horizontal),
      vertical: Number(view.vertical),
      zoom: Number(Number(view.zoom).toFixed(2))
    })),
    imageData: uploadDataUrl
  };
}

function render() {
  modeBadge.textContent = modeSelect.value;
  payloadPreview.textContent = JSON.stringify({
    node: "PolyView",
    ...getPayload(),
    imageData: uploadDataUrl ? "[base64 image omitted]" : ""
  }, null, 2);
}

async function pollJob(jobId) {
  if (pollTimer) {
    clearTimeout(pollTimer);
  }
  const response = await fetch(`./api/jobs/${jobId}`);
  const job = await response.json();

  if (job.status === "completed") {
    setStatus("生成完成。", "idle");
    generateButton.disabled = false;
    renderResult(job);
    return;
  }

  if (job.status === "error" || job.status === "timeout") {
    setStatus(`生成失败：${job.error || job.status}`, "error");
    generateButton.disabled = false;
    return;
  }

  setStatus(`任务状态：${job.status}`, "running");
  pollTimer = setTimeout(() => pollJob(jobId), 1800);
}

async function submitGenerate() {
  if (!uploadDataUrl) {
    setStatus("请先上传一张基础图像。", "error");
    return;
  }

  generateButton.disabled = true;
  clearResults();
  setStatus("正在提交到 ComfyUI 并等待生成结果。", "running");

  try {
    const response = await fetch("./api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload())
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "生成失败");
    }

    currentJobId = payload.job_id;
    setStatus("任务已进入队列，正在执行。", "running");
    await pollJob(currentJobId);
  } catch (error) {
    setStatus(`生成失败：${error.message}`, "error");
    generateButton.disabled = false;
  }
}

function resetMode(mode) {
  const preset = modePresets[mode];
  promptText.value = preset.positive;
  negativePromptText.value = preset.negative;
  currentViews = cloneViews(mode);
  buildViewControls();
  clearResults();
  render();
}

modeSelect.addEventListener("change", () => {
  resetMode(modeSelect.value);
});

promptText.addEventListener("input", render);
negativePromptText.addEventListener("input", render);

imageUpload.addEventListener("change", () => {
  const file = imageUpload.files?.[0];
  if (!file) {
    uploadDataUrl = "";
    uploadPreview.style.display = "none";
    uploadEmpty.style.display = "flex";
    render();
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    uploadDataUrl = String(reader.result || "");
    uploadPreview.src = uploadDataUrl;
    uploadPreview.style.display = "block";
    uploadEmpty.style.display = "none";
    render();
  };
  reader.readAsDataURL(file);
});

copyPromptButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(promptText.value);
  copyPromptButton.textContent = "已复制";
  setTimeout(() => {
    copyPromptButton.textContent = "复制正向词";
  }, 1200);
});

resetViewsButton.addEventListener("click", () => {
  resetMode(modeSelect.value);
});

refreshGalleryButton.addEventListener("click", () => {
  if (currentResult) {
    renderResult(currentResult);
  }
});

generateButton.addEventListener("click", submitGenerate);

modeSelect.value = "Celadon";
resetMode("Celadon");
setStatus("等待任务", "idle");
