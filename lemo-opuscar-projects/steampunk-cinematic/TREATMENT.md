# IRON AURORA — Original Lemo-Opuscar render treatment (2026-10-27)

**Target:** A code-rendered cinematic steampunk city, not a photo-pan, static-image effect or HD-2D sprite diorama. 10 seconds, 16:9, 24 fps.
**Provenance:** The authored scene lives in `lemo-opuscar-projects/steampunk-cinematic/index.html` and is rendered by the upstream `lemomo-ai/lemo-opuscar` `core/render/still.mjs` and `core/render/video.mjs`. It is not one of the official demonstrations.
**Style reference:** Original Lemo-Opuscar materials/3D family; physical materials, light, atmospheric depth and detailed movement in a fully modelled fictional environment.
**Design:** Late-Victorian copper/oxidised-brass industrial canal city at dawn; PBR materials with roughness variation, procedural masonry, iron beams and railings, water canal, dense gothic facades, giant 3D mechanical clock tower, realistic dirigible, moving gears, gas lamps and subtle rising smoke. No pixel-sprite look, no raster backdrop, no fake photo zoom.
**Camera:** Slow forward dolly and crane over a waterway toward the heroic clock tower in one continuous shot.
**Cue sheet:** 0–2.5s reveal the canal and clock city; 2.5–5.4s airship crosses the skyline; 5.4–8s gears/clock/lamps; 8–10s final city reveal with cinematic sound swell. Time-deterministic `window.render(t)`.
**Camera/render tests:** Still render at 0, 5, 8 seconds, then final video. H.264/AAC, 10 seconds. No external paid video model. Additional GPU/CPU burden due to Three.js physically based shaders.
**Audio:** Custom synthesized engine hum, chime, low brass-like tones, steam release from Python stdlib; verified 10s WAV. Original `mux.sh` is attempted, with safe FFmpeg fallback only if upstream WAV-duration validation spuriously rejects a fully decoded file.
**Honest limitation:** A CPU-rendered 3D film is not guaranteed Hollywood photorealism. The result must be judged from the actual render; technical QA does not prove aesthetic excellence. External video or remote services are not used.
**Isolation:** GitHub-hosted runner only. No Oracle SSH, Social Publisher changes, posting, or edits to other workflows.