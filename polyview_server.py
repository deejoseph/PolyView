from __future__ import annotations

import base64
import json
import shutil
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
from PIL import Image


PROJECT_ROOT = Path(r"D:\PixelSmile\celadon-lab")
COMFY_ROOT = Path(r"D:\PixelSmile\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable")
COMFY_INPUT = COMFY_ROOT / "ComfyUI" / "input"
COMFY_OUTPUT = COMFY_ROOT / "ComfyUI" / "output"
WORKFLOW_TEMPLATE = PROJECT_ROOT / "智能多角度生成【plus】.json"
PROJECT_INPUT = PROJECT_ROOT / "input"
PROJECT_TOTAL = PROJECT_ROOT / "output" / "total"
PROJECT_SINGLE = PROJECT_ROOT / "output" / "single"
PROJECT_SHEETS = PROJECT_ROOT / "output" / "contact_sheets"
PROJECT_JOBS = PROJECT_ROOT / "output" / "jobs"
PROJECT_LOGS = PROJECT_ROOT / "logs"
COMFY_API = "http://127.0.0.1:8188"
TARGET_WIDTH = 1152
TARGET_HEIGHT = 768


MODE_PRESETS = {
    "Celadon": {
        "prompt": "celadon ceramic vessel, museum-grade product photography, glossy green glaze, fine crackle texture, clean neutral background, soft studio lighting, same exact object, coherent 360-degree camera orbit, handle and body rotate together, highly detailed",
        "negative": "deformed vessel, mismatched handle orientation, detached handle, detached spout, floating lid, asymmetrical body, broken ceramic, duplicate object, blur, low quality",
        "views": [
            {"name": "front_main", "horizontal": 0, "vertical": 0, "zoom": 3.2},
            {"name": "back_main", "horizontal": 180, "vertical": 0, "zoom": 3.2},
            {"name": "top_main", "horizontal": 90, "vertical": 55, "zoom": 3.6},
            {"name": "front_right_quarter", "horizontal": 45, "vertical": 12, "zoom": 3.2},
        ],
    },
    "Pet": {
        "prompt": "same pet, realistic animal portrait, consistent fur pattern, clean studio background, soft natural lighting, coherent camera orbit, stable anatomy, detailed eyes and fur, identity preserved",
        "negative": "extra limbs, deformed anatomy, duplicate body parts, wrong fur pattern, mismatched face, blur, low quality",
        "views": [
            {"name": "front", "horizontal": 0, "vertical": 0, "zoom": 1.0},
            {"name": "front_left", "horizontal": 330, "vertical": 6, "zoom": 1.0},
            {"name": "front_right", "horizontal": 30, "vertical": 6, "zoom": 1.0},
            {"name": "side", "horizontal": 90, "vertical": 0, "zoom": 1.0},
            {"name": "back", "horizontal": 180, "vertical": 0, "zoom": 0.98},
            {"name": "top", "horizontal": 0, "vertical": 35, "zoom": 1.02},
        ],
    },
    "Human": {
        "prompt": "same person, realistic portrait, consistent face identity, clean editorial background, soft cinematic lighting, coherent camera orbit, stable anatomy, detailed hair and fabric, high fidelity",
        "negative": "bad anatomy, deformed face, mismatched limbs, duplicate body parts, blur, low quality",
        "views": [
            {"name": "front", "horizontal": 0, "vertical": 0, "zoom": 1.0},
            {"name": "front_left", "horizontal": 330, "vertical": 4, "zoom": 1.02},
            {"name": "front_right", "horizontal": 30, "vertical": 4, "zoom": 1.02},
            {"name": "side", "horizontal": 90, "vertical": 0, "zoom": 1.0},
            {"name": "back", "horizontal": 180, "vertical": 0, "zoom": 1.0},
            {"name": "top", "horizontal": 0, "vertical": 30, "zoom": 1.04},
        ],
    },
    "Industrial": {
        "prompt": "industrial structure, engineered surfaces, technical product render, clean background, precise geometry, hard-surface detailing, controlled reflections, coherent camera orbit, structural consistency, high detail",
        "negative": "warped geometry, broken structure, detached parts, extra parts, blur, low quality",
        "views": [
            {"name": "front", "horizontal": 0, "vertical": 0, "zoom": 1.0},
            {"name": "front_left", "horizontal": 315, "vertical": 10, "zoom": 0.98},
            {"name": "front_right", "horizontal": 45, "vertical": 10, "zoom": 0.98},
            {"name": "side", "horizontal": 90, "vertical": 0, "zoom": 1.0},
            {"name": "back", "horizontal": 180, "vertical": 0, "zoom": 1.0},
            {"name": "top", "horizontal": 0, "vertical": 50, "zoom": 1.02},
        ],
    },
    "Architecture": {
        "prompt": "architectural subject, professional archviz, clean facade lines, balanced daylight, realistic materials, stable geometry, coherent camera orbit, controlled perspective, detailed surfaces, high detail",
        "negative": "warped building, broken facade, impossible perspective, blur, low quality",
        "views": [
            {"name": "front", "horizontal": 0, "vertical": 0, "zoom": 0.95},
            {"name": "front_left", "horizontal": 315, "vertical": 12, "zoom": 0.92},
            {"name": "front_right", "horizontal": 45, "vertical": 12, "zoom": 0.92},
            {"name": "side", "horizontal": 90, "vertical": 6, "zoom": 0.94},
            {"name": "back", "horizontal": 180, "vertical": 6, "zoom": 0.94},
            {"name": "top", "horizontal": 0, "vertical": 55, "zoom": 0.9},
        ],
    },
}


JOBS: dict[str, dict] = {}


def ensure_dirs() -> None:
    for path in (PROJECT_INPUT, PROJECT_TOTAL, PROJECT_SINGLE, PROJECT_SHEETS, PROJECT_JOBS, PROJECT_LOGS):
        path.mkdir(parents=True, exist_ok=True)


def write_log(payload: dict) -> None:
    ensure_dirs()
    log_path = PROJECT_LOGS / f"polyview_{time.strftime('%Y%m%d_%H%M%S')}.log"
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def json_response(handler: SimpleHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def decode_data_url(data_url: str) -> bytes:
    if "," not in data_url:
        raise ValueError("invalid image payload")
    return base64.b64decode(data_url.split(",", 1)[1])


def normalize_views(mode: str, payload_views: list[dict] | None) -> list[dict]:
    base = payload_views if payload_views else MODE_PRESETS[mode]["views"]
    views = []
    for index, view in enumerate(base[:6], start=1):
        views.append(
            {
                "index": index,
                "name": view.get("name", f"view_{index}"),
                "horizontal": int(view.get("horizontal", 0)) % 360,
                "vertical": int(max(-90, min(90, view.get("vertical", 0)))),
                "zoom": max(0.1, round(float(view.get("zoom", 1.0)), 2)),
            }
        )
    return views


def describe_horizontal_bucket(horizontal: int) -> str:
    h = horizontal % 360
    if h < 22.5 or h >= 337.5:
        return "front view"
    if h < 67.5:
        return "front-right quarter view"
    if h < 112.5:
        return "right side view"
    if h < 157.5:
        return "back-right quarter view"
    if h < 202.5:
        return "back view"
    if h < 247.5:
        return "back-left quarter view"
    if h < 292.5:
        return "left side view"
    return "front-left quarter view"


def describe_vertical_bucket(vertical: int) -> str:
    if vertical < -15:
        return "low-angle shot"
    if vertical < 15:
        return "eye-level shot"
    if vertical < 45:
        return "elevated shot"
    return "high-angle shot"


def describe_zoom_bucket(zoom: float) -> str:
    if zoom < 2:
        return "wide shot"
    if zoom < 6:
        return "medium shot"
    return "close-up"


def build_panel_prompts(mode: str, views: list[dict]) -> list[str]:
    prompts = []
    for index, view in enumerate(views, start=1):
        if mode == "Celadon":
            celadon_prompts = {
                1: (
                    "<sks> front view eye-level shot medium shot, "
                    "same celadon teapot, standard front product shot, spout clearly on the left side, "
                    "body facing camera, arch handle centered above the lid, "
                    "whole vessel rotates as one object, "
                    "spout thickness, spout base and body curvature must match the same teapot"
                ),
                2: (
                    "<sks> back view eye-level shot medium shot, "
                    "same celadon teapot, standard rear product shot, arch handle centered over the lid, "
                    "back of the body facing camera, spout hidden behind the body, "
                    "clearly different from panel 1, "
                    "no detached or misaligned spout"
                ),
                3: (
                    "<sks> top-down view high-angle shot medium shot, "
                    "same celadon teapot, strict top view, look down onto the lid and knob, "
                    "arch handle crossing horizontally above the center, spout pointing to the left side of the frame, "
                    "distinct top view, "
                    "spout must connect naturally to the vessel shoulder"
                ),
                4: (
                    "<sks> front-right quarter view eye-level shot medium shot, "
                    "same celadon teapot, standard three-quarter product shot from the right, spout clearly on the right side, "
                    "body and attached parts rotate together, "
                    "different from the front view and the back view, "
                    "spout root, handle root and body volume must remain coherent"
                ),
            }
            prompts.append(celadon_prompts[index])
            continue
        elif mode == "Pet":
            base = (
                f"<sks> panel {index}, {describe_horizontal_bucket(view['horizontal'])}, "
                f"{describe_vertical_bucket(view['vertical'])}, {describe_zoom_bucket(view['zoom'])}"
            )
            extra = "same pet, same face and fur markings, distinct viewpoint, preserve anatomy"
        elif mode == "Human":
            base = (
                f"<sks> panel {index}, {describe_horizontal_bucket(view['horizontal'])}, "
                f"{describe_vertical_bucket(view['vertical'])}, {describe_zoom_bucket(view['zoom'])}"
            )
            extra = "same person, same face identity, distinct viewpoint, preserve body consistency"
        elif mode == "Industrial":
            base = (
                f"<sks> panel {index}, {describe_horizontal_bucket(view['horizontal'])}, "
                f"{describe_vertical_bucket(view['vertical'])}, {describe_zoom_bucket(view['zoom'])}"
            )
            extra = "same industrial object, distinct viewpoint, preserve rigid geometry and connected parts"
        else:
            base = (
                f"<sks> panel {index}, {describe_horizontal_bucket(view['horizontal'])}, "
                f"{describe_vertical_bucket(view['vertical'])}, {describe_zoom_bucket(view['zoom'])}"
            )
            extra = "same architecture subject, distinct viewpoint, preserve structure and facade logic"

        prompts.append(f"{base}, {extra}")
    return prompts


def load_workflow(filename: str, mode: str, views: list[dict], prompt: str, negative: str) -> dict:
    workflow = json.loads(WORKFLOW_TEMPLATE.read_text(encoding="utf-8-sig"))

    workflow.pop("52", None)
    workflow.pop("53", None)
    workflow.pop("54", None)

    workflow["6"]["inputs"]["image"] = filename
    if len(views) <= 4:
        workflow["7"]["inputs"]["width"] = 1024
        workflow["7"]["inputs"]["height"] = 1024
    else:
        workflow["7"]["inputs"]["width"] = TARGET_WIDTH
        workflow["7"]["inputs"]["height"] = TARGET_HEIGHT

    qwen_nodes = ["17", "12", "20", "19", "21", "22"]
    for node_id, view in zip(qwen_nodes, views):
        workflow[node_id]["inputs"]["horizontal_angle"] = view["horizontal"]
        workflow[node_id]["inputs"]["vertical_angle"] = view["vertical"]
        workflow[node_id]["inputs"]["zoom"] = view["zoom"]

    panel_prompts = build_panel_prompts(mode, views)
    for index in range(1, 7):
        workflow["51"]["inputs"][f"string_{index}_{index}"] = panel_prompts[index - 1] if index <= len(panel_prompts) else ""

    workflow["51"]["inputs"]["num_views"] = len(views)
    workflow["51"]["inputs"]["base_prompt"] = prompt
    workflow["51"]["inputs"]["negative_prompt"] = negative

    return workflow


def comfy_post_json(path: str, payload: dict) -> dict:
    req = request.Request(
        COMFY_API + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def comfy_get_json(path: str) -> dict:
    with request.urlopen(COMFY_API + path, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_comfy_image(image_meta: dict) -> Path:
    subfolder = image_meta.get("subfolder")
    if subfolder:
        return COMFY_OUTPUT / subfolder / image_meta["filename"]
    return COMFY_OUTPUT / image_meta["filename"]


def relative_url(path: Path) -> str:
    return "/" + path.relative_to(PROJECT_ROOT).as_posix()


def slice_total_into_singles(total_path: Path, views: list[dict], job_dir: Path) -> list[dict]:
    image = Image.open(total_path).convert("RGB")
    width, height = image.size
    if len(views) <= 4:
        cols = 2
        rows = 2
    else:
        cols = 3
        rows = 2
    cell_w = width // cols
    cell_h = height // rows

    saved: list[dict] = []
    for index, view in enumerate(views):
        col = index % cols
        row = index // cols
        crop = image.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
        dst = job_dir / (
            f"view_{index + 1:02d}_horizontal_{view['horizontal']}_vertical_{view['vertical']}_zoom_{view['zoom']:.1f}.png"
        )
        crop.save(dst)
        saved.append(
            {
                "name": view["name"],
                "horizontal": view["horizontal"],
                "vertical": view["vertical"],
                "zoom": view["zoom"],
                "path": str(dst),
                "url": relative_url(dst),
            }
        )
    return saved


def copy_single_images(image_metas: list[dict], views: list[dict], job_dir: Path) -> list[dict]:
    saved: list[dict] = []
    for index, (image_meta, view) in enumerate(zip(image_metas, views), start=1):
        src = resolve_comfy_image(image_meta)
        if not src.exists():
            continue
        dst = job_dir / (
            f"view_{index:02d}_horizontal_{view['horizontal']}_vertical_{view['vertical']}_zoom_{view['zoom']:.1f}.png"
        )
        shutil.copy2(src, dst)
        saved.append(
            {
                "name": view["name"],
                "horizontal": view["horizontal"],
                "vertical": view["vertical"],
                "zoom": view["zoom"],
                "path": str(dst),
                "url": relative_url(dst),
            }
        )
    return saved


def copy_result_images(prompt_id: str, mode: str, views: list[dict], job_dir: Path) -> dict:
    history = comfy_get_json(f"/history/{prompt_id}")
    entry = history.get(prompt_id, {})
    outputs = entry.get("outputs", {})
    result = {"total_path": None, "sheet_path": None, "single_paths": []}

    total_images = outputs.get("1", {}).get("images", []) or outputs.get("53", {}).get("images", [])
    if total_images:
        src = resolve_comfy_image(total_images[0])
        dst = job_dir / f"PolyView_{mode}_total.png"
        if src.exists():
            shutil.copy2(src, dst)
            result["total_path"] = str(dst)
            result["total_url"] = relative_url(dst)

    single_images = outputs.get("54", {}).get("images", [])
    if single_images:
        result["single_paths"] = copy_single_images(single_images, views, job_dir)
    elif result["total_path"]:
        result["single_paths"] = slice_total_into_singles(Path(result["total_path"]), views, job_dir)

    sheet_path = job_dir / f"PolyView_{mode}_sheet.png"
    if result["total_path"]:
        shutil.copy2(Path(result["total_path"]), sheet_path)
        result["sheet_path"] = str(sheet_path)
        result["sheet_url"] = relative_url(sheet_path)
    elif sheet_path.exists():
        result["sheet_path"] = str(sheet_path)
        result["sheet_url"] = relative_url(sheet_path)

    return result


def run_job(job_id: str, comfy_filename: str, mode: str, views: list[dict], prompt: str, negative: str) -> None:
    try:
        job_dir = PROJECT_JOBS / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        JOBS[job_id]["status"] = "submitting"
        workflow = load_workflow(comfy_filename, mode, views, prompt, negative)
        response = comfy_post_json("/prompt", {"prompt": workflow, "client_id": job_id})
        prompt_id = response["prompt_id"]
        JOBS[job_id]["prompt_id"] = prompt_id
        JOBS[job_id]["status"] = "running"

        for _ in range(600):
            history = comfy_get_json(f"/history/{prompt_id}")
            if prompt_id in history:
                copied = copy_result_images(prompt_id, mode, views, job_dir)
                JOBS[job_id]["status"] = "completed"
                JOBS[job_id]["job_dir"] = str(job_dir)
                JOBS[job_id]["total_path"] = copied["total_path"]
                JOBS[job_id]["total_url"] = copied.get("total_url")
                JOBS[job_id]["sheet_path"] = copied["sheet_path"]
                JOBS[job_id]["sheet_url"] = copied.get("sheet_url")
                JOBS[job_id]["single_paths"] = copied["single_paths"]
                JOBS[job_id]["completed_at"] = time.time()
                write_log(JOBS[job_id])
                return
            time.sleep(1.5)

        JOBS[job_id]["status"] = "timeout"
        write_log(JOBS[job_id])
    except Exception as exc:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(exc)
        write_log(JOBS[job_id])


class PolyViewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/config":
            return json_response(self, {"comfy_api": COMFY_API, "modes": MODE_PRESETS})
        if self.path.startswith("/api/jobs/"):
            job_id = self.path.rsplit("/", 1)[-1]
            job = JOBS.get(job_id)
            if not job:
                return json_response(self, {"error": "job not found"}, status=404)
            return json_response(self, job)
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/generate":
            return json_response(self, {"error": "not found"}, status=404)

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            image_data = payload["imageData"]
            mode = payload["mode"]
            views = normalize_views(mode, payload.get("views"))
            prompt = payload.get("positive_prompt", "").strip() or MODE_PRESETS[mode]["prompt"]
            negative = payload.get("negative_prompt", "").strip() or MODE_PRESETS[mode]["negative"]

            ensure_dirs()
            image_bytes = decode_data_url(image_data)
            comfy_filename = f"polyview_{uuid.uuid4().hex}.png"
            (PROJECT_INPUT / comfy_filename).write_bytes(image_bytes)
            (COMFY_INPUT / comfy_filename).write_bytes(image_bytes)

            job_id = uuid.uuid4().hex
            JOBS[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "mode": mode,
                "views": views,
                "job_dir": str(PROJECT_JOBS / job_id),
                "created_at": time.time(),
            }
            thread = threading.Thread(
                target=run_job,
                args=(job_id, comfy_filename, mode, views, prompt, negative),
                daemon=True,
            )
            thread.start()
            return json_response(self, {"job_id": job_id, "status": "queued"})
        except KeyError as exc:
            return json_response(self, {"error": f"missing field: {exc}"}, status=400)
        except error.URLError as exc:
            return json_response(self, {"error": f"cannot reach ComfyUI: {exc}"}, status=502)
        except Exception as exc:
            return json_response(self, {"error": str(exc)}, status=500)


if __name__ == "__main__":
    ensure_dirs()
    server = ThreadingHTTPServer(("127.0.0.1", 8080), PolyViewHandler)
    print(f"PolyView server running at http://127.0.0.1:8080 using workflow: {WORKFLOW_TEMPLATE.name}")
    server.serve_forever()
