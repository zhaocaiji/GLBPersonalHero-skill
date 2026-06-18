---
name: GLBPersonalHero-skill
description: Generate a personal website hero directly driven by a provided GLB model. Use when the user wants to upload a compressed GLB, choose a personal website template, preserve built-in GLB animation, and output a runtime Three.js HTML page with mouse-driven Head/Neck tracking.
---

# GLBPersonalHero-skill

Use this workflow to turn a user-provided `.glb` model into a runtime personal website. The final page loads the GLB directly, plays embedded animation clips, and drives Head/Neck bones with the mouse when those bones exist.

## Workflow

1. Get the `.glb` path from the user.
2. Before running the generator, always present the four template choices: `studio`, `graphite`, `gallery`, and `signal`. Show or reference the preview images in `assets/template-previews/` when the environment can display local images. Ask the user to choose one template. Do not silently default unless the user explicitly says they do not care, asks you to choose, or requests `all`.
3. After installing this skill from GitHub, verify that both `scripts/` and `assets/` exist. If the checkout only contains root files because sparse checkout is enabled, run `git sparse-checkout disable` in the installed skill repository before continuing.
4. Run the bundled generator:

```powershell
python <skill-folder>\scripts\make_glb_personal_hero.py --model <model.glb> --out-dir <output-folder> --prefix <output-prefix> --template gallery --screen-video <screen.mp4> --port 18788
```

5. Deliver the generated HTML, copied `models/<model>.glb`, `assets/`, metadata JSON, `index.html`, `start_preview.bat`, and per-template `start_<template>.bat` files.
6. Verify through a local HTTP server. Do not verify with `file://`. After starting a `.bat`, read `preview_url.txt` or `.preview-url` to get the actual localhost URL because the launcher increments the port when the requested port is busy.

## Runtime Rules

- Use GLTFLoader and local bundled Three.js assets.
- Use `THREE.ACESFilmicToneMapping` and exposure `1`.
- For gallery, use the bundled viewer-style key/fill/plane lights unless the user explicitly asks for GLB-only lighting.
- Loaded GLB lights are hidden; the generated page may add template-controlled key/fill/plane lights.
- Autoplay all embedded GLB animation clips.
- If Head/Neck bones exist, mouse movement controls those bones.
- When the pointer is idle, make Head/Neck slowly wander in a small randomized range.
- Mouse direction: moving up raises the head; moving down lowers it; left/right maps to left/right look.
- If animation clips also animate Head/Neck rotation, filter those tracks so mouse tracking stays stable.
- If `gltf.animations.length === 0`, tell the user the animation was not exported into the GLB and must be re-exported from the 3D tool with animation enabled.
- If `--screen-video` is provided, copy it to `media/` and apply it as a `VideoTexture` to meshes whose names include `screen`; hide `screen_ref`.
- Keep texture channel sanitization enabled by default. It forces runtime texture channels above 0 back to 0 to avoid Three.js shader errors such as `uv7 undeclared identifier`. Only disable with `--no-sanitize-texture-channels` when the user explicitly needs multi-UV materials and has verified the target runtime supports them.

## Validation Notes

- Read the generated metadata JSON after generation. It records animation count/names, Head/Neck candidates, screen mesh candidates, hidden `screen_ref` candidates, texture channels above 0, lighting mode, and the preview URL file.
- If `--screen-video` is used but metadata has no `screen_mesh_candidates`, tell the user the GLB mesh names need to include `screen`.
- If the browser console logs sanitized textures, that is expected for GLBs exported with high UV channels. If the model looks wrong after sanitization, ask the user for a GLB with textures on UV0.

## Templates

- `studio`: lab/editorial layout.
- `graphite`: cold minimal portfolio.
- `gallery`: dark orange-red creative layout.
- `signal`: dopamine/streetwear layout.

Each template sets CSS variables for model scale, camera padding, default yaw, offset, and mouse tracking strength.
