# pappichulo-website
interactive world website for pappi chulo

## Test walk (live)
Open on your phone: https://t0rr0s.github.io/pappichulo-website/

- Swipe up to walk forward. Swipe down to go back.
- Drag sideways to look around.
- "Move your phone to look" (top right) turns on tilt-to-look.
- Day / Night switch at the top. After 7 pm Goa time it opens on Night by itself.
- Add `?lite` to the link to test the simple version (no walking clips).

The pictures are placeholders made by `tools/make_placeholders.py`. Real 360 shots replace them with the same file names.

## What's where
- `index.html`: the whole test walk (one file).
- `walk/media/`: the 360 photos (`stopN-name-day|night.jpg`, plus `-small.jpg` previews), walking clips (`clipN-...-day|night.mp4`) and the night party loop.
- `tools/make_placeholders.py`: draws the fake Pappi and saves it like a 360 camera would.
- `tools/make_asset_list.py`: builds the "what we need from the team" list.
- `docs/`: that list as a PDF and as a checklist.
- `CLAUDE.md`: the project brief every Claude Code session reads first.

## Swapping in real footage
Export from the 360 camera as a normal 360 (2:1) file, then:
- Photos: 4096 x 2048 JPG, plus a 1024 x 512 `-small.jpg`.
- Clips: 2048 x 1024 MP4 (H.264), about 3 to 5 seconds, starting exactly at one stop and ending at the next.
