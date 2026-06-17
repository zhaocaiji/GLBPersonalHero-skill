---
name: GLBPersonalHero-skill
description: Generate a personal website hero directly driven by a provided GLB model. Use when the user wants to upload a compressed GLB, choose a personal website template, preserve built-in GLB animation, and output a runtime Three.js HTML page with mouse-driven Head/Neck tracking.
---

# GLBPersonalHero-skill

Use this workflow to turn a user-provided `.glb` model into a runtime personal website. The final page loads the GLB directly, plays embedded animation clips, and drives Head/Neck bones with the mouse when those bones exist.

## Workflow

1. Get the `.glb` path from the user.
2. Ask the user to choose one template unless they already named one: `studio`, `graphite`, `gallery`, `signal`, or `all`. Default to `gallery` when they do not care. Use `all` when they want a selectable demo package.
3. Run the bundled generator:

```powershell
python <skill-folder>\scripts\make_glb_personal_hero.py --model <model.glb> --out-dir <output-folder> --prefix <output-prefix> --template gallery --screen-video <screen.mp4> --port 18788
```

4. Deliver the generated HTML, copied `models/<model>.glb`, `assets/`, metadata JSON, `index.html`, `start_preview.bat`, and per-template `start_<template>.bat` files.
5. Verify through a local HTTP server. Do not verify with `file://`.

## Runtime Rules

- Use GLTFLoader and local bundled Three.js assets.
- Use `THREE.ACESFilmicToneMapping` and exposure `1`.
- For gallery, use the bundled viewer-style key/fill/plane lights unless the user explicitly asks for GLB-only lighting.
- Autoplay all embedded GLB animation clips.
- If Head/Neck bones exist, mouse movement controls those bones.
- When the pointer is idle, make Head/Neck slowly wander in a small randomized range.
- Mouse direction: moving up raises the head; moving down lowers it; left/right maps to left/right look.
- If animation clips also animate Head/Neck rotation, filter those tracks so mouse tracking stays stable.
- If `gltf.animations.length === 0`, tell the user the animation was not exported into the GLB and must be re-exported from the 3D tool with animation enabled.
- If `--screen-video` is provided, copy it to `media/` and apply it as a `VideoTexture` to meshes whose names include `screen`; hide `screen_ref`.

## Templates

- `studio`: lab/editorial layout.
- `graphite`: cold minimal portfolio.
- `gallery`: dark orange-red creative layout.
- `signal`: dopamine/streetwear layout.

Each template sets CSS variables for model scale, camera padding, default yaw, offset, and mouse tracking strength.
