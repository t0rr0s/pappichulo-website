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
- `index.html` is this page. Sample media comes from `tools/make_home_placeholders.py` and lives in `media/`. Real files replace them with the same names. The brand book (Oct 2026) gives the one line, the promises, the voice rules, the room names and the colours; the page follows it.
- The list of what the team must collect is `docs/assets-needed.md` (and the PDF), built by `tools/make_asset_list.py`.

## Look and feel: the living wall (decided Oct 2026, after the neon, serif boutique, sticker and street poster versions were all rejected)
- The walls are the brand. The site is one long cream wall of Pappi. The real graffiti characters host each section: gorilla astronaut (hero, the face of the house), wolf and horse (the night promise), split face (the worries), pink pig (the review wall), croc (Tonight, the bar), tiger (the day loop), masked woman (the eras), blue cat "HEY" (the basics and booking), the "PAPPI" letters (footer).
- The art lives in `media/art/` as WebP cut-outs with transparent backgrounds, two sizes each (`name.webp` laptop, `name-phone.webp` phone). Made from the artist's 2000px renders by keying out the white. Replace with higher quality files under the same names when they arrive. The artist gave his blessing; his name and credit line still need to go in the footer.
- Everything that is a "thing" on the page (card, button, quote, photo) is a glossy sticker like the art: `.stk` in `index.html`. Thick black outline (3px), round corners, a hard dark edge underneath, one white shine, a tiny tilt. Coloured bands have a black top and bottom line and drip into the next section (`svg.drip`, drawn by script).
- Colours are the brand book's, matched to the walls: cream `#faf7f0`, ink `#111111`, pink `#ff4f9a` (main, buttons), blue `#2fb4f0`, green `#8fd14f`, orange `#ff8a1f`, purple `#8b5cf6`, yellow `#ffd23f`. Page chrome is cream, ink and pink. The other colours come from the art and the stickers.
- Type: Dela Gothic One for headlines (uppercase), Londrina Solid for everything else. Both in `fonts/`. No puffy lettering made by code: Vru parked that (the tool `tools/make_lettering.py` stays, unused).
- Motion (GSAP + ScrollTrigger, in `vendor/`, Lenis for wheel smoothing): stickers and characters pop in like they were slapped on (back.out), the gorilla floats, splashes drift slower than the page, drips grow down, the croc smokes, buttons are jelly, characters lean toward the mouse on laptops. The review wall is a held scroll scene (quotes slap on one by one). Reduced motion gets the finished page with nothing moving.
- Sample media in `media/` follows the same palette (`tools/make_home_placeholders.py`).

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
