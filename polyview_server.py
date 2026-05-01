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
WORKFLOW_TEMPLATE = PROJECT_ROOT / "智能多角度生成【6视图】.json"
PROJECT_INPUT = PROJECT_ROOT / "input"
PROJECT_JOBS = PROJECT_ROOT / "output" / "jobs"
COMFY_API = "http://127.0.0.1:8188"


# ========== 固定的视角角度 ==========
FIXED_VIEW_ANGLES = {
    # Celadon
    "正面主视": {"horizontal": 0, "vertical": 10},
    "背面视图": {"horizontal": 180, "vertical": 10},
    "顶视图": {"horizontal": 0, "vertical": 75},
    "四分之三视图": {"horizontal": 45, "vertical": 15},
    "侧视图": {"horizontal": 90, "vertical": 10},
    # Pet/Human/Industrial
    "正面": {"horizontal": 0, "vertical": 0},
    "左前": {"horizontal": 315, "vertical": 6},
    "右前": {"horizontal": 45, "vertical": 6},
    "侧面": {"horizontal": 90, "vertical": 0},
    "背面": {"horizontal": 160, "vertical": 0},
    "俯视": {"horizontal": 0, "vertical": 35},
    # Architecture
    "正立面": {"horizontal": 0, "vertical": 0},
    "侧立面": {"horizontal": 90, "vertical": 6},
    "背立面": {"horizontal": 180, "vertical": 6},
    "鸟瞰": {"horizontal": 0, "vertical": 55},
}


def get_fixed_angle(view_name: str) -> tuple[int, int]:
    angle = FIXED_VIEW_ANGLES.get(view_name, {"horizontal": 0, "vertical": 10})
    return angle["horizontal"], angle["vertical"]


# ========== 各模式的默认参数 ==========
MODE_PRESETS = {
    "Celadon": {
        "prompt": "celadon ceramic vessel, museum-grade product photography, glossy green glaze, fine crackle texture, clean neutral background, soft studio lighting, same exact object, coherent camera orbit, one intact vessel only, spout body arch-handle lid and knob must stay attached and rotate together, highly detailed",
        "negative": "deformed vessel, repeated viewpoint, duplicate object, detached spout, detached handle, misaligned arch handle, wrong spout attachment, floating lid, broken ceramic, asymmetrical body, blur, low quality",
        "views": [
            {"name": "正面主视", "zoom": 1.5, "steps": 24, "cfg": 2.2},
            {"name": "背面视图", "zoom": 1.35, "steps": 36, "cfg": 2.4},
            {"name": "顶视图", "zoom": 1.5, "steps": 20, "cfg": 1.8},
            {"name": "四分之三视图", "zoom": 2.2, "steps": 28, "cfg": 2.0},
            {"name": "侧视图", "zoom": 1.5, "steps": 24, "cfg": 2.2},
        ],
    },
    "Pet": {
        "prompt": "same pet, realistic animal portrait, consistent fur pattern, clean studio background, soft natural lighting, coherent camera orbit, stable anatomy, detailed eyes and fur, identity preserved, high fidelity, 4K",
        "negative": "extra limbs, deformed anatomy, duplicate body parts, wrong fur pattern, mismatched face, blurry eyes, deformed ears, low quality, blur, cartoon, illustration",
        "views": [
            {"name": "正面", "zoom": 1.2, "steps": 28, "cfg": 2.8},
            {"name": "左前", "zoom": 1.2, "steps": 28, "cfg": 2.8},
            {"name": "右前", "zoom": 1.2, "steps": 28, "cfg": 2.8},
            {"name": "侧面", "zoom": 1.1, "steps": 28, "cfg": 2.6},
            {"name": "背面", "zoom": 1.0, "steps": 28, "cfg": 2.5},
            {"name": "俯视", "zoom": 1.1, "steps": 28, "cfg": 2.6},
        ],
    },
    "Human": {
        "prompt": "same person, realistic full body portrait, consistent face identity and body shape, clean editorial background, soft cinematic lighting, coherent camera orbit around the entire body, stable anatomy, detailed hair and fabric, full body rotates together, high fidelity, professional photography, 4K",
        "negative": "bad anatomy, deformed face, mismatched limbs, duplicate body parts, blurry face, wrong eyes, extra fingers, deformed hands, torso facing wrong direction, head turned but body facing forward, low quality, blur, cartoon",
        "views": [
            {"name": "正面", "zoom": 0.85, "steps": 40, "cfg": 1.5},
            {"name": "左前", "zoom": 1.3, "steps": 35, "cfg": 2.3},
            {"name": "右前", "zoom": 1.3, "steps": 35, "cfg": 2.3},
            {"name": "侧面", "zoom": 1.2, "steps": 32, "cfg": 2.2},
            {"name": "背面", "zoom": 1.2, "steps": 32, "cfg": 2.2},
            {"name": "俯视", "zoom": 1.1, "steps": 28, "cfg": 2.2},
        ],
    },
    "Industrial": {
        "prompt": "industrial structure, engineered surfaces, technical product render, clean background, precise geometry, hard-surface detailing, controlled reflections, coherent camera orbit, structural consistency, high detail, 4K, sharp edges",
        "negative": "warped geometry, broken structure, detached parts, extra parts, soft edges, blurry reflections, low quality, blur, unrealistic materials, cartoon",
        "views": [
            {"name": "正面", "zoom": 1.2, "steps": 28, "cfg": 2.2},
            {"name": "左前", "zoom": 1.2, "steps": 28, "cfg": 2.2},
            {"name": "右前", "zoom": 1.2, "steps": 28, "cfg": 2.2},
            {"name": "侧面", "zoom": 1.1, "steps": 28, "cfg": 2.2},
            {"name": "背面", "zoom": 1.1, "steps": 28, "cfg": 2.2},
            {"name": "俯视", "zoom": 1.0, "steps": 28, "cfg": 2.2},
        ],
    },
    "Architecture": {
        "prompt": "architectural subject, professional archviz, clean facade lines, balanced daylight, realistic materials, stable geometry, coherent camera orbit, controlled perspective, detailed surfaces, high detail, 4K, sharp lines, realistic shadows",
        "negative": "warped building, broken facade, impossible perspective, distorted geometry, blurry textures, low quality, blur, cartoon, unrealistic lighting",
        "views": [
            {"name": "正立面", "zoom": 0.9, "steps": 32, "cfg": 2.2},
            {"name": "左前", "zoom": 0.85, "steps": 32, "cfg": 2.2},
            {"name": "右前", "zoom": 0.85, "steps": 32, "cfg": 2.2},
            {"name": "侧立面", "zoom": 0.9, "steps": 32, "cfg": 2.2},
            {"name": "背立面", "zoom": 0.9, "steps": 32, "cfg": 2.2},
            {"name": "鸟瞰", "zoom": 0.8, "steps": 32, "cfg": 2.2},
        ],
    },
}


JOBS: dict[str, dict] = {}


def ensure_dirs() -> None:
    PROJECT_JOBS.mkdir(parents=True, exist_ok=True)
    PROJECT_INPUT.mkdir(parents=True, exist_ok=True)
    (COMFY_INPUT).mkdir(parents=True, exist_ok=True)


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
    """处理视图参数"""
    if payload_views is not None:
        base = payload_views
        print(f"[DEBUG] Using {len(base)} views from frontend")
    else:
        base = MODE_PRESETS[mode]["views"]
        print(f"[DEBUG] Using {len(base)} views from preset")
    
    views = []
    for idx, view in enumerate(base):
        horizontal, vertical = get_fixed_angle(view.get("name", f"view_{idx+1}"))
        views.append({
            "index": idx + 1,
            "name": view.get("name", f"view_{idx+1}"),
            "horizontal": horizontal,
            "vertical": vertical,
            "zoom": float(view.get("zoom", 1.0)),
            "steps": int(view.get("steps", 24)),
            "cfg": float(view.get("cfg", 2.0)),
        })
        print(f"[DEBUG] View {idx+1}: {views[-1]['name']} steps={views[-1]['steps']} cfg={views[-1]['cfg']} zoom={views[-1]['zoom']}")
    
    return views


def build_prompt_for_view(view_name: str, horizontal: int, vertical: int, zoom: float, mode: str = "Celadon") -> str:
    """根据视角构建 Prompt"""
    angle_desc = f"horizontal angle {horizontal} degrees, vertical angle {vertical} degrees"
    
    # 视角名称映射
    view_desc_map = {
        "正面": "front view",
        "左前": "front-left quarter view",
        "右前": "front-right quarter view",
        "侧面": "side view",
        "背面": "back view",
        "俯视": "top-down view",
        "正立面": "front elevation",
        "侧立面": "side elevation",
        "背立面": "back elevation",
        "鸟瞰": "bird's eye view",
    }
    
    # Celadon 模式的专用 Prompt
    if mode == "Celadon":
        prompts = {
            "正面主视": f"Turn the camera to a front view, {angle_desc}, zoom level {zoom}. Show the front of the celadon porcelain product centered in frame.",
            "背面视图": f"Turn the camera to a back view, {angle_desc}, zoom level {zoom}. Show the back of the celadon porcelain product centered in frame.",
            "顶视图": f"Turn the camera to a top-down view, {angle_desc}, zoom level {zoom}. Show the top of the celadon porcelain product centered in frame.",
            "四分之三视图": f"Turn the camera to a three-quarter view, {angle_desc}, zoom level {zoom}. Show the celadon porcelain product from a dynamic angle centered in frame.",
            "侧视图": f"Turn the camera to a side view, {angle_desc}, zoom level {zoom}. Show the side profile of the celadon porcelain product centered in frame.",
        }
        base_prompt = prompts.get(view_name, prompts.get("正面主视"))
        return base_prompt + " Keep the same celadon glaze, shape, and material properties. celadon porcelain product photo, premium ceramic object, consistent object, clean background, 4K, high resolution"
    
    # 其他模式的通用 Prompt
    view_desc = view_desc_map.get(view_name, "view")
    
    if mode == "Human":
        if view_name == "正面":
            return f"Turn the camera to front view, {angle_desc}, zoom level {zoom}. Show the full body of the same person from head to toe. **Natural face expression, symmetrical face, realistic skin texture, no distortion.** Keep the same face identity, body shape, clothing. Professional full-body portrait photography, clean background, 4K, high resolution."
        else:
            return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same person from this angle. Keep the same face identity, body shape, clothing. Full body rotates together. Professional portrait photography, clean background, 4K, high resolution."
    elif mode == "Pet":
        return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same pet from this angle. Keep the same fur pattern, face markings, and body shape. The pet's head and body rotate together. Clean studio background, soft lighting, 4K, high resolution."
    elif mode == "Industrial":
        return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same industrial object from this angle. Keep the exact same geometry, surface finish, and structural integrity. Clean background, technical product render, 4K, sharp edges."
    elif mode == "Architecture":
        return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same building from this angle. Keep the same facade design, materials, and structural consistency. Professional architectural visualization, balanced lighting, 4K, sharp lines."
    
    # 默认情况
    return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same subject from this angle. Keep consistency with the original image."


def load_workflow(filename: str, views: list[dict], mode: str = "Celadon", is_single: bool = False) -> dict:
    """加载并修改工作流"""
    workflow = json.loads(WORKFLOW_TEMPLATE.read_text(encoding="utf-8-sig"))
    workflow["6_load"]["inputs"]["image"] = filename

    # ========== 单独生成：禁用其他采样器 ==========
    if is_single:
        print(f"[DEBUG] Single generation, disabling other samplers")
        # 所有采样器节点（除了当前需要的）
        all_samplers = ["23_front_sampler", "33_back_sampler", "43_top_sampler", 
                        "53_threequarter_sampler", "63_side_sampler", "73_additional_sampler"]
        
        # 获取当前视图对应的采样器 ID
        sampler_map = {
            "正面": "23_front_sampler", "正面主视": "23_front_sampler",
            "左前": "33_back_sampler", "背面视图": "33_back_sampler",
            "右前": "43_top_sampler", "顶视图": "43_top_sampler",
            "侧面": "53_threequarter_sampler", "四分之三视图": "53_threequarter_sampler",
            "背面": "63_side_sampler", "侧视图": "63_side_sampler",
            "俯视": "73_additional_sampler", "鸟瞰": "73_additional_sampler",
            "正立面": "23_front_sampler", "侧立面": "53_threequarter_sampler",
            "背立面": "63_side_sampler",
        }
        
        current_view_name = views[0]["name"]
        keep_sampler = sampler_map.get(current_view_name, "23_front_sampler")
        
        for sampler_id in all_samplers:
            if sampler_id in workflow:
                if sampler_id == keep_sampler:
                    print(f"  [KEEP] {sampler_id}")
                else:
                    # 禁用：设置 steps=1, denoise=0
                    workflow[sampler_id]["inputs"]["steps"] = 1
                    workflow[sampler_id]["inputs"]["denoise"] = 0
                    print(f"  [DISABLED] {sampler_id}")
    
    # ========== 映射表 ==========
    # 编码器映射
    encoder_map = {
        "正面主视": "20_front_encoder",
        "背面视图": "30_back_encoder",
        "顶视图": "40_top_encoder",
        "四分之三视图": "50_threequarter_encoder",
        "侧视图": "60_side_encoder",
        "正面": "20_front_encoder",
        "左前": "30_back_encoder",
        "右前": "40_top_encoder",
        "侧面": "50_threequarter_encoder",
        "背面": "60_side_encoder",
        "俯视": "70_additional_encoder",
        "正立面": "20_front_encoder",
        "侧立面": "50_threequarter_encoder",
        "背立面": "60_side_encoder",
        "鸟瞰": "70_additional_encoder",
    }
    
    # 采样器映射
    sampler_map = {
        "正面主视": "23_front_sampler",
        "背面视图": "33_back_sampler",
        "顶视图": "43_top_sampler",
        "四分之三视图": "53_threequarter_sampler",
        "侧视图": "63_side_sampler",
        "正面": "23_front_sampler",
        "左前": "33_back_sampler",
        "右前": "43_top_sampler",
        "侧面": "53_threequarter_sampler",
        "背面": "63_side_sampler",
        "俯视": "73_additional_sampler",
        "正立面": "23_front_sampler",
        "侧立面": "53_threequarter_sampler",
        "背立面": "63_side_sampler",
        "鸟瞰": "73_additional_sampler",
    }
    
    # Latent 映射
    latent_map = {
        "正面主视": "22_front_latent",
        "背面视图": "32_back_latent",
        "顶视图": "42_top_latent",
        "四分之三视图": "52_threequarter_latent",
        "侧视图": "62_side_latent",
        "正面": "22_front_latent",
        "左前": "32_back_latent",
        "右前": "42_top_latent",
        "侧面": "52_threequarter_latent",
        "背面": "62_side_latent",
        "俯视": "72_additional_latent",
        "正立面": "22_front_latent",
        "侧立面": "52_threequarter_latent",
        "背立面": "62_side_latent",
        "鸟瞰": "72_additional_latent",
    }
    
    # 添加调试日志
    print(f"[DEBUG] Processing {len(views)} views: mode={mode}")
    
    for idx, view in enumerate(views):
        name = view["name"]
        print(f"  [{idx+1}] {name}: steps={view.get('steps')}, cfg={view.get('cfg')}, zoom={view.get('zoom')}")
        
        if name not in encoder_map:
            print(f"  [WARN] View '{name}' not found in encoder_map, skipping")
            continue

        # 更新编码器的 prompt
        encoder_id = encoder_map[name]
        workflow[encoder_id]["inputs"]["prompt"] = build_prompt_for_view(
            name, view["horizontal"], view["vertical"], view["zoom"], mode
        )
        workflow[encoder_id]["inputs"]["target_size"] = 1024
        workflow[encoder_id]["inputs"]["target_vl_size"] = 384

        # 更新采样器的 steps 和 cfg
        sampler_id = sampler_map[name]
        workflow[sampler_id]["inputs"]["steps"] = view["steps"]
        workflow[sampler_id]["inputs"]["cfg"] = view["cfg"]
        print(f"  [OK] Set {sampler_id}: steps={view['steps']}, cfg={view['cfg']}")

        # 确保 Latent 是 1024x1024
        if name in latent_map:
            latent_id = latent_map[name]
            workflow[latent_id]["inputs"]["width"] = 1024
            workflow[latent_id]["inputs"]["height"] = 1024

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
    subfolder = image_meta.get("subfolder", "")
    if subfolder:
        return COMFY_OUTPUT / subfolder / image_meta["filename"]
    return COMFY_OUTPUT / image_meta["filename"]


def relative_url(path: Path) -> str:
    return "/" + path.relative_to(PROJECT_ROOT).as_posix()


def copy_result_images(prompt_id: str, mode: str, views: list[dict], job_dir: Path) -> dict:
    """从 ComfyUI 输出复制图片到任务目录"""
    history = comfy_get_json(f"/history/{prompt_id}")
    entry = history.get(prompt_id, {})
    outputs = entry.get("outputs", {})
    
    print(f"[DEBUG] outputs keys: {list(outputs.keys())}")
    
    result = {"single_paths": []}
    
    # 判断是否是单独生成
    is_single = len(views) == 1
    
    if is_single:
        # 单独生成：只处理第一个保存节点
        save_nodes = ["1"]
        print(f"[DEBUG] Single generation, only processing save node 1")
    else:
        # 完整生成：处理所有保存节点
        save_nodes = ["1", "2", "3", "4", "5", "6"]
    
    for idx, save_node in enumerate(save_nodes):
        if idx >= len(views):
            break
            
        if save_node not in outputs:
            print(f"[WARN] Save node {save_node} not found in outputs")
            continue
            
        images = outputs[save_node].get("images", [])
        if not images:
            print(f"[WARN] No images in node {save_node}")
            continue
        
        src = resolve_comfy_image(images[0])
        if not src.exists():
            print(f"[WARN] Image file not found: {src}")
            continue
        
        view = views[idx]
        dst = job_dir / f"view_{idx+1:02d}_{view['name']}_z{view['zoom']}_s{view['steps']}_c{view['cfg']}.png"
        
        shutil.copy2(src, dst)
        result["single_paths"].append({
            "name": view["name"],
            "horizontal": view.get("horizontal", 0),
            "vertical": view.get("vertical", 0),
            "zoom": view.get("zoom", 1.0),
            "steps": view.get("steps", 24),
            "cfg": view.get("cfg", 2.0),
            "path": str(dst),
            "url": relative_url(dst),
        })
        print(f"[INFO] Saved image from node {save_node} to {dst.name}")
    
    # 生成总图拼接（如果有多张图）
    if len(result["single_paths"]) > 1:
        try:
            images = [Image.open(p["path"]) for p in result["single_paths"]]
            if images:
                # 根据图片数量决定网格布局
                if len(images) <= 4:
                    cols, rows = 2, 2
                else:
                    cols, rows = 3, 2
                
                cell_w, cell_h = images[0].size
                total_w = cols * cell_w
                total_h = rows * cell_h
                total_img = Image.new('RGB', (total_w, total_h))
                
                for i, img in enumerate(images[:cols*rows]):
                    x = (i % cols) * cell_w
                    y = (i // cols) * cell_h
                    total_img.paste(img, (x, y))
                
                total_path = job_dir / "total_contact_sheet.png"
                total_img.save(total_path)
                result["total_url"] = relative_url(total_path)
                print(f"[INFO] Created contact sheet: {total_path}")
        except Exception as e:
            print(f"[WARN] Failed to create contact sheet: {e}")
    
    # 设置预览图
    if result["single_paths"]:
        result["total_url"] = result["single_paths"][0]["url"]
    
    print(f"[INFO] Total images saved: {len(result['single_paths'])}")
    return result


def run_job(job_id: str, comfy_filename: str, mode: str, views: list[dict]) -> None:
    print(f"[DEBUG] Job {job_id}: {len(views)} views")
    for v in views:
        print(f"  {v['name']}: steps={v['steps']}, cfg={v['cfg']}, zoom={v['zoom']}")
    
    # 判断是否是单独生成
    is_single = len(views) == 1
    if is_single:
        print(f"[DEBUG] Single generation mode for view: {views[0]['name']}")
    
    try:
        job_dir = PROJECT_JOBS / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        JOBS[job_id]["status"] = "submitting"
        
        workflow = load_workflow(comfy_filename, views, mode, is_single)  # 传递 is_single
        response = comfy_post_json("/prompt", {"prompt": workflow, "client_id": job_id})
        prompt_id = response["prompt_id"]
        JOBS[job_id]["prompt_id"] = prompt_id
        JOBS[job_id]["status"] = "running"

        # 60 分钟超时
        for _ in range(2400):
            history = comfy_get_json(f"/history/{prompt_id}")
            if prompt_id in history:
                copied = copy_result_images(prompt_id, mode, views, job_dir)
                JOBS[job_id]["status"] = "completed"
                JOBS[job_id]["single_paths"] = copied["single_paths"]
                JOBS[job_id]["total_url"] = copied.get("total_url")
                JOBS[job_id]["completed_at"] = time.time()
                print(f"[DEBUG] Job {job_id} completed, saved {len(copied['single_paths'])} images")
                return
            time.sleep(1.5)

        JOBS[job_id]["status"] = "timeout"
        JOBS[job_id]["error"] = "超时：60 分钟后仍未完成"
    except Exception as exc:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(exc)
        print(f"[ERROR] {exc}")


class PolyViewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self) -> None:
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
                "created_at": time.time(),
            }
            thread = threading.Thread(
                target=run_job,
                args=(job_id, comfy_filename, mode, views),
                daemon=True,
            )
            thread.start()
            return json_response(self, {"job_id": job_id, "status": "queued"})
        except Exception as exc:
            return json_response(self, {"error": str(exc)}, status=500)


if __name__ == "__main__":
    ensure_dirs()
    server = ThreadingHTTPServer(("127.0.0.1", 8080), PolyViewHandler)
    print(f"PolyView server running at http://127.0.0.1:8080")
    server.serve_forever()