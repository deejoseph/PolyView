const promptTemplates = {
  Celadon: "celadon ceramic vessel, museum-grade product photography, glossy green glaze, fine crackle texture, clean neutral background, soft studio lighting, consistent silhouette, premium craftsmanship, highly detailed, stable geometry",
  Pet: "same pet, consistent fur pattern, realistic animal portrait, clean studio background, soft natural lighting, stable anatomy, detailed eyes and fur, gentle color contrast, highly detailed, identity preserved",
  Human: "same person, realistic portrait, consistent face identity, clean editorial background, soft cinematic lighting, natural skin texture, stable anatomy, detailed hair and fabric, high fidelity, identity preserved",
  Industrial: "industrial structure, engineered surfaces, technical product render, clean background, precise geometry, hard-surface detailing, controlled reflections, neutral studio light, structural consistency, high detail",
  Architecture: "architectural subject, professional archviz, clean facade lines, balanced daylight, realistic materials, stable geometry, controlled perspective, detailed surfaces, minimal background noise, high detail"
};

const modeSelect = document.querySelector("#mode");
const promptText = document.querySelector("#promptText");
const modeBadge = document.querySelector("#modeBadge");
const payloadPreview = document.querySelector("#payloadPreview");
const horizontal = document.querySelector("#horizontal");
const vertical = document.querySelector("#vertical");
const zoom = document.querySelector("#zoom");
const horizontalValue = document.querySelector("#horizontalValue");
const verticalValue = document.querySelector("#verticalValue");
const zoomValue = document.querySelector("#zoomValue");
const copyPromptButton = document.querySelector("#copyPrompt");
const resetViewButton = document.querySelector("#resetView");

Object.keys(promptTemplates).forEach((mode) => {
  const option = document.createElement("option");
  option.value = mode;
  option.textContent = mode;
  modeSelect.appendChild(option);
});

function render() {
  const mode = modeSelect.value;
  const payload = {
    node: "PolyView",
    mode,
    horizontal_angle: Number(horizontal.value),
    vertical_angle: Number(vertical.value),
    zoom: Number(zoom.value),
    positive_prompt: promptText.value.trim(),
    use_sd_controlnet: false
  };

  horizontalValue.textContent = horizontal.value;
  verticalValue.textContent = vertical.value;
  zoomValue.textContent = Number(zoom.value).toFixed(2);
  modeBadge.textContent = mode;
  payloadPreview.textContent = JSON.stringify(payload, null, 2);
}

modeSelect.addEventListener("change", () => {
  promptText.value = promptTemplates[modeSelect.value];
  render();
});

[horizontal, vertical, zoom].forEach((input) => {
  input.addEventListener("input", render);
});

promptText.addEventListener("input", render);

copyPromptButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(promptText.value);
  copyPromptButton.textContent = "Copied";
  setTimeout(() => {
    copyPromptButton.textContent = "Copy Prompt";
  }, 1200);
});

resetViewButton.addEventListener("click", () => {
  horizontal.value = "0";
  vertical.value = "0";
  zoom.value = "1";
  render();
});

modeSelect.value = "Celadon";
promptText.value = promptTemplates.Celadon;
render();
