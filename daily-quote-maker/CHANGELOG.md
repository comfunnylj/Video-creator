# Change log

## 1.1.0 maintenance verification — 2026-10-29 (Asia/Seoul)
- Reconcile the old failed user-original workflow: run 40195292739 failed because fontTools was missing; fix c85a850 already installed it, and subsequent runs 40195474147, 40195659964 and 40195857726 succeeded. October 27–28 unrelated issue events skipped quote jobs; they were not failed renders.
- Use the shared requirements.txt for the user-original workflow and include that workflow in regression path filters, avoiding dependency drift.
- Add original-text attribution/empty-credit and external-config/CLI precedence coverage: 19 offline tests pass. Document the original-text contract in SKILL and manual; forward-test the blank-credit case locally.
- Rerender A/B/C as 1080×1350 and independent 1080×1920 sRGB JPEGs from archived originals. Visually review all six, mobile preview and original native detail.
- Move C story text from y=.63 to .50 to reduce interference from water highlights, without grading the photo. Minimum line contrast coverage improves from 93.14% to 99.35%.
- Keep automated production/publication paused, existing DBs untouched and other social tasks unchanged. See REVALIDATION_20261029.md and renewed Output records.

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
