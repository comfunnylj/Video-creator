# Change log

## 1.1.0 — 2026-10-25
- Replace fixed white centered text and global middle shading with configurable center/upper/side photographic typography. No global color grade or default shadow.
- Make 4:5 the only default. Generate 9:16 only on explicit request, with independent source crop and ratio-specific type overrides.
- Add JSON style/config support: fonts, sizes, colors, position, alignment, line spacing, attribution styles, crop centers, subject rectangles and recommendation.
- Verify actual decoded pixels, EXIF, ICC/sRGB, complete glyph coverage, native crop, safe bounds, local glyph contrast, final JPEG and SHA256. Reject transparent type and banned source 37522118.
- Stage every format and provenance before replacing outputs; rollback installation failure and remove stale same-quote story exports after a successful feed-only rerender.
- Preserve quote/job/provenance and local publisher payload compatibility. Keep the 65-row live DB, photo DB and posting history unchanged.
- Add three real-photo example jobs and separate design config. Record reference comparison and 100%/mobile visual review separately from code success.
- Replace issue-triggered sample generation with offline push/PR regression; real-photo sample rendering is manual opt-in only. No scheduled production or publishing workflow introduced.
- Operational hold: existing 09:00 automation stays disabled; disable only Threads quote receiver, verify empty quote queue, preserve other sources and Instagram jobs.
- Validation: 16 offline regression cases cover EXIF, insufficient native pixels, contrast, glyphs, transparency, independent ratios, protected subjects, transactional rerender, stale outputs, source gates and payload compatibility. Real samples: A/B/C feed + story, visually reviewed. Actual test transcript and review record accompany Output.

## 1.0.0
Existing release preserved in Git history; baseline commit 46d6966b646b365b90e89ba182ccceb575cae38b.
