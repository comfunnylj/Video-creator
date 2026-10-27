# Lemo-Opuscar: isolated upstream renderer proof

This is an independent proof of concept, not the existing Video Creation (Artlist/Seedance) or Travel TOP5 Shorts system.

## Run location and safety

- Repository: `comfunnylj/Video-creator`, GitHub-hosted **ubuntu-latest** ephemeral GitHub Actions runner.
- No SSH connection to Oracle; no Oracle IP/keys/tokens used.
- No edits to `social-publisher`, other workflows, Travel TOP5 skill or Daily Quote Maker.
- No API key or paid video generation service is necessary for this code-authored steampunk sample.
- GitHub Actions runner usage may consume minutes under the user's plan. Third-party upstream dependencies are installed afresh from public package registries.

## Exact execution

Trigger the workflow manually under **Actions → Lemo-Opuscar - original HD2D steampunk render → Run workflow**, or edit/create a GitHub Issue whose body starts with `LEMO_STEAMPUNK_V1` **as the repository owner**. Nonowner issues are skipped.

Workflow file: `.github/workflows/lemo-opuscar-steampunk.yml`

Pipeline:
1. Clone **official upstream** `lemomo-ai/lemo-opuscar` in the temporary runner workspace with sparse checkout.
2. Run the upstream `plugin/skills/lemo-opuscar/scripts/setup.sh deps` to install upstream core, Node dependencies, Python packages and Chromium headless shell.
3. Use `core/render/still.mjs` to render inspection frames.
4. Use **upstream** `core/render/video.mjs` on our original `steampunk-hd2d/index.html` scene, 800×450, 24fps, 10s.
5. Write a new synthesised soundtrack from `score.py`, then call **upstream** `core/render/mux.sh` with zero film grain.
6. Check output with `ffprobe` for H.264, AAC audio, width/height and duration.
7. Upload MP4, still frames, ffprobe JSON, source code and upstream commit SHA to GitHub Actions artifact `lemo-steampunk-hd2d-original`, retained for 14 days.

## Fidelity and limits

Our independently authored Three.js film includes a real 3D diorama, 2D sprite adventurer, animated clock gears, moving airship, steam plumes, dynamic lights and shadowed geometry. It follows the published upstream HD-2D style guide, but **is not the upstream HD-2D demo** and does not reproduce every advanced post-processing shader/technique in that demo. HD-2D is Square Enix's trademark: do not imply Square Enix endorsement or use the term as the film's brand/title.

This runner does not automatically call Claude Code or any LLM to invent a new film from a text prompt. It executes the authored, version-controlled film script. General prompt-to-video generation would require separate coding-agent orchestration, rate controls, security review and explicit authorization.

## Related links

- Official library: https://github.com/lemomo-ai/lemo-opuscar
- Upstream style specification: https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/hd-2d/STYLE.md
- Local skill: `.claude/skills/lemo-opuscar/SKILL.md`
- First test issue: https://github.com/comfunnylj/Video-creator/issues/22

## Troubleshooting

- If the workflow has no jobs and a red X on push, check unsupported GitHub expression contexts in YAML. Job-level `env` must not use `runner.temp`; here `github.workspace` is used.
- If upstream clone fails, check GitHub access in the Actions logs; do not retry via Oracle.
- If Chromium fails, check Ubuntu libraries, headless Chrome install and `LEMO_ANGLE=swiftshader`; software GL will be slow.
- If `READY` times out, check `index.html` imports, console errors and local `window.READY` / `window.render(t)`.
- If no MP4, review step logs. An artifact containing only source/stills is **not successful video production**.
