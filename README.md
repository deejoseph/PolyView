# PolyView

PolyView is a lightweight front-end shell for the ComfyUI `PolyView` custom node.

## Included

- `index.html`: static UI
- `styles.css`: UI styles
- `app.js`: mode presets, prompt templates, UI state
- `input/`: source images
- `output/`: generated total and single-angle images
- `logs/`: run logs written by the node

## Modes

- Celadon
- Pet
- Human
- Industrial
- Architecture

## Run

Open `index.html` directly, or serve the folder:

```bash
python -m http.server 8080
```

Then open:

```text
http://127.0.0.1:8080
```

## ComfyUI Node

Custom node path:

```text
D:\PixelSmile\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\custom_nodes\polyview_node.py
```

## Notes

- The UI is a first-version project shell for prompt iteration and parameter review.
- Stable Diffusion + ControlNet execution still happens inside ComfyUI.
