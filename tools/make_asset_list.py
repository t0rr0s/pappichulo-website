#!/usr/bin/env python3
"""Builds the "what we need from the Pappi team" list as a PDF and a Markdown file."""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = "/usr/share/fonts/truetype/google-fonts/"
pdfmetrics.registerFont(TTFont("Pop", GF + "Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("PopB", GF + "Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("PopBI", GF + "Poppins-BoldItalic.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Pop", normal="Pop", bold="PopB", italic="Pop", boldItalic="PopBI")

TITLE = "Pappi website: what we need from the team"
INTRO = [
    "We are building the new Pappi Chulo website. The front page is a 360 walk: you swipe up and walk "
    "through Pappi, from the gate to the bar to the dance floor. You can switch between Day Pappi and Night Pappi.",
    "Right now the walk uses fake pictures. Everything below replaces them with the real Pappi.",
]
HOW = [
    "Put everything in one shared Google Drive folder called <b>Pappi Website</b>, with one folder per section below.",
    "Always send the <b>original files</b>. WhatsApp makes photos and videos small and blurry, so don't send them there.",
    "360 camera files: export them as normal 360 files (on Insta360 the export is called \"360 video\" or \"360 photo\"). Don't reframe them into flat videos.",
]
ORDER = [
    ("1", "Today", "Cloudbeds booking link, and who owns the domain name (section E)."),
    ("2", "This week", "Night 360 shots and night walks (section A). Parties are on now."),
    ("3", "This week", "Day 360 shots and day walks (section A)."),
    ("4", "Start now", "Old photos from all 11 years (section C). This takes time to collect."),
    ("5", "Next week", "Logo and brand files (section D), normal photos (section B)."),
    ("6", "After the rebuild", "The new rooms. Don't shoot the old dorms."),
]
SECTIONS = [
    ("A. 360 shots for the walk", "This is the most important part.", [
        ("Rules for every 360 shot", [
            "Camera on a stick held above your head, or on a light stand at eye height (about 1.6 m).",
            "Turn on the setting that keeps \"forward\" pointing forward (Insta360: Direction Lock or FlowState).",
            "Use the top quality setting (5.7K or 8K if the camera has it).",
            "Stick tape on the floor at every stop. Shoot day and night from the exact same tape mark, same height.",
            "Keep people at least 1.5 m from the camera. Close faces look strange in 360.",
            "Tidy up before day shots (laundry, empty bottles, bins).",
            "Put a small sign up on shoot nights: \"We're filming for our website tonight.\"",
        ]),
        ("The stops (start with these 4, add any spot people love)", [
            "The gate, standing outside and looking in.",
            "The bar under the mango tree.",
            "The graffiti wall or the chill area.",
            "The dance floor, a few steps in front of the DJ.",
        ]),
        ("For every stop", [
            "<b>Day 360 photo.</b> Late afternoon, about 4 to 5 pm, when the light is soft.",
            "<b>Night 360 photo.</b> On a busy night, about 11 pm to 1 am.",
            "<b>Night 360 video, 30 seconds,</b> camera standing still on its stand. We cut a short loop from it.",
        ]),
        ("The walks between stops", [
            "Start recording on the tape mark. Wait 3 seconds. Walk slowly at the same speed to the next tape mark. "
            "Stop on the mark. Wait 3 seconds. Stop recording.",
            "Do every walk 3 times, so we can pick the smoothest one.",
            "Do every walk in the day and again on a busy night.",
        ]),
        ("Party moments (360 video, camera standing still)", [
            "Middle of the dance floor at the busiest moment, 30 to 60 seconds.",
            "Camera on a bar stool. People come up and say hi, about 60 seconds.",
            "The group leaving Pappi for Hilltop (and arriving, if you can).",
            "Sunset to night from one spot, using the camera's time-lapse mode, 1 to 2 hours.",
            "Meet the family: each staff member and each dog, one by one, waving at the camera.",
        ]),
        ("Night tip", [
            "360 cameras get grainy in the dark. On shoot night, add some extra light around the camera spot, "
            "and don't point the camera straight into lasers or strobes.",
        ]),
    ]),
    ("B. Normal photos and videos", "A good phone is fine. Use the back camera.", [
        ("", [
            "Your 20 best party photos from this season.",
            "Every painting and graffiti wall: one straight-on photo each, plus who painted it and when (rough year is fine).",
            "The dogs: a photo of each, and their names.",
            "Staff: a photo, first name and job for each person who wants to be on the site.",
            "Food and drinks: your 5 best dishes and 5 best drinks.",
            "Short vertical party clips (9:16), 5 to 15 seconds each.",
            "The rooms: only after the rebuild is finished.",
        ]),
    ]),
    ("C. The three eras (the nostalgia page)", "Old guests will love this. Start asking now.", [
        ("", [
            "Old photos and videos from all 11 years. Look in old phones, old Instagram and Facebook posts, "
            "old staff, the owners' laptops and Google Photos.",
            "For each one: the rough year, and who is in it if you know.",
            "Old logos, flyers, posters, menus and T-shirts.",
            "In a few lines: what were the three eras? What changed each time, and what do you call each era?",
            "Names or Instagram handles of old regulars who might send their own photos.",
            "Only send photos where the people would be happy to be shown. The site will have a \"remove my photo\" button.",
        ]),
    ]),
    ("D. Logo and brand", "", [
        ("", [
            "The logo in the best quality you have. Best: the original design file (AI, SVG or PDF). "
            "Next best: a big PNG with a see-through background.",
            "Any brand colours or fonts, if someone made a brand guide.",
            "A sharp photo of the gate sign at night.",
        ]),
    ]),
    ("E. Info and links", "Text is fine. WhatsApp is OK for this part.", [
        ("", [
            "<b>The direct booking link from Cloudbeds.</b> This is the most important link on the whole site.",
            "<b>The domain:</b> do we own a Pappi website address (like pappichulo.com)? Who has the login?",
            "Room types and prices (after the rebuild): dorms, girls' dorm, quiet dorm, private rooms.",
            "What happens each night of the week: DJ nights, game nights, Hilltop nights.",
            "House rules (we will rewrite them in a fun way).",
            "Check-in and check-out times, Google Maps link, WhatsApp number, Instagram handle, email.",
            "A DJ mix we are allowed to play online (for the music button). Ask the DJ for written OK.",
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
