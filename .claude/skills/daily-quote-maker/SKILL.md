---
name: daily-quote-maker
description: Create emotional photographic literature cards from verified Korean or translated quotations and genuine high-resolution photographs, with configurable center/upper/side typography, independent 4:5 and optional 9:16 crops, concise captions, visual QA and source archiving. Use for Daily Quote Maker, 명언제조기, 문학 문구 이미지. Publishing and scheduled production are paused pending explicit user resumption.
version: 1.1.0
---

# Daily Quote Maker v1.1

## 0. Current operating state — PAUSED
- Do not publish to Instagram or Threads, create a new scheduled task, or reactivate automation `6adce8c3eea08191be7dab5261338783` until the user reviews the actual images and explicitly requests resumption.
- Keep `comfunnylj/telegram-market-feed/social-publisher/automation/tasks.json` task `quote.enabled=false`; verify `social-publisher/automation/quote.json` has an empty `jobs` array. Preserve every other task, existing Instagram queue, tokens and server configuration.
- Rendering, testing, saving and preparing LOCAL payloads are separate from publication. Never mark a source quote approved or record an SNS success merely because an image exists.

## 1. Canonical files and live databases
- Edit this existing repository and branch, never a duplicate skill/repository: `comfunnylj/Video-creator`, branch `claude/eloquent-hamilton-wvxqej`.
- Skill: `.claude/skills/daily-quote-maker/SKILL.md`; implementation, quality policy, examples, tests and changelog: `daily-quote-maker/`.
- Read the live Google Sheet before selecting content: https://docs.google.com/spreadsheets/d/1be-g64yNrQ6d3bAT-lopUpjZmDRBnhfe_1YAP674BjE/edit . Preserve all 65 IDs, `문구DB`, `사진DB`, approval columns and `게시이력`. Never replace it with an old snapshot.
- Skill/manual archive: https://drive.google.com/drive/folders/1bnoleQJiWi9Lz7jjbQnOfKUrC5U-1D_6 . Update the existing two Docs in place rather than proliferating manuals.
- Project: https://drive.google.com/drive/folders/1dtgJ6i001xNdCklwWc8u9SJh6OUnFiYA . Save finished JPEGs, captions and production/source records in its `Output` folder, ID `1hYu1BjrmtG3jBmDrOrRCr7aJpPgYOUPM`; read back metadata after saving.

## 2. Editorial contract
- Balance 힘/성취/위로 over future approved production; preserve exact quote/author/work and source/context. Keep historical spelling modernization and original translation clearly distinguished from verbatim quotation.
- On the card show only the literary excerpt, a distinctly smaller author and a concise work title. Put biography, context and hashtags in a separate 2–4 sentence caption.
- Do not invent composition dates, motives or biographical circumstances. Avoid imposing a lesson or excessive emotion.
- For user-provided original text, set `user_original=true`. Leave unspecified author/work blank; never invent credits. Nonempty credits require `attribution_approved=true` after the user supplies/approves them. Keep `source_verified=true` only when the exact supplied text has been checked. This exception does not change the existing 65 literary DB rows.
- User rights evaluation and actual posting permission are separate from source accuracy. All v1.1 samples remain NOT_PUBLISHED.

## 3. Photographic literature archive design
Read `daily-quote-maker/QUALITY_POLICY.md` and compare actual user references before choosing a source.
- Prefer real still photographs from Unsplash → Pexels → Pixabay → Wikimedia Commons → public archives/공공누리. Record page, photographer, license URL, actual decoded pixels and checksum.
- Require at least 3000px long edge and enough native pixels AFTER each crop. No preview enlargement, artificial upscaling, heavy denoise or sharpening. An asserted resolution is not proof of sharpness.
- Seek emotional fit, clear negative space and a viable crop rather than a spectacular tourism view. Warm sunset/lake, dark night paths, starry snow mountains, glimmering water and overcast city scenes are all valid; Seoul is not mandatory.
- Long-exposure stills are welcome. Do not use time/hyperlapse video. Never reuse rejected Pexels ID `37522118`.
- Preserve natural photographic color. No universal desaturation, darkening, contrast filter or middle shading. If text cannot be read, change position/color/crop/photo, not the whole photograph.
- Center: center or slightly above, with distant sky. Upper: upper third, keeping lower subjects clear. Side: upper-right or lower-right negative space. Users may specify positions; `recommend=true` ranks candidate positions by local contrast, texture and explicitly protected subject rectangles. It does NOT understand semantic subjects; human inspection remains required.
- Korean serif/Myeongjo first. Default quote 38px; quiet samples around 36px, brighter short text may use 44–52px. User-configurable range 28–72px; author/work 16–27px and always smaller than the minimum quote size. Judge at mobile width before approval.
- White/ivory on dark areas, charcoal/black on bright areas. No frames, logo, badge, divider, text box, heavy shadow or outline. Shadows default to none; optional <=45/255 opacity, <=2px offset only.

## 4. Reproducible rendering
Install Python 3.11+ dependencies from `daily-quote-maker/requirements.txt` and a Korean serif font (Noto Serif CJK or Nanum Myeongjo). Set `QUOTE_FONT_PATH` if not installed at an auto-detected path.

```bash
python daily-quote-maker/render_quote_card.py --job daily-quote-maker/examples/A_warm_lake.json --output output/A
python daily-quote-maker/render_quote_card.py --job daily-quote-maker/examples/B_star_mountain.json --output output/B --formats 4:5 9:16
python daily-quote-maker/render_quote_card.py --job job.json --config daily-quote-maker/examples/design_config.json --output output/custom
python -m unittest discover -s daily-quote-maker/tests -v
```

- Default output is ONE 1080×1350 4:5 sRGB JPEG at quality 96, 4:4:4. Request 9:16 explicitly via `--formats 4:5 9:16`; independently crop the oriented original and reflow type, never stretch the feed image.
- Existing quote/job and publisher provenance fields remain compatible. `photo.local_path` optionally uses an already downloaded original while retaining provenance. `design.style` is shared; `design.formats['9:16']` overrides only that ratio. An external `--config` JSON overrides inline design. CLI `--formats` overrides the config's `output_formats`.
- Adjust font, size, color, position, alignment, line_spacing, quote width, author/work formatting, crop_center, safe margins and protected_regions in JSON, never Python for routine design changes. See `examples/design_config.json` and `OPERATING_MANUAL.md` for units and examples.
- EXIF rotation precedes crop and subject coordinates. Embedded ICC converts to sRGB; untagged images are explicitly recorded as assumed sRGB. Decode actual pixels, validate glyph coverage, reject transparency, inspect output bytes/dimensions/profile and record all text boxes, crop bounds, font path, contrast, hashes and effective settings.
- Readability gate: each line's actual glyph interiors must have at least 88% samples with contrast >=3:1. Record p10 contrast and coverage; this photographic heuristic is not a WCAG compliance claim and does not replace mobile visual review.
- Render all requested formats and metadata into staging before installing the batch. Failed rendering preserves previous outputs; successful feed-only rerender removes stale same-quote story exports. Use a separate output directory per job.

## 5. Required visual review and saving
- Open full-size final JPEGs, mobile-width previews and 100% source/crop details. Compare references side by side. Inspect quote size, spacing, emotional fit, visible detail, subject preservation, attribution and source accuracy.
- Code success is not visual approval. Write a separate review record with evidence, adjustments and limitations. Generated provenance starts with `visual_review=REQUIRED`; a reviewer must record the actual result. Never fabricate passing QA.
- Preserve source/checksum, resolved style and plain captions with outputs. Source photos are evidence, not social posting approval. Archive real files then read back Drive metadata (parent, dimensions/size, modified time).
- `build_publisher_payloads.py` remains a local, non-submitting adapter. Its explicit approval flag and pinned SHA URL validation still apply when the user later resumes posting. No queue writes in this paused release.

## 6. Maintenance / rollback
Keep SKILL, QUALITY_POLICY, renderer, example JSON, tests, workflows and Drive manual on version 1.1.0. Run regression tests and real-photo QA after relevant changes. Record changes/test results in CHANGELOG; use Git history for v1.0 restoration, preserving databases and other workflows. Do not claim that a repository skill is account-level ChatGPT installation.

Install renderer dependencies from the single `daily-quote-maker/requirements.txt` in every rendering workflow, including user-original samples. Run all 19 regression cases after changes. See `REVALIDATION_20261029.md` for the renewed photo, visual, failure-log and storage checks; a historical failed run alone does not show that the current implementation is broken.
