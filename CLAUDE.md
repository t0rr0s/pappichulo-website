# Pappi Chulo website

The website for Pappi Chulo, a party hostel on Ozran Beach Road (next to 9 Bar), Vagator, North Goa. Running for 11 years. Guests say it has had three "eras". Owner of this repo and the person you talk to: Vru (GitHub t0rr0s).

## What the site must do
1. Make a stranger feel a Pappi night before they arrive.
2. Get them to book direct on Pappi's own Cloudbeds booking page (saves the Hostelworld fee).
3. Pull back old guests from all three eras.

## The launch idea: real people, real words (decided Oct 2026)
- The homepage shows what Pappi gives its guests: the party, the friends, the plans that make themselves, the memories. Mostly through real guests: short videos of them talking, their own words, and photos and clips of people having a good time.
- What Pappi solves: travelling alone, not knowing where the party is, not wanting to plan every day, wanting a place that feels like home.
- Everything on the page must be real. Until the real videos and quotes arrive, placeholders are clearly marked "Sample" and the page carries a "Test version" banner. Never present a made-up quote as real.
- Everyone shown must have said yes. Keep the "remove my photo" option.
- `index.html` is this page. Sample media comes from `tools/make_home_placeholders.py` and lives in `media/`. Real files replace them with the same names.
- The list of what the team must collect is `docs/assets-needed.md` (and the PDF), built by `tools/make_asset_list.py`.

## Look and feel: the graffiti wall (decided Oct 2026, after Vru rejected a neon version and a serif boutique version)
- Fun but classy, the way award-winning hostel and hotel sites do it (The Hoxton, citizenM, Mama Shelter, The Social Hub): a calm paper frame, chunky black type, ONE bright colour, and the fun living in the content: stickers, symbols, a ticker, cheeky copy, a Book button with a hard shadow that wobbles. Not neon, not glow, not a serif boutique look.
- Colours (CSS variables in `index.html`): paper `#fffaf2`, sand `#f3ebdc`, ink `#141210`, coral `#ff5a3c` (the one bright colour: buttons, numbers, worry quotes), mango `#ffc53d` and mint `#8fe3c0` (stickers and one section block each). Dark sections use ink, not black.
- Type: Dela Gothic One for the big headlines (uppercase), Londrina Solid 900 for the hand-lettered bits (the name, stickers, quotes, labels, section numbers), Bricolage Grotesque for body text. All three saved in `fonts/` (woff2), loaded by `fonts/fonts.css`, not from Google's servers.
- The Pappi symbols: a small family of simple shapes (sun, moon, mango, disco ball, speaker, dog, cat, eye for Hilltop, bottle, sunrise, three-era wheel, home) drawn as SVG symbols at the top of `index.html`. Thick line, flat fills. Used as section marks, card corners, ticker, footer, favicon. To be redrawn in the style of the real graffiti once Vru sends wall photos.
- Cards and photos: 2px ink border, 18px radius, a 4px hard shadow, a tiny tilt. Hard shadows, never soft blur.
- The real graffiti on Pappi's walls is the illustration layer of the site (like The Hoxton's local artists). Once photos arrive, cut-outs of the real art replace or join the symbols.
- The sample media in `media/` follows the same palette. If the palette changes, change `tools/make_home_placeholders.py` too and re-run it.

## Later: the 360 walk (Day Pappi, Night Pappi)
Parked until after launch. It lives in `walk/` and still works. Keep it, don't delete it.
- A 360 walk through the party and common areas (gate, bar under the mango tree, graffiti wall, dance floor). Never empty dorm tours.
- A Day / Night switch. Every stop has a day 360 shot and a night 360 shot from the exact same spot.
- After 7 pm Goa time (Asia/Kolkata) the walk flips to Night by itself.
- Placeholder 360 scenes come from `tools/make_walk_placeholders.py`.

## Real layout (from Vru)
- Walking in from the main gate, the bar is on the LEFT.
- Placeholder scenes must match the real layout. In `tools/make_walk_placeholders.py` the walk goes along +z, and +x is on your left.

## How the walk works (keep this for later)
- Stops = sharp 360 photos the visitor can look around in.
- Moving between stops = short 360 video clips (3 to 5 seconds) that play when the visitor swipes up.
- Party spots can use a short looping 360 video instead of a photo.
- Swipe up = walk forward. Swipe down = go back (quick fade, never play video backwards).
- Drag sideways = look around. Up/down belongs to the page, sideways belongs to the 360.
- "Move your phone to look around" button (iPhone needs a tap to ask for motion permission).
- Ends at a Book button that goes to the Cloudbeds booking page.

## Smoothness rules
- Mobile first. Most visitors are on phones. Test on a cheap Android on 4G, not only an iPhone on wifi.
- Show a still picture instantly, load the 360 behind it.
- Load only the next stop ahead, never the whole walk.
- Two sizes of every file: phone and laptop. Load a small preview first, then the sharp version.
- Pause anything off screen. Sound off until the visitor taps it.
- Fallback for weak phones, slow internet or "reduce motion": normal swipeable photos and video.
- Big media files will live on a fast file host (planned: Cloudflare R2), not in this repo, once real footage exists.

## Tech
- Plain static site, no build step: `index.html` (home page) + `media/` (its sample videos and photos) + `walk/` (the parked 360 walk, Three.js from jsDelivr, pinned version).
- Sample media is generated by Python tools in `tools/` (numpy, Pillow, ffmpeg, Poppins font). Real footage replaces it later with the same file names.
- Hosting for testing: GitHub Pages. Later: Cloudflare Pages + custom domain.

## How to talk to Vru
- Plain language, like explaining to a five year old. Short sentences, common words, no jargon.
- Never use em dashes or long dashes anywhere (copy, code comments shown to users, docs, replies).
- Be decisive. Lead with the hard truth first. Say how sure you are (sure / likely / guessing).
- Give complete answers the first time. Double check work before saying it's done.
- Test every link before it goes out.
