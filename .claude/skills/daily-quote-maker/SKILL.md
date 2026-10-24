---
name: daily-quote-maker
description: Create high-resolution poetic Korean/English quote cards and optional slow real-time landscape reels from verified literature and real photography; write concise Korean social captions; archive source and outputs; route approved posts to existing Instagram/Threads social publisher. Use for Daily Quote Maker, 명언 제조기, 문학 문구 카드, 한강 감성 사진/릴스.
version: 1.0.0
---

# Daily Quote Maker v1.0 — living skill

## 0. Source of truth
- The editable Google Sheet is `Daily Quote Maker_명언·시·소설 문구 DB_v1`:
  `https://docs.google.com/spreadsheets/d/1be-g64yNrQ6d3bAT-lopUpjZmDRBnhfe_1YAP674BjE/edit`.
  It currently contains 65 IDs in the `문구DB` tab, with `게시이력` for verified publication URLs. Always **read it live** before selection. Never assume an old GitHub snapshot reflects later corrections.
- Google Drive asset folder: `프로젝트/멀티미디어/명언제조기`,
  `https://drive.google.com/drive/folders/1dtgJ6i001xNdCklwWc8u9SJh6OUnFiYA`.
- Skill and manual canonical archive: `프로젝트/Skill & Manual/daily-quote-maker` (create and use this folder).
- All files here are source/editable. Users may request changes anytime. Increment version and update GitHub + Drive copy; do not claim static account-level ChatGPT skill installation merely because files exist.

## 1. Content/editorial rules
1. Select one literary excerpt or attributed quotation, balancing `힘`, `성취`, `위로` and avoiding recently used IDs.
2. Verify author, original work, **exact source text** and context. Preserve the user's preferred Korean original when it exists. Keep modernized historical spellings distinct from verbatim quotations.
3. User handles copyright evaluation separately. Do not filter source discovery solely by age of author. **Publication status is separate**: never turn source discovery alone into an approved live post.
4. The card contains only the quote, then small author and work attribution. Do not put historical commentary, biographies, hashtags or long explanations on the artwork.
5. Write a polished Korean caption of **2–4 short sentences**: author/work context, social or historical relevance if verified, one concise reflection; then optionally 2–4 suitable hashtags. Do not invent circumstances of composition or overconfident biographical details.
6. No repeated quotes, misleading author attribution, invented source URLs or fabricated publication confirmations.

## 2. Photography (highest-priority aesthetic contract)
- Read `daily-quote-maker/QUALITY_POLICY.md` first and follow it.
- Prefer beautiful **real high-resolution, long-exposure still photography** with Seoul skyline/Han River, sky, mountain, city, rivers and seasonal landscapes. Search Unsplash, Pexels, Pixabay, Korean public sources. Use actual source files, not image query thumbnail or AI recreation, whenever requested.
- Reject all timelapse, hyperlapse, accelerated or sped-up video.
- Prefer original stills of at least 3000px long edge. Verify **actual original** pixels and sharpness, choose 4:5 1080×1350 for Instagram and Threads; for motion prefer vertical 9:16 1080×1920, only with naturally moving real-time footage and native resolution sufficient for the crop.
- Original Pexels reel ID `37522118` from 2026-10-24 was rejected. Never reuse.
- Text should be modest-sized Korean serif in soft white on dark background (or dark text on bright sky), placed central/upper-middle where there is breathing room. No synthetic decorative frames, large logos, decorative badges, big faces or tiny unreadable type. Human-review the final picture; compare examples user supplied.
- Do not create visually unsatisfactory content just to meet schedule. If source crop fails, choose a better photograph or skip the day and report.

## 3. Technical outputs
- Produce 1080×1350 RGB JPEG for Instagram (4:5) plus optional 1080×1920 for Reels; retain source page, photographer, original dimensions, source checksum, crop bounds and reproducible rendering parameters in JSON.
- Use Pillow/ffmpeg as already present in Video-creator, but no forced upscaling of small/soft imagery. Render proper Korean fonts.
- Avoid excessive compression. QA: text not clipped, 100% crop sharp, reliable source, all 4 corners clear of app UI where applicable, no spelling errors. Name `YYYYMMDD_Q<id>_short-title_IG.jpg`.
- Return final image in chat, plus a short caption; archive verified files under the Google Drive folder. Maintain the spreadsheet's `게시이력` only when status is confirmed.
- Production files should be modifiable: Python renderer, configurable JSON themes, quotes DB, image metadata.

## 4. Automation / publishing adapters
- **Instagram** currently uses `comfunnylj/telegram-market-feed/social-publisher/instagram/outbox.json`. Existing independent `instagram-publisher` accepts a SHA256-verified public immutable JPEG URL, size, caption, `media_type=image`, `approved=true`, account `genie_carrot`, stable `dedup_key` and not_before/expires_at. Existing status and tokens must not be changed without a safe migration. Never fabricate success. Follow that repo's `social-publisher/instagram-service/README.md`.
- **Threads** currently uses `social-publisher/automation/tasks.json`, each registered task has its own outbox, and Oracle polls. Register a dedicated `quote` task and `social-publisher/automation/quote.json`. Check live bridge health/capabilities before enabling; follow `social-publisher/AUTOMATION.md`.
- Public images for either publisher must be committed to GitHub and addressed via immutable commit-SHA raw.githubusercontent.com URL; verify exactly matching SHA256 and size before queueing. The social publisher must not interpret prepared/pending as published. Once the account returns a permalink and final published receipt, record it in `게시이력`. On unknown response avoid blind retry with a new ID.
- The workflow may be run manually with a specifically reviewed source. To automate unattended daily publication, first create a **curated accepted photo bank** and initial tested scripts, establish credential-free or secured access to approved quote records, and confirm receipt reconciliation. If any of these cannot be verified, keep publication disabled and clearly show setup remaining rather than silently posting poor photos or publishing unapproved drafts.
- Proposed time, Asia/Seoul: Instagram 09:00, Threads 09:10; schedule only after operational safeguards and queue readiness.

## 5. Maintenance
- GitHub folder: `.claude/skills/daily-quote-maker/` is the skill; `daily-quote-maker/` holds code and quality docs.
- User may revise fonts, photos, crops, channels, captions, author biographies, schedule or categories at any time. Make targeted changes, run tests, update version, and re-archive `Skill & Manual`; preserve previous release for rollback.
- Never post arbitrary new copyright assumptions: user's rights judgments are separate; maintain a clear user approval column for actual publishing.
