# pappichulo-website
The website for Pappi Chulo, a party hostel in Vagator, North Goa.

## Test version (live)
Open on your phone: https://t0rr0s.github.io/pappichulo-website/

The page shows what Pappi is like through its guests: short videos of them talking, their own words, a day at Pappi, the family, the three eras, and a Book button.

Every video, photo, quote and name is a **sample** until the real ones arrive. The page says so at the top. The list of what the team needs to collect is in `docs/assets-needed.md` (also as a PDF).

## What's where
- `index.html`: the home page (one file).
- `media/`: the sample videos and photos for the home page. Real files replace them with the same names.
- `tools/make_home_placeholders.py`: makes the sample videos and photos.
- `tools/make_asset_list.py`: builds the "what we need from the team" list (`docs/`).
- `walk/`: the 360 walk, parked until after launch. Open `walk/` to try it.
- `tools/make_walk_placeholders.py`: makes the fake 360 scenes for the walk.
- `CLAUDE.md`: the project brief every Claude Code session reads first.

## Swapping in real files for the home page
Keep the file names. Sizes that work well on phones:
- Hero video: `hero-phone.mp4` 720 x 1280 (tall) and `hero-laptop.mp4` 1280 x 720 (wide), 8 to 15 seconds, H.264, no sound needed. Plus a `.jpg` still of each with the same name.
- Guest videos: `story-1.mp4` to `story-6.mp4`, 540 x 960 (tall), 20 to 40 seconds, H.264 with sound. Plus a `.jpg` still of each.
- Photos: `day-1.jpg` to `day-6.jpg` 1200 x 800, `era-1.jpg` to `era-3.jpg` 900 x 675, `family-1.jpg` to `family-6.jpg` 480 x 480 square.
- Sharing picture: `og.jpg` 1200 x 630.

The quotes and names live in `index.html`. Search for "Sample" to find every spot to fill in.

## The 360 walk (later)
- Swipe up to walk forward. Swipe down to go back. Drag sideways to look around.
- Day / Night switch at the top. After 7 pm Goa time it opens on Night by itself.
- Add `?lite` to the link to test the simple version (no walking clips).
- Real 360 footage: photos 4096 x 2048 JPG plus a 1024 x 512 `-small.jpg`; clips 2048 x 1024 MP4, 3 to 5 seconds, from one stop to the next.
