# Making the Pappi site a piece of art (research, 20 Nov 2026)

Asked by Roro: the site should feel like a piece of art, the way the walls at Pappi are art. Study the best hospitality sites that are art, and say what to change.

How sure: the list of sites and what reviewers say about them is from published reviews and the Awwwards pages (likely). I could not open the sites themselves in this session, so I have not checked each effect with my own eyes.

## What the best ones do

| Site | What it is known for | What we take |
| --- | --- | --- |
| Michelberger Hotel, Berlin (Awwwards Honorable Mention, 2019) | Whole sections are flat colour blocks with giant letters. Feels rebellious, like the hotel | Full screen colour walls with huge words. Few words per screen |
| The Drake Hotel, Toronto (Awwwards Site of the Day, 2 Sep 2025, by Locomotive) | A hotel that is also an art gallery and music venue. An earlier version of its site was built from textures, patterns, handwriting and "a little bit of chaos" | Treat the walls as an art collection. Let some mess in |
| Paris by Emily (Awwwards Site of the Day, 26 Dec 2025, by LOOP) | Playful toys on the page, like objects that fall and bounce | One toy the visitor can play with |
| Mama Shelter | Moving video at the top, loud type | Video first, words on top |
| The Hoxton | Shows one clear kind of guest through photos and words. Never says "stylish" | Show the Pappi guest. Never describe the vibe in adjectives |
| Ace Hotel, 25hours | What is happening (events, artists) is as big as the rooms. Photos look like real life, not adverts | "Tonight" is as big as "Beds". Phone photos are fine |

## The one idea
**The page is a wall that gets painted while you scroll.**

It starts almost bare: cream wall, one line, the Book button. As you scroll, the real graffiti characters get sprayed in, photos get pasted on like posters, guests' words get written on. At the bottom the wall is full, like the real walls after eleven years.

Nobody else can copy this, because nobody else has these walls.

## What to change (most important first)

1. **Spray the art in.** Each character should appear the way paint goes on a wall: a rough spray edge wiping across it, with a few drips after. Not a pop or a fade. This is the signature move.
2. **Night is blacklight.** After 7 pm Goa time the wall goes dark and the art glows like under UV light. Day and night also swap the photos and clips (see `media/dream-site/day-night.json`).
3. **Photos are pasted, not placed.** Slightly crooked, tape on the corners, a torn edge, overlapping the art. Not tidy cards in a row.
4. **Video inside the art.** Play a clip inside a shape from the wall: inside the gorilla's visor, or inside the letters PAPPI. One or two times only.
5. **Giant words.** One or two screens that are only a colour and a few huge words, like a painted wall.
6. **One toy.** Let the visitor spray their own tag on a wall near the bottom (finger on phone, mouse on laptop). It fades after a while. Small, fast, optional.
7. **The walls as a gallery.** A short section that names each big mural, who painted it and when. The artists get credit, and the hostel reads as a place where art happens.
8. **Tonight is as big as Beds.** What is on this week sits high on the page, with a clip.
9. **Sound, on a tap.** One button: "Hear Pappi". Real bar sound or the guitar clip. Off by default.
10. **Keep it honest.** Real photos, real words, phone quality is fine. That is the Ace and Hoxton lesson.

## What not to do
- Do not add 3D, heavy effects or long loading screens. Most visitors are on a phone on mobile data.
- Do not let art hide the Book button. It stays in reach on every screen.
- Do not add more fonts or more colours. The walls bring the colour.
- Do not animate everything. Three strong moments (spray, blacklight, video in the art) beat thirty small ones.

## Speed limits that protect the art
- First screen shows in under 2 seconds on 4G: one still picture, text, button. No video in the first load.
- At most 6 video clips, loaded only when seen (see `video-picks.md`).
- If the phone asks for less motion, show the finished wall with nothing moving.

## What this needs from the team
- A straight-on daylight photo of every mural, plus the artist's name and year.
- The week's real events.
- 30 seconds of clean sound from the bar on a busy night.
- Guest videos, talking to the camera. There are none in the Drive.

## Sources
- Michelberger: https://www.awwwards.com/sites/michelberger-hotel and https://www.justinmind.com/web-design/hotel-website
- The Drake Hotel: https://www.awwwards.com/sites/the-drake-hotel , https://locomotive.ca/en/work , http://www.kamnong.com/drakehotel
- Paris by Emily: https://www.awwwards.com/sites/paris-by-emily and https://www.osmo.supply/showcase/paris-by-emily
- Hoxton, Ace, 25hours: https://www.krishaweb.com/blog/best-hotel-website-designs/
- Mama Shelter: https://websitevice.com/hotel-examples-3
- Video loading: https://web.dev/articles/lazy-loading-video
