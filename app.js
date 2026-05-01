const modePresets = {
  Celadon: {
    positive: "celadon ceramic vessel, museum-grade product photography, glossy green glaze, fine crackle texture, clean neutral background, soft studio lighting, same exact object, coherent camera orbit, one intact vessel only, spout body arch-handle lid and knob must stay attached and rotate together, highly detailed",
    negative: "deformed vessel, repeated viewpoint, duplicate object, detached spout, detached handle, misaligned arch handle, wrong spout attachment, floating lid, broken ceramic, asymmetrical body, blur, low quality",
    views: [
      { name: "正面主视", hint: "标准产品主视图，器身正对镜头，壶嘴和提梁关系清楚。", zoom: 1.5, steps: 24, cfg: 2.2 },
      { name: "背面视图", hint: "标准背视图，突出器身背部轮廓，避免与正面重复。", zoom: 1.35, steps: 36, cfg: 2.4 },
      { name: "顶视图", hint: "标准俯视图，重点检查提梁、壶盖、壶嘴与壶身连接是否一致。", zoom: 1.5, steps: 20, cfg: 1.8 },
      { name: "四分之三视图", hint: "标准四分之三产品视角，兼顾器身体积与壶嘴方向。", zoom: 2.2, steps: 28, cfg: 2.0 },
      { name: "侧视图", hint: "标准侧视图，展示器皿的侧面轮廓和提梁的侧面形态。", zoom: 1.5, steps: 24, cfg: 2.2 }
    ]
  },
  Pet: {
    positive: "same pet, realistic animal portrait, consistent fur pattern, clean studio background, soft natural lighting, coherent camera orbit, stable anatomy, detailed eyes and fur, identity preserved, high fidelity, 4K",
    negative: "extra limbs, deformed anatomy, duplicate body parts, wrong fur pattern, mismatched face, blurry eyes, deformed ears, low quality, blur, cartoon, illustration",
    views: [
      { name: "正面", hint: "标准正面展示，面部正对镜头，双眼可见。", zoom: 1.2, steps: 28, cfg: 2.8 },
      { name: "左前", hint: "轻微左前视角，展示左侧面部和身体。", zoom: 1.2, steps: 28, cfg: 2.8 },
      { name: "右前", hint: "轻微右前视角，展示右侧面部和身体。", zoom: 1.2, steps: 28, cfg: 2.8 },
      { name: "侧面", hint: "标准侧面展示，完整身体轮廓。", zoom: 1.1, steps: 30, cfg: 2.3 },
      { name: "背面", hint: "标准背面展示，从后方看宠物。", zoom: 1.0, steps: 28, cfg: 2.5 },
      { name: "俯视", hint: "轻微俯视视角，展示宠物姿态。", zoom: 1.1, steps: 28, cfg: 2.6 }
    ]
  },
  Human: {
    positive: "same person, realistic full body portrait, consistent face identity and body shape, clean editorial background, soft cinematic lighting, coherent camera orbit around the entire body, stable anatomy, detailed hair and fabric, full body rotates together, high fidelity, professional photography, 4K",
    negative: "bad anatomy, deformed face, mismatched limbs, duplicate body parts, blurry face, wrong eyes, extra fingers, deformed hands, torso facing wrong direction, head turned but body facing forward, low quality, blur, cartoon",
    views: [
      { name: "正面", hint: "标准正面视角，面部和身体正对镜头。", zoom: 0.85, steps: 40, cfg: 1.5 },
      { name: "左前", hint: "左前视角，身体和头部一起转向左侧。", zoom: 1.3, steps: 35, cfg: 2.3 },
      { name: "右前", hint: "右前视角，身体和头部一起转向右侧。", zoom: 1.3, steps: 35, cfg: 2.3 },
      { name: "侧面", hint: "标准侧面视角，完整身体侧面轮廓。", zoom: 1.2, steps: 32, cfg: 2.2 },
      { name: "背面", hint: "后侧面视角，展示背部和后脑勺。", zoom: 1.2, steps: 32, cfg: 2.2 },
      { name: "俯视", hint: "俯视视角。", zoom: 1.1, steps: 28, cfg: 2.2 }
    ]
  },
  Industrial: {
    positive: "industrial structure, engineered surfaces, technical product render, clean background, precise geometry, hard-surface detailing, controlled reflections, coherent camera orbit, structural consistency, high detail, 4K, sharp edges",
    negative: "warped geometry, broken structure, detached parts, extra parts, soft edges, blurry reflections, low quality, blur, unrealistic materials, cartoon",
    views: [
      { name: "正面", hint: "标准正面展示，正对产品正面。", zoom: 1.2, steps: 28, cfg: 2.2 },
      { name: "左前", hint: "左前产品角度，展示左侧面和正面。", zoom: 1.2, steps: 28, cfg: 2.2 },
      { name: "右前", hint: "右前产品角度，展示右侧面和正面。", zoom: 1.2, steps: 28, cfg: 2.2 },
      { name: "侧面", hint: "标准侧视图，展示侧面结构。", zoom: 1.1, steps: 30, cfg: 2.0 },
      { name: "背面", hint: "标准背视图，展示背面结构。", zoom: 1.1, steps: 28, cfg: 2.2 },
      { name: "俯视", hint: "结构俯视图，展示顶部结构。", zoom: 1.0, steps: 28, cfg: 2.2 }
    ]
  },
  Architecture: {
    positive: "architectural subject, professional archviz, clean facade lines, balanced daylight, realistic materials, stable geometry, coherent camera orbit, controlled perspective, detailed surfaces, high detail, 4K, sharp lines, realistic shadows",
    negative: "warped building, broken facade, impossible perspective, distorted geometry, blurry textures, low quality, blur, cartoon, unrealistic lighting",
    views: [
      { name: "正立面", hint: "标准正立面，正对建筑正面。", zoom: 0.9, steps: 32, cfg: 2.2 },
      { name: "左前", hint: "左前透视角，展示左侧和正面。", zoom: 0.85, steps: 32, cfg: 2.2 },
      { name: "右前", hint: "右前透视角，展示右侧和正面。", zoom: 0.85, steps: 32, cfg: 2.2 },
      { name: "侧立面", hint: "侧向立面展示，展示侧面结构。", zoom: 0.9, steps: 32, cfg: 2.2 },
      { name: "背立面", hint: "背立面展示，展示建筑背面。", zoom: 0.9, steps: 32, cfg: 2.2 },
      { name: "鸟瞰", hint: "高位俯瞰，展示建筑整体布局。", zoom: 0.8, steps: 32, cfg: 2.2 }
    ]
  }
};

const viewAngles = {
  "正面主视": { horizontal: 0, vertical: 10 },
  "背面视图": { horizontal: 180, vertical: 10 },
  "顶视图": { horizontal: 0, vertical: 75 },
  "四分之三视图": { horizontal: 45, vertical: 15 },
  "侧视图": { horizontal: 90, vertical: 10 },
  "正面": { horizontal: 0, vertical: 0 },
  "左前": { horizontal: 315, vertical: 6 },
  "右前": { horizontal: 45, vertical: 6 },
  "侧面": { horizontal: 90, vertical: 0 },
  "背面": { horizontal: 160, vertical: 0 },
  "俯视": { horizontal: 0, vertical: 35 },
  "正立面": { horizontal: 0, vertical: 0 },
  "侧立面": { horizontal: 90, vertical: 6 },
  "背立面": { horizontal: 180, vertical: 6 },
  "鸟瞰": { horizontal: 0, vertical: 55 }
};

const modeSelect = document.querySelector("#mode");
const promptText = document.querySelector("#promptText");
const negativePromptText = document.querySelector("#negativePromptText");
const modeBadge = document.querySelector("#modeBadge");
const payloadPreview = document.querySelector("#payloadPreview");
const copyPromptButton = document.querySelector("#copyPrompt");
const copyNegativeButton = document.querySelector("#copyNegative");
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
let currentViews = [];
let currentResult = null;
let singleResults = {};

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
  imgEl.src = `${src}?t=${Date.now()}`;
}

function clearResults() {
  currentResult = null;
  singleResults = {};
  setImageState(totalPreview, totalEmpty, "");
  setImageState(sheetPreview, sheetEmpty, "");
  renderSingleGallery();
}

function renderSingleGallery() {
  if (!currentViews || currentViews.length === 0) {
    singleGallery.innerHTML = "";
    singleEmpty.style.display = "flex";
    return;
  }

  singleGallery.innerHTML = "";
  let hasAnyImage = false;

  currentViews.forEach((view) => {
    const section = document.createElement("div");
    section.className = "view-section";

    const sectionTitle = document.createElement("h3");
    sectionTitle.className = "view-section-title";
    sectionTitle.textContent = `${view.name}`;
    
    const paramBadge = document.createElement("span");
    paramBadge.className = "view-section-badge";
    paramBadge.textContent = `缩放 ${view.zoom} | 步数 ${view.steps} | CFG ${view.cfg}`;
    sectionTitle.appendChild(paramBadge);
    
    const grid = document.createElement("div");
    grid.className = "view-section-grid";

    const savedResult = singleResults[view.name];
    if (savedResult && savedResult.url) {
      hasAnyImage = true;
      const card = document.createElement("div");
      card.className = "thumb-card";
      
      const img = document.createElement("img");
      img.src = savedResult.url;
      
      const label = document.createElement("span");
      const date = savedResult.created_at ? new Date(savedResult.created_at).toLocaleTimeString() : "";
      label.textContent = `${view.name} | 生成于 ${date}`;
      
      const downloadBtn = document.createElement("button");
      downloadBtn.textContent = "📥 下载图片";
      downloadBtn.className = "download-btn";
      downloadBtn.onclick = (e) => {
        e.preventDefault();
        const link = document.createElement("a");
        link.href = savedResult.url;
        link.download = `${view.name}_${Date.now()}.png`;
        link.click();
      };
      
      card.appendChild(img);
      card.appendChild(label);
      card.appendChild(downloadBtn);
      grid.appendChild(card);
    } else {
      const emptyCard = document.createElement("div");
      emptyCard.className = "thumb-card empty-card";
      emptyCard.innerHTML = '<span style="color: #aaa;">尚未生成</span>';
      grid.appendChild(emptyCard);
    }

    section.appendChild(sectionTitle);
    section.appendChild(grid);
    singleGallery.appendChild(section);
  });

  singleEmpty.style.display = hasAnyImage ? "none" : "flex";
}

function updateSingleResult(viewName, imageUrl) {
  if (!imageUrl) return;
  singleResults[viewName] = {
    url: imageUrl,
    created_at: Date.now()
  };
  renderSingleGallery();
}

function renderResult(job) {
  currentResult = job;
  setImageState(totalPreview, totalEmpty, job.total_url || "");
  setImageState(sheetPreview, sheetEmpty, job.sheet_url || "");

  const singles = Array.isArray(job.single_paths) ? job.single_paths : [];
  singles.forEach((entry) => {
    if (entry && entry.name && entry.url) {
      updateSingleResult(entry.name, entry.url);
    }
  });
}

function cloneViews(mode) {
  const preset = modePresets[mode];
  if (!preset) return [];
  return preset.views.map(view => ({ ...view }));
}

function getAngleForView(viewName) {
  return viewAngles[viewName] || { horizontal: 0, vertical: 10 };
}

function getPayload() {
  return {
    mode: modeSelect.value,
    positive_prompt: promptText.value.trim(),
    negative_prompt: negativePromptText.value.trim(),
    views: currentViews.map((view) => {
      const angle = getAngleForView(view.name);
      return {
        name: view.name,
        horizontal: angle.horizontal,
        vertical: angle.vertical,
        zoom: Number(view.zoom),
        steps: Number(view.steps),
        cfg: Number(view.cfg)
      };
    }),
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

async function pollJob(jobId, isSingle = false, viewName = null, buttonElement = null) {
  const startTime = Date.now();
  const timeout = 60 * 60 * 1000;
  
  while (true) {
    if (Date.now() - startTime > timeout) {
      setStatus(`任务超时`, "error");
      if (buttonElement) {
        buttonElement.disabled = false;
        buttonElement.textContent = "单独生成";
      }
      generateButton.disabled = false;
      return;
    }
    
    try {
      const response = await fetch(`./api/jobs/${jobId}`);
      const job = await response.json();

      if (job.status === "completed") {
        if (isSingle && viewName) {
          if (job.single_paths && job.single_paths.length > 0) {
            const matched = job.single_paths.find(p => p.name === viewName);
            if (matched && matched.url) {
              updateSingleResult(viewName, matched.url);
            } else if (job.single_paths[0] && job.single_paths[0].url) {
              updateSingleResult(viewName, job.single_paths[0].url);
            }
          }
          setStatus(`「${viewName}」生成完成`, "idle");
        } else {
          renderResult(job);
          setStatus("生成完成", "idle");
        }
        if (buttonElement) {
          buttonElement.disabled = false;
          buttonElement.textContent = "单独生成";
        }
        generateButton.disabled = false;
        return;
      }

      if (job.status === "error" || job.status === "timeout") {
        setStatus(`生成失败：${job.error || job.status}`, "error");
        if (buttonElement) {
          buttonElement.disabled = false;
          buttonElement.textContent = "单独生成";
        }
        generateButton.disabled = false;
        return;
      }

      setStatus(`生成中... ${job.status}`, "running");
      await new Promise(resolve => setTimeout(resolve, 1500));
    } catch (error) {
      console.error("pollJob error:", error);
      setStatus(`轮询失败`, "error");
      if (buttonElement) {
        buttonElement.disabled = false;
        buttonElement.textContent = "单独生成";
      }
      generateButton.disabled = false;
      return;
    }
  }
}

async function submitSingleGenerate(view, buttonElement) {
  if (!uploadDataUrl) {
    setStatus("请先上传一张基础图像", "error");
    return;
  }

  const payload = {
    mode: modeSelect.value,
    positive_prompt: promptText.value.trim(),
    negative_prompt: negativePromptText.value.trim(),
    views: [{
      name: view.name,
      horizontal: getAngleForView(view.name).horizontal,
      vertical: getAngleForView(view.name).vertical,
      zoom: view.zoom,
      steps: view.steps,
      cfg: view.cfg
    }],
    imageData: uploadDataUrl
  };

  setStatus(`正在生成「${view.name}」...`, "running");
  
  const originalText = buttonElement.textContent;
  buttonElement.disabled = true;
  buttonElement.textContent = '生成中...';

  try {
    const response = await fetch("./api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "生成失败");
    }

    await pollJob(result.job_id, true, view.name, buttonElement);
  } catch (error) {
    setStatus(`生成失败：${error.message}`, "error");
    buttonElement.disabled = false;
    buttonElement.textContent = originalText;
  }
}

async function submitGenerate() {
  if (!uploadDataUrl) {
    setStatus("请先上传一张基础图像", "error");
    return;
  }

  generateButton.disabled = true;
  clearResults();
  setStatus("正在提交完整生成任务...", "running");

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
    await pollJob(currentJobId, false, null, null);
  } catch (error) {
    setStatus(`生成失败：${error.message}`, "error");
    generateButton.disabled = false;
  }
}

function refreshResults() {
  if (currentResult) {
    renderResult(currentResult);
  }
  renderSingleGallery();
}

function resetMode(mode) {
  const preset = modePresets[mode];
  if (!preset) return;
  promptText.value = preset.positive;
  negativePromptText.value = preset.negative;
  currentViews = cloneViews(mode);
  buildViewControls();
  clearResults();
  render();
  renderSingleGallery();
  
  const viewCount = currentViews.length;
  const viewNames = currentViews.map(v => v.name).join('、');
  const titleElement = document.getElementById('viewControlTitle');
  if (titleElement) titleElement.textContent = `${viewCount}视图控制`;
  const subheadElement = document.getElementById('viewControlSubhead');
  if (subheadElement) {
    subheadElement.textContent = `当前模式「${mode}」包含 ${viewCount} 个视角：${viewNames}。每个视角可单独生成。`;
  }
  const generateBtn = document.getElementById('generateButton');
  if (generateBtn) generateBtn.textContent = `完整生成（${viewCount}个视角）`;
}

function buildViewControls() {
  viewControls.innerHTML = "";
  currentViews.forEach((view, index) => {
    const card = document.createElement("div");
    card.className = "view-card";

    const title = document.createElement("h3");
    title.textContent = `${view.name}`;

    const hint = document.createElement("p");
    hint.textContent = view.hint;

    const angleInfo = getAngleForView(view.name);
    const angleDisplay = document.createElement("p");
    angleDisplay.style.fontSize = "11px";
    angleDisplay.style.color = "#6a756f";
    angleDisplay.style.margin = "0 0 12px 0";
    angleDisplay.style.padding = "4px 8px";
    angleDisplay.style.background = "#f0ece4";
    angleDisplay.style.borderRadius = "8px";
    angleDisplay.innerHTML = `📷 固定视角：水平 ${angleInfo.horizontal}° / 垂直 ${angleInfo.vertical}°`;

    const zLabel = document.createElement("label");
    zLabel.textContent = "缩放倍率 (Zoom)";
    const zInput = document.createElement("input");
    zInput.type = "range";
    zInput.min = "0.5";
    zInput.max = "4.0";
    zInput.step = "0.01";
    zInput.value = String(view.zoom);
    const zValue = document.createElement("output");
    zValue.textContent = Number(view.zoom).toFixed(2);

    const sLabel = document.createElement("label");
    sLabel.textContent = "迭代步数 (Steps)";
    const sInput = document.createElement("input");
    sInput.type = "range";
    sInput.min = "8";
    sInput.max = "50";
    sInput.step = "1";
    sInput.value = String(view.steps);
    const sValue = document.createElement("output");
    sValue.textContent = String(view.steps);

    const cLabel = document.createElement("label");
    cLabel.textContent = "提示词权重 (CFG)";
    const cInput = document.createElement("input");
    cInput.type = "range";
    cInput.min = "1.0";
    cInput.max = "3.5";
    cInput.step = "0.05";
    cInput.value = String(view.cfg);
    const cValue = document.createElement("output");
    cValue.textContent = Number(view.cfg).toFixed(2);

    const singleBtn = document.createElement("button");
    singleBtn.type = "button";
    singleBtn.className = "single-generate-btn";
    singleBtn.textContent = "单独生成";
    singleBtn.style.marginTop = "16px";
    singleBtn.style.background = "#6d8d87";
    singleBtn.style.width = "100%";
    
    singleBtn.addEventListener("click", async () => {
      const currentView = {
        name: view.name,
        zoom: Number(zInput.value),
        steps: Number(sInput.value),
        cfg: Number(cInput.value)
      };
      await submitSingleGenerate(currentView, singleBtn);
    });

    zInput.addEventListener("input", () => {
      currentViews[index].zoom = Number(zInput.value);
      zValue.textContent = Number(zInput.value).toFixed(2);
      render();
    });

    sInput.addEventListener("input", () => {
      currentViews[index].steps = Number(sInput.value);
      sValue.textContent = sInput.value;
      render();
    });

    cInput.addEventListener("input", () => {
      currentViews[index].cfg = Number(cInput.value);
      cValue.textContent = Number(cInput.value).toFixed(2);
      render();
    });

    card.append(title, hint, angleDisplay, zLabel, zInput, zValue, sLabel, sInput, sValue, cLabel, cInput, cValue, singleBtn);
    viewControls.appendChild(card);
  });
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

if (copyNegativeButton) {
  copyNegativeButton.addEventListener("click", async () => {
    await navigator.clipboard.writeText(negativePromptText.value);
    copyNegativeButton.textContent = "已复制";
    setTimeout(() => {
      copyNegativeButton.textContent = "复制负向词";
    }, 1200);
  });
}

resetViewsButton.addEventListener("click", () => {
  resetMode(modeSelect.value);
});

refreshGalleryButton.addEventListener("click", refreshResults);

generateButton.addEventListener("click", submitGenerate);

modeSelect.value = "Celadon";
resetMode("Celadon");
setStatus("等待任务", "idle");