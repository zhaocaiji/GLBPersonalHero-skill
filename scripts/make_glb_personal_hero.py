from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"
TEMPLATE = ASSETS / "glb_personal_hero_template.html"
SIGNAL_CARD_IMAGE = ASSETS / "signal-card-image.png"
TEMPLATE_CLASSES = {
    "studio": "theme-studio",
    "graphite": "theme-graphite",
    "gallery": "theme-gallery",
    "signal": "theme-signal",
}
DEFAULT_TEMPLATE_ORDER = ("gallery", "studio", "graphite", "signal")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a GLB runtime personal hero website.")
    parser.add_argument("--model", required=True, help="GLB file path. Relative paths resolve from cwd.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    parser.add_argument("--prefix", default="glb_personal_hero", help="Output HTML prefix.")
    parser.add_argument("--template", default="gallery", choices=[*sorted(TEMPLATE_CLASSES), "all"])
    parser.add_argument("--title", default="Alex Chen")
    parser.add_argument("--email", default="hello@example.com")
    parser.add_argument("--screen-video", default="", help="Optional MP4/WebM video texture for meshes named screen/screen_ref.")
    parser.add_argument("--port", type=int, default=18788, help="Preview bat server port.")
    return parser.parse_args()


def resolve_model(model: str) -> Path:
    path = Path(model)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def resolve_optional_file(file_path: str) -> Path | None:
    if not file_path:
        return None
    path = Path(file_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def write_start_bat(out_dir: Path, html_name: str, port: int, bat_name: str = "start_preview.bat") -> None:
    bat = f"""@echo off
setlocal
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "PORT={port}"
set "PAGE={html_name}"

pushd "%ROOT%" || (
  echo Failed to enter output folder:
  echo %ROOT%
  pause
  exit /b 1
)

echo.
echo GLB Personal Hero Preview
echo Root: %CD%
echo Preferred port: %PORT%
echo.
echo Keep this window open while previewing.
echo Press Ctrl+C to stop the server.
echo.

:find_port
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) {{ exit 1 }} else {{ exit 0 }}"
if errorlevel 1 (
  set /a PORT+=1
  goto find_port
)

set "URL=http://localhost:%PORT%/%PAGE%"
echo URL : %URL%
echo.

where py >nul 2>nul
if not errorlevel 1 (
  start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Milliseconds 800; Start-Process '%URL%'"
  pushd "%ROOT%"
  py -3 -m http.server %PORT%
  popd
  goto done
)

where python >nul 2>nul
if not errorlevel 1 (
  start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Milliseconds 800; Start-Process '%URL%'"
  pushd "%ROOT%"
  python -m http.server %PORT%
  popd
  goto done
)

echo Python was not found. Please install Python or add it to PATH.

:done
echo.
echo Server stopped or failed to start.
pause
"""
    (out_dir / bat_name).write_text(bat, encoding="utf-8")


def render_html(template_name: str, model_name: str, title: str, email: str, screen_video_name: str = "") -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__TEMPLATE_CLASS__", TEMPLATE_CLASSES[template_name])
    html = html.replace("__MODEL_FILE__", model_name)
    html = html.replace("__SCREEN_VIDEO_FILE__", screen_video_name)
    html = html.replace("Alex Chen", title)
    html = html.replace("hello@example.com", email)
    return html


def write_metadata(out_dir: Path, prefix: str, template_name: str, model: Path, html_name: str, screen_video: Path | None) -> None:
    metadata = {
        "model": model.name,
        "source_model": str(model),
        "screen_video": screen_video.name if screen_video else "",
        "source_screen_video": str(screen_video) if screen_video else "",
        "template": template_name,
        "html": html_name,
        "runtime": "three-gltf",
        "animation": "auto-play glTF animation clips",
        "head_tracking": "Head/Neck bones, mouse-driven, mouse wins over animation rotation tracks",
        "lighting": "none added by page; loaded GLB lights disabled",
        "tone_mapping": "THREE.ACESFilmicToneMapping",
        "exposure": 1,
    }
    (out_dir / f"{prefix}_{template_name}.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def write_index(out_dir: Path, prefix: str, templates: list[str]) -> None:
    links = "\n".join(
        f'        <a class="card" href="./{prefix}_{name}.html"><span>{name}</span><small>Open {name} template</small></a>'
        for name in templates
    )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GLB Personal Hero Templates</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #101010;
      color: #f7f2ee;
      font-family: Inter, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
    }}
    main {{ width: min(960px, calc(100vw - 40px)); padding: 56px 0; }}
    h1 {{ margin: 0 0 12px; font-size: clamp(42px, 8vw, 92px); line-height: .9; letter-spacing: 0; }}
    p {{ margin: 0 0 32px; max-width: 620px; color: rgba(247, 242, 238, .68); line-height: 1.6; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
    .card {{
      min-height: 148px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: inherit;
      text-decoration: none;
      border: 1px solid rgba(255,255,255,.14);
      background: rgba(255,255,255,.06);
    }}
    .card:hover {{ background: rgba(255,255,255,.12); }}
    .card span {{ font-size: 22px; font-weight: 800; text-transform: uppercase; }}
    .card small {{ color: rgba(247, 242, 238, .62); }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <h1>GLB Personal Hero</h1>
    <p>Choose one generated personal website template. The GLB is loaded at runtime from the local models folder, embedded animation clips autoplay, and Head/Neck bones follow the mouse when available.</p>
    <div class="grid">
{links}
    </div>
  </main>
</body>
</html>
"""
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    model = resolve_model(args.model)
    screen_video = resolve_optional_file(args.screen_video)
    if not model.exists():
        raise FileNotFoundError(model)
    if screen_video and not screen_video.exists():
        raise FileNotFoundError(screen_video)
    if model.suffix.lower() != ".glb":
        raise ValueError("GLBPersonalHero expects a .glb file.")
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    asset_dir = out_dir / "assets"
    model_dir = out_dir / "models"
    media_dir = out_dir / "media"
    asset_dir.mkdir(exist_ok=True)
    model_dir.mkdir(exist_ok=True)
    media_dir.mkdir(exist_ok=True)

    shutil.copytree(ASSETS / "vendor", asset_dir / "vendor", dirs_exist_ok=True)
    if SIGNAL_CARD_IMAGE.exists():
        shutil.copy2(SIGNAL_CARD_IMAGE, asset_dir / SIGNAL_CARD_IMAGE.name)
    runtime_model = model_dir / model.name
    shutil.copy2(model, runtime_model)
    runtime_screen_video: Path | None = None
    if screen_video:
        runtime_screen_video = media_dir / screen_video.name
        shutil.copy2(screen_video, runtime_screen_video)

    templates = list(DEFAULT_TEMPLATE_ORDER if args.template == "all" else (args.template,))
    generated_html: list[str] = []
    for template_name in templates:
        html_name = f"{args.prefix}_{template_name}.html"
        (out_dir / html_name).write_text(
            render_html(template_name, model.name, args.title, args.email, runtime_screen_video.name if runtime_screen_video else ""),
            encoding="utf-8",
        )
        write_metadata(out_dir, args.prefix, template_name, model, html_name, screen_video)
        write_start_bat(out_dir, html_name, args.port, f"start_{template_name}.bat")
        generated_html.append(html_name)

    write_index(out_dir, args.prefix, templates)
    default_html = f"{args.prefix}_gallery.html" if "gallery" in templates else generated_html[0]
    write_start_bat(out_dir, default_html, args.port, "start_preview.bat")

    for html_name in generated_html:
        print(f"html={out_dir / html_name}")
    print(f"model={runtime_model}")
    if runtime_screen_video:
        print(f"screen_video={runtime_screen_video}")
    print(f"index={out_dir / 'index.html'}")
    print(f"start={out_dir / 'start_preview.bat'}")


if __name__ == "__main__":
    main()
