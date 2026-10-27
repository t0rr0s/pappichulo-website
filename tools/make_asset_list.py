#!/usr/bin/env python3
"""Builds the "what we need from the Pappi team" list as a PDF and a Markdown file.

Run:  python3 tools/make_asset_list.py
Needs: reportlab, the Poppins font (set FONT_DIR if it is not in the folder below).
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = os.environ.get("FONT_DIR", "/usr/share/fonts/truetype/google-fonts")
pdfmetrics.registerFont(TTFont("Pop", os.path.join(GF, "Poppins-Regular.ttf")))
pdfmetrics.registerFont(TTFont("PopB", os.path.join(GF, "Poppins-Bold.ttf")))
pdfmetrics.registerFont(TTFont("PopBI", os.path.join(GF, "Poppins-BoldItalic.ttf")))
registerFontFamily("Pop", normal="Pop", bold="PopB", italic="Pop", boldItalic="PopBI")

TITLE = "Pappi website: what we need from the team"
INTRO = [
    "We are building the new Pappi Chulo website. The front page shows what Pappi is really like, through the "
    "guests: short videos of them talking, their own words, and photos and clips of the good moments. "
    "It ends with a button to book direct with Pappi.",
    "Right now the page uses fake sample videos and quotes. Everything below replaces them with the real thing. "
    "The site will only be as good as what we collect, so this list matters more than the code.",
]
HOW = [
    "Put everything in one shared Google Drive folder called <b>Pappi Website</b>, with one folder per section below.",
    "Always send the <b>original files</b>. WhatsApp makes photos and videos small and blurry, so don't send them there.",
    "For every guest in a video or photo: get a clear yes for the website. Write down their first name and country.",
]
ORDER = [
    ("1", "Today", "Cloudbeds booking link, and who owns the domain name (section F)."),
    ("2", "This week", "Guest videos (section A). Guests are here now, and every guest who leaves is a video we missed."),
    ("3", "This week", "Straight-on photos of every graffiti wall and the gate sign (section B). The look of the whole site is built from them. Then party and friends clips and photos."),
    ("4", "Start now", "Written words from guests (section C) and old photos from all 11 years (section D)."),
    ("5", "Next week", "Staff and dogs (section B), logo and brand files (section E)."),
    ("6", "After launch", "360 shots for the walk (section G). Not now."),
]
SECTIONS = [
    ("A. Guest videos", "The most important part. Real guests, talking about Pappi in their own words.", [
        ("How to film", [
            "Any good phone. Back camera. Hold the phone <b>upright</b> (tall video, like Instagram stories).",
            "Good light: daylight, or under the bar lights. Not in the dark, and not with the sun behind them.",
            "Quiet spot: away from the speakers. We need to hear every word.",
            "Hold the phone still, or lean it on something. Face about 1 m away.",
            "20 to 40 seconds each. One guest at a time, or two friends together.",
            "Don't give them lines. Let them talk. Laughing, stumbling and swearing are all fine.",
        ]),
        ("Ask these three questions", [
            "Why did you come to Pappi?",
            "What happened here that you'll never forget?",
            "Pappi in three words?",
        ]),
        ("How many, and who", [
            "Aim for <b>30 guests this month.</b> Mix it up: different countries, ages, solo travellers and groups, first timers and people who came back.",
            "Catch them in a good mood: at the bar before the night, on the beach, the morning after.",
            "At the start of each video ask: \"Are you happy to be on the Pappi website?\" Keep their yes in the video.",
            "Write down each guest's first name and country in a note next to the file.",
        ]),
    ]),
    ("B. Party and friends: clips and photos", "A good phone is fine. Use the back camera.", [
        ("Clips (tall, 9:16, 5 to 15 seconds each)", [
            "30 clips of the good moments: the dance floor, the bar at sunset, games, the beach crew, the walk to Hilltop, sunrise.",
            "One 10 to 15 second clip of a full dance floor on a big night. This goes at the top of the page.",
            "Film with sound. We'll pick what plays.",
        ]),
        ("Photos", [
            "Your 30 best photos from this season: people laughing, groups, the bar at sunset, the gate at night.",
            "A real day at Pappi: one photo each for the slow morning, the beach, sunset at the bar, the night starting, late night, sunrise.",
            "<b>Every painting and graffiti wall: one straight-on photo each in daylight,</b> plus who painted it and when (rough year is fine). The site's stickers and symbols are drawn from these, so this comes first.",
            "Food and drinks: your 5 best dishes and 5 best drinks.",
            "The rooms: only after the rebuild is finished.",
        ]),
        ("The family", [
            "Staff: a photo, first name and job for each person who wants to be on the site.",
            "The dogs: a photo of each, their names, and one line about them (\"head of security\").",
        ]),
    ]),
    ("C. Written words from guests", "Their own words, not ours. Text or screenshots are fine.", [
        ("", [
            "The 20 best real reviews from Google, Hostelworld and Booking. Screenshot them, or copy the text with the name and date.",
            "Messages from old guests (WhatsApp, Instagram) saying what Pappi meant to them. Ask them if we can use it.",
            "Ask 10 old regulars for three lines each: why they came, why they came back.",
            "Photos of the guest book pages, if there is one.",
        ]),
    ]),
    ("D. The three eras (were you here?)", "Old guests will love this. Start asking now, it takes time.", [
        ("", [
            "Old photos and videos from all 11 years. Look in old phones, old Instagram and Facebook posts, "
            "old staff, the owners' laptops and Google Photos.",
            "For each one: the rough year, and who is in it if you know.",
            "Old logos, flyers, posters, menus and T-shirts.",
            "In a few lines: what were the three eras? Rough years, what changed each time, and what do you call each era?",
            "Names or Instagram handles of old regulars who might send their own photos.",
            "Only send photos where the people would be happy to be shown. The site will have a \"remove my photo\" button.",
        ]),
    ]),
    ("E. Logo and brand", "", [
        ("", [
            "The logo in the best quality you have. Best: the original design file (AI, SVG or PDF). "
            "Next best: a big PNG with a see-through background.",
            "Any brand colours or fonts, if someone made a brand guide.",
            "A sharp photo of the gate sign at night.",
        ]),
    ]),
    ("F. Info and links", "Text is fine. WhatsApp is OK for this part.", [
        ("", [
            "<b>The direct booking link from Cloudbeds.</b> This is the most important link on the whole site.",
            "<b>The domain:</b> do we own a Pappi website address (like pappichulo.com)? Who has the login?",
            "Room types and prices (after the rebuild): dorms, girls' dorm, quiet dorm, private rooms.",
            "What happens each night of the week: DJ nights, game nights, Hilltop nights.",
            "House rules (we will rewrite them in a fun way).",
            "Check-in and check-out times, Google Maps link, WhatsApp number, Instagram handle, email.",
            "Where should old photos be sent? A WhatsApp number or an email we can put on the site.",
        ]),
    ]),
    ("G. Later: 360 shots for the walk", "Not for launch. Keep this for after the site is live.", [
        ("", [
            "The plan is a 360 walk from the gate to the bar to the dance floor, with a Day and Night switch.",
            "When we get there: 360 photos at each stop, day and night from the same tape mark, plus short walking clips between stops.",
            "The full shot list is ready. Ask Vru when it's time.",
        ]),
    ]),
]


def md():
    out = [f"# {TITLE}", ""] + [p.replace("<b>", "**").replace("</b>", "**") for p in INTRO] + ["", "## How to send"]
    out += [f"- {h.replace('<b>', '**').replace('</b>', '**')}" for h in HOW]
    out += ["", "## What first"] + [f"{n}. **{w}:** {t}" for n, w, t in ORDER]
    for title, sub, groups in SECTIONS:
        out += ["", f"## {title}"]
        if sub:
            out.append(sub)
        for gt, items in groups:
            if gt:
                out += ["", f"**{gt}**"]
            out += [f"- [ ] {i.replace('<b>', '**').replace('</b>', '**')}" for i in items]
    return "\n".join(out) + "\n"


def pdf(path):
    ink = colors.HexColor("#180F22")
    pink = colors.HexColor("#E8288F")
    soft = colors.HexColor("#5B5266")
    st = {
        "brand": ParagraphStyle("brand", fontName="PopBI", fontSize=11, textColor=pink, leading=14),
        "h1": ParagraphStyle("h1", fontName="PopB", fontSize=21, leading=26, textColor=ink, spaceAfter=6),
        "body": ParagraphStyle("body", fontName="Pop", fontSize=10.5, leading=15.5, textColor=ink, spaceAfter=5),
        "h2": ParagraphStyle("h2", fontName="PopB", fontSize=14.5, leading=19, textColor=ink, spaceBefore=12, spaceAfter=2),
        "sub": ParagraphStyle("sub", fontName="Pop", fontSize=10, leading=14, textColor=soft, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="PopB", fontSize=10.5, leading=15, textColor=pink, spaceBefore=6, spaceAfter=2),
        "item": ParagraphStyle("item", fontName="Pop", fontSize=10.5, leading=15, textColor=ink),
        "cell": ParagraphStyle("cell", fontName="Pop", fontSize=10, leading=14, textColor=ink),
        "cellb": ParagraphStyle("cellb", fontName="PopB", fontSize=10, leading=14, textColor=ink),
    }
    story = [Paragraph("PAPPI CHULO", st["brand"]), Paragraph(TITLE, st["h1"])]
    story += [Paragraph(p, st["body"]) for p in INTRO]
    story.append(Paragraph("How to send", st["h2"]))
    story += [checkrow(h, st, box=False) for h in HOW]
    story.append(Paragraph("What first", st["h2"]))
    rows = [[Paragraph(n, st["cellb"]), Paragraph(w, st["cellb"]), Paragraph(t, st["cell"])] for n, w, t in ORDER]
    tbl = Table(rows, colWidths=[8 * mm, 32 * mm, None])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#E2DCE8")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(tbl)
    for title, sub, groups in SECTIONS:
        head = [Paragraph(title, st["h2"])]
        if sub:
            head.append(Paragraph(sub, st["sub"]))
        first = True
        for gt, items in groups:
            block = []
            if gt:
                block.append(Paragraph(gt, st["h3"]))
            block += [checkrow(i, st) for i in items]
            story.append(KeepTogether((head if first else []) + block))
            first = False
    story += [Spacer(1, 10), Paragraph("Questions? Ask Vru.", st["sub"])]

    def footer(c, d):
        c.saveState()
        c.setFont("Pop", 8)
        c.setFillColor(soft)
        c.drawString(18 * mm, 10 * mm, "Pappi Chulo website, assets list")
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}")
        c.restoreState()

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm, title=TITLE, author="Pappi Chulo")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def checkrow(text, st, box=True):
    mark = Paragraph("☐" if box else "•", ParagraphStyle("m", fontName="DejaVu", fontSize=11, leading=15))
    t = Table([[mark, Paragraph(text, st["item"])]], colWidths=[6 * mm, None])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
    return t


if __name__ == "__main__":
    pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "assets-needed.md"), "w") as f:
        f.write(md())
    pdf(os.path.join(ROOT, "docs", "Pappi-website-assets-needed.pdf"))
    print("ok")
