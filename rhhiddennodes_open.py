"""
Open replacement for the closed-source `RHHiddenNodes` node used by
`智能多角度生成【plus】.json`.

What this file does
-------------------
1. ComfyUI compatibility layer
   - Registers a node with the exact workflow type name: `RHHiddenNodes`
   - Keeps the same required inputs as node id 51 in `智能多角度生成【plus】.json`
   - Returns one output named `p0`, so it can replace the closed node directly

2. Standalone multi-angle generation utility
   - Uses Stable Diffusion + ControlNet img2img
   - Accepts a source image and output directory
   - Generates N consistent celadon product views with yaw/pitch/roll control
   - Optionally exports a contact sheet and GIF

Dependencies
------------
pip install torch diffusers transformers accelerate pillow numpy imageio

Optional but recommended model defaults
---------------------------------------
- Base SD model:
  `runwayml/stable-diffusion-v1-5`
- ControlNet:
  `lllyasviel/sd-controlnet-canny`

If you prefer SDXL or your local model paths, pass them through CLI args or
the optional ComfyUI node inputs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import imageio.v2 as imageio
import numpy as np
import torch
from PIL import Image, ImageFilter, ImageOps, ImageDraw

try:
    from diffusers import ControlNetModel, StableDiffusionControlNetImg2ImgPipeline
except Exception:  # pragma: no cover - lets ComfyUI import the file even if deps are missing
    ControlNetModel = None
    StableDiffusionControlNetImg2ImgPipeline = None


ANGLE_RE = re.compile(r"(-?\d+)\s*[,/ ]\s*(-?\d+)")


@dataclass
class ViewSpec:
    index: int
    yaw: float
    pitch: float
    roll: float
    zoom: float
    source_prompt: str
    conditioned_prompt: str


def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", text).strip("_") or "output"


def ensure_pil_image(image: Image.Image | np.ndarray | torch.Tensor) -> Image.Image:
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    if isinstance(image, torch.Tensor):
        tensor = image.detach().cpu()
        if tensor.ndim == 4:
            tensor = tensor[0]
        if tensor.ndim != 3:
            raise ValueError(f"Unsupported tensor image shape: {tuple(tensor.shape)}")
        if tensor.shape[-1] in (3, 4):
            array = tensor.numpy()
        else:
            array = tensor.permute(1, 2, 0).numpy()
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)
        return Image.fromarray(array[..., :3], mode="RGB")
    if isinstance(image, np.ndarray):
        array = image
        if array.dtype != np.uint8:
            array = np.clip(array * 255.0, 0, 255).astype(np.uint8)
        if array.ndim != 3:
            raise ValueError(f"Unsupported ndarray image shape: {array.shape}")
        return Image.fromarray(array[..., :3], mode="RGB")
    raise TypeError(f"Unsupported image type: {type(image)!r}")


def pil_to_comfy_tensor(image: Image.Image) -> torch.Tensor:
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(array).unsqueeze(0)


def parse_angle_prompt(text: str, fallback_index: int, angle_step: float) -> Tuple[float, float, float, float]:
    """
    Best-effort parse for strings coming from `QwenMultiangleCameraNode`.
    The original closed node likely interpreted these prompt strings internally.
    Here we preserve them as text and also recover usable camera values when possible.
    """
    match = ANGLE_RE.search(text)
    if match:
        yaw = float(match.group(1))
        pitch = float(match.group(2))
    else:
        yaw = float(fallback_index * angle_step)
        pitch = 8.0 * math.sin(math.radians(yaw))

    roll_match = re.search(r"roll[^-\d]*(-?\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
    zoom_match = re.search(r"zoom[^-\d]*(\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)

    roll = float(roll_match.group(1)) if roll_match else 0.0
    zoom = float(zoom_match.group(1)) if zoom_match else 1.0
    return yaw, pitch, roll, zoom


def build_conditioned_prompt(
    base_prompt: str,
    source_prompt: str,
    yaw: float,
    pitch: float,
    roll: float,
    style_anchor: str = "same celadon ceramic object, same glaze, same lighting, same product identity",
) -> str:
    camera_phrase = (
        f"viewpoint rotation: yaw {yaw:.1f} degrees, pitch {pitch:.1f} degrees, "
        f"roll {roll:.1f} degrees"
    )
    return (
        f"{base_prompt}, {style_anchor}, studio product photography, "
        f"{camera_phrase}. Preserve silhouette, glaze color, crackle texture, "
        f"rim profile and handle/spout proportions. Source angle hint: {source_prompt}"
    )


def build_qwen_prompt_payload(pwd: str, views: Sequence[ViewSpec]) -> str:
    """
    Output string for the downstream `TextEncodeQwenImageEditPlusAdvance_lrzjason` prompt input.

    JSON mapping
    ------------
    - `pwd`            -> node 51 widget `pwd`
    - `string_1_1`     -> link 85 from node 17 prompt
    - `string_2_2`     -> link 86 from node 12 prompt
    - `string_3_3`     -> link 87 from node 20 prompt
    - `string_4_4`     -> link 88 from node 19 prompt
    - `string_5_5`     -> link 89 from node 21 prompt
    - `string_6_6`     -> link 90 from node 22 prompt
    - returned `p0`    -> link 91 into node 26 input `prompt`
    """
    lines = [
        "[CELADON_MULTIANGLE_V1]",
        f"pwd={pwd}",
        "Generate the same celadon object from the following controlled camera views.",
        "Keep the same object identity, glaze color, ceramic material, lighting and clean background.",
    ]
    for view in views:
        lines.append(
            (
                f"view_{view.index}: yaw={view.yaw:.1f}, pitch={view.pitch:.1f}, "
                f"roll={view.roll:.1f}, zoom={view.zoom:.2f}; prompt={view.source_prompt}"
            )
        )
    return "\n".join(lines)


def apply_perspective_hint(
    image: Image.Image,
    yaw: float,
    pitch: float,
    roll: float,
    zoom: float,
) -> Image.Image:
    """
    Cheap geometry hint used as ControlNet conditioning image.
    It is not a physically-correct renderer; it only provides a consistent view prior.
    """
    image = image.convert("RGB")
    w, h = image.size
    scale = max(0.6, min(1.8, 1.0 + (zoom - 1.0) * 0.25))
    resized = image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (w, h), (245, 245, 245))
    x = (w - resized.width) // 2
    y = (h - resized.height) // 2
    canvas.paste(resized, (x, y))

    dx = int((yaw / 180.0) * w * 0.18)
    dy = int((-pitch / 90.0) * h * 0.14)
    rotated = canvas.rotate(roll, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=(245, 245, 245))

    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [
        (0 + dx, 0 + dy),
        (w + dx, 0 - dy),
        (w - dx, h - dy),
        (0 - dx, h + dy),
    ]

    coeffs = find_perspective_coeffs(src, dst)
    warped = rotated.transform((w, h), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
    return warped


def find_perspective_coeffs(
    src: Sequence[Tuple[float, float]],
    dst: Sequence[Tuple[float, float]],
) -> List[float]:
    matrix = []
    for (sx, sy), (dx, dy) in zip(src, dst):
        matrix.append([sx, sy, 1, 0, 0, 0, -dx * sx, -dx * sy])
        matrix.append([0, 0, 0, sx, sy, 1, -dy * sx, -dy * sy])
    a = np.array(matrix, dtype=np.float64)
    b = np.array(dst, dtype=np.float64).reshape(8)
    return np.linalg.solve(a, b).tolist()


def make_control_image(image: Image.Image) -> Image.Image:
    edges = ImageOps.grayscale(image.filter(ImageFilter.FIND_EDGES))
    edges = ImageOps.autocontrast(edges)
    return edges.convert("RGB")


def add_angle_label(image: Image.Image, spec: ViewSpec) -> Image.Image:
    labeled = image.copy()
    draw = ImageDraw.Draw(labeled)
    label = f"#{spec.index} yaw {spec.yaw:.0f} pitch {spec.pitch:.0f} roll {spec.roll:.0f}"
    draw.rectangle((12, 12, 12 + len(label) * 8 + 12, 42), fill=(20, 20, 20))
    draw.text((18, 18), label, fill=(240, 240, 240))
    return labeled


def build_default_view_specs(
    prompts: Sequence[str],
    num_views: int,
    angle_step: float,
    base_prompt: str,
) -> List[ViewSpec]:
    views: List[ViewSpec] = []
    for index in range(num_views):
        source_prompt = prompts[index] if index < len(prompts) else f"front three-quarter view {index + 1}"
        yaw, pitch, roll, zoom = parse_angle_prompt(source_prompt, index, angle_step)
        views.append(
            ViewSpec(
                index=index + 1,
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                zoom=zoom,
                source_prompt=source_prompt,
                conditioned_prompt=build_conditioned_prompt(
                    base_prompt=base_prompt,
                    source_prompt=source_prompt,
                    yaw=yaw,
                    pitch=pitch,
                    roll=roll,
                ),
            )
        )
    return views


def load_generation_pipeline(
    model_id: str,
    controlnet_id: str,
    device: Optional[str] = None,
) -> StableDiffusionControlNetImg2ImgPipeline:
    if StableDiffusionControlNetImg2ImgPipeline is None or ControlNetModel is None:
        raise ImportError(
            "diffusers is not available. Install: pip install diffusers transformers accelerate"
        )

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    controlnet = ControlNetModel.from_pretrained(controlnet_id, torch_dtype=torch_dtype)
    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
        model_id,
        controlnet=controlnet,
        torch_dtype=torch_dtype,
        safety_checker=None,
    )
    pipe = pipe.to(device)
    if hasattr(pipe, "enable_xformers_memory_efficient_attention"):
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception:
            pass
    return pipe


def generate_multiangle_images(
    input_image: Image.Image | np.ndarray | torch.Tensor | str,
    output_dir: str | os.PathLike[str],
    num_views: int = 6,
    angle_step: float = 30.0,
    base_prompt: str = (
        "celadon porcelain product photo, refined ceramic craftsmanship, soft studio lighting, "
        "clean seamless background, premium commercial still life"
    ),
    negative_prompt: str = (
        "different object, duplicate object, broken handle, broken spout, warped silhouette, "
        "deformed, low detail, blur, cluttered background, text, watermark"
    ),
    prompts: Optional[Sequence[str]] = None,
    model_id: str = "runwayml/stable-diffusion-v1-5",
    controlnet_id: str = "lllyasviel/sd-controlnet-canny",
    strength: float = 0.72,
    controlnet_conditioning_scale: float = 0.8,
    guidance_scale: float = 7.0,
    num_inference_steps: int = 30,
    seed: int = 1234,
    export_gif: bool = True,
    export_contact_sheet: bool = True,
    device: Optional[str] = None,
) -> dict:
    source_image = ensure_pil_image(Image.open(input_image) if isinstance(input_image, (str, os.PathLike)) else input_image)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    views = build_default_view_specs(
        prompts=prompts or [],
        num_views=num_views,
        angle_step=angle_step,
        base_prompt=base_prompt,
    )
    pipe = load_generation_pipeline(model_id=model_id, controlnet_id=controlnet_id, device=device)
    device_name = "cuda" if torch.cuda.is_available() and device != "cpu" else "cpu"

    generated_paths: List[str] = []
    frames: List[np.ndarray] = []

    for view in views:
        hint_image = apply_perspective_hint(source_image, view.yaw, view.pitch, view.roll, view.zoom)
        control_image = make_control_image(hint_image)
        generator = torch.Generator(device=device_name).manual_seed(seed + view.index)

        result = pipe(
            prompt=view.conditioned_prompt,
            negative_prompt=negative_prompt,
            image=source_image,
            control_image=control_image,
            strength=strength,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator,
        )
        final_image = add_angle_label(result.images[0], view)
        file_name = f"celadon_view_{view.index:02d}_yaw{int(view.yaw):+03d}_pitch{int(view.pitch):+03d}.png"
        file_path = output_path / file_name
        final_image.save(file_path)
        generated_paths.append(str(file_path))
        frames.append(np.asarray(final_image))

    sheet_path = None
    if export_contact_sheet and generated_paths:
        sheet = build_contact_sheet([Image.open(path) for path in generated_paths])
        sheet_path = str(output_path / "celadon_contact_sheet.png")
        sheet.save(sheet_path)

    gif_path = None
    if export_gif and frames:
        gif_path = str(output_path / "celadon_turntable.gif")
        imageio.mimsave(gif_path, frames, duration=0.45, loop=0)

    manifest = {
        "output_dir": str(output_path),
        "views": [asdict(view) for view in views],
        "images": generated_paths,
        "contact_sheet": sheet_path,
        "gif": gif_path,
        "base_prompt": base_prompt,
        "negative_prompt": negative_prompt,
        "model_id": model_id,
        "controlnet_id": controlnet_id,
        "seed": seed,
    }
    manifest_path = output_path / "celadon_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def build_contact_sheet(images: Sequence[Image.Image], columns: int = 3) -> Image.Image:
    if not images:
        raise ValueError("No images provided for contact sheet")
    widths, heights = zip(*(image.size for image in images))
    cell_w = max(widths)
    cell_h = max(heights)
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (cell_w * columns, cell_h * rows), (255, 255, 255))
    for idx, image in enumerate(images):
        x = (idx % columns) * cell_w
        y = (idx // columns) * cell_h
        sheet.paste(image.resize((cell_w, cell_h), Image.Resampling.LANCZOS), (x, y))
    return sheet


class OpenRHHiddenNodes:
    """
    ComfyUI replacement node for the missing closed-source `RHHiddenNodes`.

    Direct workflow compatibility:
    - type/class name exposed as `RHHiddenNodes`
    - required inputs mirror node 51 in `智能多角度生成【plus】.json`
    - first output `p0` can remain connected to node 26 input `prompt`
    """

    CATEGORY = "celadon/open"
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("p0",)
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pwd": ("STRING", {"default": "1234", "multiline": False}),
                "string_1_1": ("STRING", {"default": ""}),
                "string_2_2": ("STRING", {"default": ""}),
                "string_3_3": ("STRING", {"default": ""}),
                "string_4_4": ("STRING", {"default": ""}),
                "string_5_5": ("STRING", {"default": ""}),
                "string_6_6": ("STRING", {"default": ""}),
            },
            "optional": {
                "source_image": ("IMAGE",),
                "output_dir": ("STRING", {"default": ""}),
                "num_views": ("INT", {"default": 6, "min": 1, "max": 24, "step": 1}),
                "angle_step": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 180.0, "step": 1.0}),
                "base_prompt": (
                    "STRING",
                    {
                        "default": "celadon porcelain product photo, premium ceramic object, consistent object, clean background",
                        "multiline": True,
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "default": "different object, blurry, deformed, duplicate object, bad anatomy, text, watermark",
                        "multiline": True,
                    },
                ),
                "model_id": ("STRING", {"default": "runwayml/stable-diffusion-v1-5"}),
                "controlnet_id": ("STRING", {"default": "lllyasviel/sd-controlnet-canny"}),
                "strength": ("FLOAT", {"default": 0.72, "min": 0.0, "max": 1.0, "step": 0.01}),
                "controlnet_conditioning_scale": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.01}),
                "guidance_scale": ("FLOAT", {"default": 7.0, "min": 1.0, "max": 20.0, "step": 0.1}),
                "num_inference_steps": ("INT", {"default": 30, "min": 1, "max": 100, "step": 1}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2**31 - 1, "step": 1}),
                "export_gif": ("BOOLEAN", {"default": True}),
                "export_contact_sheet": ("BOOLEAN", {"default": True}),
            },
        }

    def run(
        self,
        pwd: str,
        string_1_1: str,
        string_2_2: str,
        string_3_3: str,
        string_4_4: str,
        string_5_5: str,
        string_6_6: str,
        source_image=None,
        output_dir: str = "",
        num_views: int = 6,
        angle_step: float = 30.0,
        base_prompt: str = "celadon porcelain product photo, premium ceramic object, consistent object, clean background",
        negative_prompt: str = "different object, blurry, deformed, duplicate object, bad anatomy, text, watermark",
        model_id: str = "runwayml/stable-diffusion-v1-5",
        controlnet_id: str = "lllyasviel/sd-controlnet-canny",
        strength: float = 0.72,
        controlnet_conditioning_scale: float = 0.8,
        guidance_scale: float = 7.0,
        num_inference_steps: int = 30,
        seed: int = 1234,
        export_gif: bool = True,
        export_contact_sheet: bool = True,
    ):
        prompt_inputs = [
            string_1_1,
            string_2_2,
            string_3_3,
            string_4_4,
            string_5_5,
            string_6_6,
        ]
        views = build_default_view_specs(
            prompts=prompt_inputs,
            num_views=num_views,
            angle_step=angle_step,
            base_prompt=base_prompt,
        )
        prompt_payload = build_qwen_prompt_payload(pwd=pwd, views=views)

        if source_image is not None and output_dir:
            generate_multiangle_images(
                input_image=source_image,
                output_dir=output_dir,
                num_views=num_views,
                angle_step=angle_step,
                base_prompt=base_prompt,
                negative_prompt=negative_prompt,
                prompts=prompt_inputs,
                model_id=model_id,
                controlnet_id=controlnet_id,
                strength=strength,
                controlnet_conditioning_scale=controlnet_conditioning_scale,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                seed=seed,
                export_gif=export_gif,
                export_contact_sheet=export_contact_sheet,
            )

        return (prompt_payload,)


NODE_CLASS_MAPPINGS = {
    "RHHiddenNodes": OpenRHHiddenNodes,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RHHiddenNodes": "RHHiddenNodes",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate multi-angle celadon product images and/or emit RHHiddenNodes-compatible prompt payload."
    )
    parser.add_argument("--input", required=True, help="Path to source image")
    parser.add_argument("--output-dir", required=True, help="Directory for generated images")
    parser.add_argument("--num-views", type=int, default=6, help="How many views to generate")
    parser.add_argument("--angle-step", type=float, default=30.0, help="Yaw step in degrees")
    parser.add_argument("--pwd", default="1234", help="Maps to RHHiddenNodes widget `pwd`")
    parser.add_argument(
        "--base-prompt",
        default="celadon porcelain product photo, refined ceramic object, premium glaze, clean background",
        help="Shared prompt anchor for all generated views",
    )
    parser.add_argument(
        "--negative-prompt",
        default="different object, duplicate object, broken handle, deformed, blurry, bad quality, text, watermark",
        help="Negative prompt",
    )
    parser.add_argument("--model-id", default="runwayml/stable-diffusion-v1-5", help="Diffusers model id or local path")
    parser.add_argument(
        "--controlnet-id",
        default="lllyasviel/sd-controlnet-canny",
        help="Diffusers ControlNet id or local path",
    )
    parser.add_argument("--strength", type=float, default=0.72, help="Img2img strength")
    parser.add_argument("--control-scale", type=float, default=0.8, help="ControlNet conditioning scale")
    parser.add_argument("--guidance-scale", type=float, default=7.0, help="Classifier-free guidance scale")
    parser.add_argument("--steps", type=int, default=30, help="Inference steps")
    parser.add_argument("--seed", type=int, default=1234, help="Base seed")
    parser.add_argument("--no-gif", action="store_true", help="Disable GIF export")
    parser.add_argument("--no-sheet", action="store_true", help="Disable contact sheet export")
    parser.add_argument(
        "--prompt",
        action="append",
        default=[],
        help=(
            "Angle hint from QwenMultiangleCameraNode; repeat up to 6 times. "
            "Example: --prompt \"yaw 45, pitch 10, zoom 1.2, front-right\""
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompts = args.prompt[: args.num_views]
    if not prompts:
        prompts = [f"yaw {i * args.angle_step:.0f}, pitch 0, front product photo" for i in range(args.num_views)]

    manifest = generate_multiangle_images(
        input_image=args.input,
        output_dir=args.output_dir,
        num_views=args.num_views,
        angle_step=args.angle_step,
        base_prompt=args.base_prompt,
        negative_prompt=args.negative_prompt,
        prompts=prompts,
        model_id=args.model_id,
        controlnet_id=args.controlnet_id,
        strength=args.strength,
        controlnet_conditioning_scale=args.control_scale,
        guidance_scale=args.guidance_scale,
        num_inference_steps=args.steps,
        seed=args.seed,
        export_gif=not args.no_gif,
        export_contact_sheet=not args.no_sheet,
    )

    views = build_default_view_specs(
        prompts=prompts,
        num_views=args.num_views,
        angle_step=args.angle_step,
        base_prompt=args.base_prompt,
    )
    prompt_payload = build_qwen_prompt_payload(args.pwd, views)
    prompt_file = Path(args.output_dir) / "rhhiddennodes_prompt.txt"
    prompt_file.write_text(prompt_payload, encoding="utf-8")

    print(json.dumps({"manifest": manifest, "prompt_file": str(prompt_file)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
