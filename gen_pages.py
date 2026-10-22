#!/usr/bin/env python3
"""Regenerate ToolNova tool pages: preserves each page's toolbox + scripts,
rebuilds head/header/footer/content with expanded human-written copy."""
import re, json, os, html as ihtml

BASE = os.path.dirname(os.path.abspath(__file__))
BASEURL = "https://trytoolnova.com/"

GA_HEAD = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZFCP6M1MEB"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-ZFCP6M1MEB');
</script>"""

def extract(path):
    s = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", s, re.S).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)"', s, re.S).group(1)
    canon = re.search(r'<link rel="canonical" href="(.*?)"', s).group(1)
    head = re.search(r"<head>(.*?)</head>", s, re.S).group(1)
    head_srcs = re.findall(r'<script src="[^"]+"></script>', head)
    # toolbox: balanced div scan
    i = s.index('<div class="toolbox">')
    j = i; depth = 0
    for m in re.finditer(r"<div|</div>", s[i:]):
        if m.group(0) == "<div": depth += 1
        else:
            depth -= 1
            if depth == 0:
                j = i + m.end(); break
    toolbox = s[i:j]
    # body scripts after footer
    tail = s[s.index("</footer>"):]
    scripts = re.findall(r"<script>.*?</script>", tail, re.S)
    return dict(title=title, desc=desc, canon=canon, head_srcs=head_srcs,
                toolbox=toolbox, scripts="\n".join(scripts))

def strip_tags(t):
    return ihtml.unescape(re.sub(r"<[^>]+>", "", t)).strip()

HEADER = """<header class="site"><div class="wrap">
  <a class="logo" href="../">⚡ Tool<span>Nova</span></a>
  <nav class="main"><a href="../">Home</a><a href="../guides/">Guides</a><a href="../about/">About</a><a href="../contact/">Contact</a><a href="../privacy-policy/">Privacy Policy</a></nav>
</div></header>"""

FOOTER = """<footer class="site"><div class="wrap">
  <div class="cols">
    <div><h4>⚡ ToolNova</h4><p style="color:var(--muted);font-size:.92rem;max-width:260px">Free online tools for everyday tasks. Fast, private and no sign-up required.</p></div>
    <div><h4>Popular Tools</h4><a href="../word-counter/">Word Counter</a><a href="../password-generator/">Password Generator</a><a href="../qr-code-generator/">QR Code Generator</a><a href="../bmi-calculator/">BMI Calculator</a><a href="../emi-calculator/">EMI Calculator</a></div>
    <div><h4>Guides</h4><a href="../guides/strong-password-you-can-remember/">Strong Passwords You Can Remember</a><a href="../guides/bmi-explained/">BMI Explained</a><a href="../guides/compress-images-without-losing-quality/">Compress Images Without Losing Quality</a></div>
    <div><h4>Site</h4><a href="../about/">About Us</a><a href="../contact/">Contact</a><a href="../privacy-policy/">Privacy Policy</a><a href="../terms/">Terms of Service</a><a href="../disclaimer/">Disclaimer</a></div>
  </div>
  <p class="copy">© 2026 ToolNova. All rights reserved.</p>
</div></footer>"""

def build_page(slug, data, ex):
    faqs = data["faqs"]
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q,
                          "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}
    faq_html = "\n    ".join(
        f'<div class="faq"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs)
    related = "".join(f'<a href="../{s}/">{label}</a>' for s, label in data["related"])
    if data.get("guide"):
        gslug, gtitle = data["guide"]
        related += f'<a href="../guides/{gslug}/">📖 Guide: {gtitle}</a>'
    sections = "\n    ".join(
        f"<h2>{h}</h2>\n    {body}" for h, body in data["sections"])
    head_srcs = "\n".join(ex["head_srcs"])
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_HEAD}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ex['title']}</title>
<meta name="description" content="{ex['desc']}">
<link rel="canonical" href="{ex['canon']}">
<link rel="stylesheet" href="../style.css">
{head_srcs}
<script type="application/ld+json">
{json.dumps(ld, indent=0)}
</script>
</head>
<body>
{HEADER}

<div class="wrap">
  <p class="crumb"><a href="../">Home</a> › {data['name']}</p>
  <div class="pagehead">
    <h1>{data['h1']}</h1>
    <p class="lead">{data['lead']}</p>
  </div>

  {ex['toolbox']}

  <section class="block">
    {sections}
  </section>

  <section class="block">
    <h2>Frequently Asked Questions</h2>
    {faq_html}
    <h2>Related Tools</h2>
    <div class="related">{related}</div>
  </section>
</div>

{FOOTER}

{ex['scripts']}
</body>
</html>
"""
    words = len(strip_tags(data["lead"] + " " + " ".join(b for _, b in data["sections"]) + " " + " ".join(q + a for q, a in faqs)).split())
    out = os.path.join(BASE, slug, "index.html")
    open(out, "w", encoding="utf-8").write(page)
    print(f"{slug}: content words ≈ {words}")

TOOLS = {}

TOOLS["word-counter"] = {
"name": "Word Counter", "h1": "Word Counter",
"lead": "Paste or type any text and watch the numbers update as you go — words, characters, sentences, paragraphs, reading time, speaking time and even your longest word. It's the counter to reach for when an essay has a hard limit, a post is running long, or a speech has to fit inside five minutes.",
"sections": [
("More Than Just a Word Count",
"""<p>A plain word count is only half the story. This counter shows seven live statistics at once: <strong>words, characters, characters without spaces, sentences, paragraphs, estimated reading time, estimated speaking time</strong>, and the longest word in your text. Each one answers a different question. Characters matter when a form, a tweet or a meta description cuts you off at a fixed length. Reading time tells a blogger how long a post will hold a visitor. Speaking time — calculated at a slower 130 words per minute, because talking is slower than reading — is the one presenters and video creators actually need.</p>
<p>Who uses it most? Students working to limits like 500, 1,500 or 3,000 words (and the dreaded "±10%" that lecturers allow). Freelance writers and translators who bill per word and need a number both sides can trust. Job seekers squeezing a cover letter onto one page. Social media managers checking a post before it gets truncated. And speakers of every kind — teachers, students defending a thesis, anyone recording a voiceover — who plan in minutes, not words.</p>"""),
("How to Use the Word Counter",
"""<ol>
<li>Click into the box and start typing, or paste text from Word, Google Docs, an email — anywhere.</li>
<li>Read the statistics under the box. They update instantly with every keystroke; there is no "count" button to press.</li>
<li>Edit directly in the box to trim or expand your text until the numbers match your target.</li>
<li>Use "Clear text" when you're done — everything disappears, because nothing was ever saved.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>Say you've written a scholarship essay and the limit is <strong>1,200 words</strong>. You paste your draft and the counter reports <strong>1,247 words, 7,480 characters, 52 sentences, a 6-minute reading time and a 10-minute speaking time</strong>.</p>
<p>Two useful things jump out. First, you're 47 words over — about four average sentences to cut. Second, 1,247 words across 52 sentences means roughly 24 words per sentence, which reads a little heavy; splitting the longest sentences makes the essay feel lighter without changing its length. Ten minutes later you've trimmed the filler, the counter shows 1,196 words, and you're inside the limit with room to spare.</p></div>"""),
("Tips for Making the Numbers Work for You",
"""<ul>
<li><strong>Plan articles by reading time.</strong> Many readers happily finish a 5–7 minute post but abandon a 20-minute one. Checking reading time before publishing tells you which one you've written.</li>
<li><strong>Check characters before you paste into a form.</strong> Application portals and ad platforms count characters — usually including spaces — and silently cut off anything extra.</li>
<li><strong>Trim by sentences, not by words.</strong> Deleting one weak sentence removes 20 words painlessly. Shaving single words off forty sentences just makes the text choppy.</li>
<li><strong>Recount after every serious edit.</strong> A "small" rewrite routinely adds 10% to a draft. The live counter keeps you honest.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Assuming every tool counts the same way.</strong> This counter treats anything separated by spaces as a word — "well-known" is one word, numbers count as words, and a stray "123" in your references counts too. Word processors sometimes count text boxes, footnotes and endnotes on top of that, which is why totals can differ slightly.</li>
<li><strong>Forgetting that spaces count as characters.</strong> If a limit says 160 characters, spaces are part of it. That's exactly why this counter shows both figures side by side.</li>
<li><strong>Pasting confidential text into tools that upload it.</strong> Some counters send your text to a server. This one counts locally in your browser — but it's a habit worth checking on any site.</li>
</ul>"""),
],
"faqs": [
("How does the counter decide what counts as a word?", "Any run of characters separated by spaces counts as one word — so \"well-known\" is one word, \"2026\" is one word, and so is a stray link. It's the same simple rule most editors and teachers apply, which is why the total matches what people expect."),
("How are reading time and speaking time calculated?", "Reading time assumes an average adult silent reading speed of 200 words per minute. Speaking time uses 130 words per minute — a natural, clear pace for presentations and voiceovers. A 650-word script is therefore about 5 minutes spoken aloud."),
("Is my text uploaded or stored anywhere?", "No. The counting happens in your browser with JavaScript the moment you type. Close the tab and the text is gone — nothing is transmitted to or kept on a server."),
("Why is my count slightly different from Microsoft Word or Google Docs?", "Word processors may also count words in text boxes, headers, footnotes and endnotes, and they treat some hyphenated phrases and symbols differently. Differences of a few words on a long document are normal; for a strict limit, leave yourself a small safety margin."),
("Is there a maximum text length?", "There's no set limit. Book-length texts still count instantly, though on a very old phone a huge paste might take a moment to process."),
("Can I use this for tweets and social media posts?", "Yes — watch the Characters figure. For example, a standard post on X allows 280 characters; the counter updates live so you can trim before you post instead of after."),
],
"related": [("case-converter", "Case Converter"), ("remove-duplicate-lines", "Remove Duplicate Lines"), ("lorem-ipsum-generator", "Lorem Ipsum Generator")],
}

TOOLS["password-generator"] = {
"name": "Password Generator", "h1": "Password Generator",
"lead": "Build strong, genuinely random passwords with the length and character mix you choose — generated on your own device and never sent anywhere. If you still reuse one or two passwords across every account (most people do), this is the five-second fix.",
"sections": [
("Why Random Beats Clever",
"""<p>Humans are terrible at being random. Ask a hundred people to invent a "clever" password and you'll get seasons, football teams, keyboard walks like <em>qwerty123</em>, and a capital letter at the front with a number and an exclamation mark at the end. Attackers know this. Their cracking software tries exactly those patterns first, billions of times per second, using lists of real passwords leaked from previous breaches. Industry breach reports have attributed the majority of hacking-related break-ins to weak, stolen or reused credentials for years — the clever password feels safe and isn't.</p>
<p>A machine-generated password has no pattern to guess. It isn't based on your birthday, your dog, or a word in any dictionary, and the generator here uses your browser's cryptographically secure random generator — the same class of randomness operating systems rely on — rather than simple predictable math. The only thing standing between an attacker and an account protected this way is brute force: trying every possible combination. Make the password long enough and that stops being a realistic threat.</p>"""),
("How to Use the Password Generator",
"""<ol>
<li>Choose a length. Sixteen characters is the default and a solid minimum; use 20 or more for email, banking and anything you'd hate to lose.</li>
<li>Tick the character sets you want: lowercase, uppercase, numbers and symbols. Leave all four on unless a website refuses symbols.</li>
<li>Click "Generate New Password". Don't like it? Generate again — each click is a fresh, independent random result.</li>
<li>Copy the password straight into the sign-up form and into your password manager at the same time. Never leave it only in your clipboard.</li>
</ol>"""),
("A Worked Example: Why Length Wins",
"""<div class="example"><p>Compare two passwords. An 8-character password using only lowercase letters has 26<sup>8</sup> possible combinations — about 200 billion. That sounds like a lot until you learn a modern cracking rig tests around 10 billion guesses per second: it's exhausted in roughly <strong>20 seconds</strong>.</p>
<p>Now take a 16-character password from this generator with all character sets on (about 95 possible characters per position). That's roughly 2<sup>105</sup> combinations — the tool shows this as about 105 bits of strength. At the same 10-billion-guesses-per-second rate, cracking it would take on the order of <strong>100 trillion years</strong>. Doubling the length didn't double the security; it multiplied it by an astronomical factor. That's why every expert gives the same advice: length first, everything else second.</p></div>"""),
("Tips for Passwords That Actually Protect You",
"""<ul>
<li><strong>One password per account, no exceptions.</strong> When one site leaks, only that account is exposed. Reuse is how a forgotten forum account becomes a hacked email account.</li>
<li><strong>Use a password manager.</strong> You were never meant to memorize 60 random passwords. A manager remembers them; you remember one strong master password.</li>
<li><strong>Turn on two-factor authentication (2FA)</strong> for email, banking and social accounts. A stolen password alone then isn't enough to get in.</li>
<li><strong>Change a password when there's a reason</strong> — a breach notice, a shared account, a lost device. Routine forced changes mostly push people back toward predictable patterns.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>"Personalizing" a generated password.</strong> Swapping in your initials or birth year re-introduces the exact patterns attackers try first. Use it exactly as generated.</li>
<li><strong>Saving it in a notes app or a photo.</strong> Plain notes aren't encrypted and sync everywhere. If it isn't in a password manager yet, write it on paper kept somewhere safe — never in a chat message to yourself.</li>
<li><strong>Generating it and losing it.</strong> Save the password into the account and your manager in the same sitting. A brilliant password you can't retrieve is just a locked door.</li>
<li><strong>Using your email password anywhere else.</strong> Your inbox is the master key — password resets for everything else land there. Give it your longest, most unique password of all.</li>
</ul>"""),
],
"faqs": [
("Are these passwords really random?", "Yes. The generator builds each password with your browser's cryptographically secure random number generator (the Web Crypto API), not Math.random. No two clicks produce related results, and nothing is picked from a list."),
("Does ToolNova see or store my password?", "No. Generation happens entirely on your device. The password is never transmitted, logged or stored — close the tab and it exists only where you saved it."),
("What length should I choose?", "Sixteen characters is a good everyday minimum. Use 20–24 for your email, banking and primary accounts. A few older systems cap passwords at 16 or even 12 — in that case use the maximum allowed with all character sets on."),
("Should I include symbols?", "If the site allows them, yes — symbols widen the pool of possible characters and add strength. If a site rejects symbols (some banks do), untick them and add a few extra characters of length to compensate."),
("How often should I change my passwords?", "Current guidance from standards bodies like NIST is: change on evidence of compromise, not on a schedule. A long, unique, random password can safely stay in place for years."),
("Can I use this for my Wi-Fi or router password?", "Absolutely — and you should. Default router passwords are printed in manuals and widely known. A 20-character generated password, stored in your manager, is a far better gatekeeper."),
],
"related": [("qr-code-generator", "QR Code Generator"), ("base64-encoder-decoder", "Base64 Encoder / Decoder"), ("word-counter", "Word Counter")],
"guide": ("strong-password-you-can-remember", "How to Create a Strong Password You'll Actually Remember"),
}

TOOLS["qr-code-generator"] = {
"name": "QR Code Generator", "h1": "QR Code Generator",
"lead": "Turn any link or piece of text into a clean, scannable QR code in seconds — then download it as a PNG for menus, flyers, business cards, packaging and posters. No account, no scan limits, no expiry dates, because the code carries your information itself.",
"sections": [
("What a QR Code Actually Is",
"""<p>A QR code is a two-dimensional barcode: the black-and-white squares encode your text directly into the image. When a phone camera reads the pattern, it recovers exactly what you put in — most often a website address. That design has a consequence people love: a QR code generated here is <strong>static</strong>. It doesn't route through ToolNova or any middleman service, so there is nothing to expire, no subscription keeping it alive, and no limit on how many times it can be scanned. The code you download today will still work in ten years, provided the page it points to is still there.</p>
<p>Who uses it? Restaurants putting digital menus on table tents. Cafés sharing Wi-Fi details without a chalkboard full of typos. Shop owners linking to their Google reviews page — scans climb because customers no longer have to type a long address. Realtors on yard signs, teachers on worksheets, event organizers linking to RSVP forms, market stalls taking payments. Anywhere a long URL, password or set of details would otherwise be read out loud or typed by hand, a QR code earns its square inch.</p>"""),
("How to Use the QR Code Generator",
"""<ol>
<li>Type or paste the URL or text the code should contain. For a website, include the full address starting with https://.</li>
<li>Pick a size. The size controls the downloaded image's resolution — 512 × 512 suits documents and screens; choose 1024 × 1024 for anything you'll print large. On your phone screen the preview always displays at a comfortable fixed size.</li>
<li>Click "Generate QR Code" and test it immediately: point your own phone camera at the screen and confirm it opens the right destination.</li>
<li>Click "Download PNG". The file comes with a clean white border (the "quiet zone") already included, which scanners need to read the code reliably.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>A small bakery wants customers to leave Google reviews. The review link is a 60-character tangle nobody will ever type. The owner pastes it here, generates a code at 1024 × 1024, downloads the PNG, and prints it on a small counter card: "Enjoyed your cake? Scan to review us."</p>
<p>Result: instead of hoping people search for the bakery later (they don't), the review is two taps away while the experience is fresh. The same card works forever — there's no monthly fee keeping the code alive, because the link lives inside the printed squares themselves. If the bakery ever changes the link, it simply generates and prints a new card.</p></div>"""),
("Tips for QR Codes That Scan First Time",
"""<ul>
<li><strong>Keep the destination short.</strong> The more text a code holds, the denser and harder to scan it becomes. Use a short URL where you can, and never encode a whole paragraph.</li>
<li><strong>Mind the quiet zone.</strong> Scanners need that empty white margin around the code. Don't crop it, and don't print the code on a busy or dark background.</li>
<li><strong>Size it for the scanning distance.</strong> A useful rule is a 10:1 ratio — a code scanned from 1 meter away should be at least 10 cm wide. Table cards can be small (around 2.5 cm / 1 inch minimum); posters need to be much bigger.</li>
<li><strong>Always test the final print.</strong> Scan the actual printed piece, in the lighting where it will live, before ordering 500 of them.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Encoding a link that later dies.</strong> The code never expires, but the page it opens can. Point codes at addresses you control and keep them alive — a scanned code that lands on a 404 is a wasted customer.</li>
<li><strong>Changing the destination after printing.</strong> With a static code, the content is fixed at print time. If you need changeable destinations, that's what (paid) dynamic QR services are for — for most menus, cards and signs, static is simpler and free forever.</li>
<li><strong>Reversing the colors.</strong> Codes are designed dark-on-light. White squares on a black background fail on many scanners.</li>
<li><strong>Placing codes out of reach.</strong> A beautiful code on a window too high to scan, or behind reflective glass, helps nobody. Think about where the phone will actually be.</li>
</ul>"""),
],
"faqs": [
("Do QR codes generated here expire?", "No. The code encodes your text or URL directly in the image, so it works forever — there's no service in the middle that could shut it off. The only thing that can break it is the destination itself changing or disappearing."),
("What size should I choose?", "The preview always shows at a comfortable size on screen; the size you pick is the resolution of the downloaded PNG. 256 is fine for a screen or document, 512 covers most uses, and 1024 gives print shops crisp edges for posters and signage."),
("Can I make a QR code for Wi-Fi or a phone number?", "Yes. Paste any text and the scanner will read exactly that. For a phone number use the tel: format (for example tel:+15551234567); plain text works for notes, serial numbers and instructions."),
("Is there a limit on how many times my code can be scanned?", "None at all. Scans aren't routed through ToolNova, so there's no tracking, no counter and no cap."),
("Why does my code look blurry when printed big?", "You probably downloaded the small 256 size and stretched it. Regenerate at 1024 × 1024 for print — the squares stay sharp at poster sizes."),
("Can I put my logo in the middle of the code?", "Not with this generator — it produces clean, standard codes. If you add a logo yourself in an image editor, keep it small, centered, and test-scan the result thoroughly; covering too many squares makes codes unreadable."),
],
"related": [("password-generator", "Password Generator"), ("image-compressor", "Image Compressor"), ("base64-encoder-decoder", "Base64 Encoder / Decoder")],
}

TOOLS["image-compressor"] = {
"name": "Image Compressor", "h1": "Image Compressor",
"lead": "Shrink JPEG, PNG and WebP images with a simple quality slider and see the before-and-after sizes before you download. Your photo is compressed right here in your browser — it's never uploaded to a server, which is exactly how image compression should work.",
"sections": [
("Why Image Size Matters More Than You Think",
"""<p>Modern phone cameras are wonderful and enormous. A single photo can be 4–8 MB, which is fine on your phone and a problem almost everywhere else: it crawls up to a website on a slow connection, eats a visitor's mobile data, blows an email attachment limit, and makes your pages load seconds slower — and slow pages lose people. Studies of web behavior consistently show visitors abandoning pages that take more than a few seconds to appear. Compressing an image re-encodes it more efficiently, trading a small, often invisible amount of detail for a file that's a fraction of the size.</p>
<p>The people who compress images daily: website owners and bloggers keeping pages fast, online sellers whose product photos must fit marketplace limits, students and office workers shrinking scans for application portals with strict MB caps, and anyone who has ever hit "attachment too large" at the worst possible moment. Because this tool works locally, it's also the right choice for personal photos you'd rather not hand to a random server.</p>"""),
("How to Use the Image Compressor",
"""<ol>
<li>Click "Choose an image" and pick a JPEG, PNG or WebP file from your device.</li>
<li>Set the quality slider. It starts at 80% — the sweet spot for most photos, where the size drops dramatically and the difference is hard to spot.</li>
<li>Choose an output format. JPEG is smallest for photos; WebP is smaller still and supported by all modern browsers; PNG keeps a transparent background.</li>
<li>Compare the original and compressed previews and their sizes, then click "Download Compressed Image". Compress as many images as you like, one at a time, free.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>You've photographed a product for your online shop: a 4032 × 3024 phone photo weighing <strong>4.6 MB</strong>. At the default 80% quality, saved as JPEG, it comes back at roughly <strong>620 KB</strong> — an 87% reduction. At normal viewing size on a product page, side by side, you'd struggle to tell them apart.</p>
<p>Drop the slider to 60% and the file falls to about 380 KB, still perfectly presentable for a web listing. That difference is your page loading in under a second instead of four — on a customer's phone, in a market with patchy signal, that's the difference between a sale and a shrug.</p></div>"""),
("Tips for Great Results",
"""<ul>
<li><strong>Start at 80%, then experiment.</strong> For most photos, 75–85% is where size savings are huge and quality loss is minimal. Go lower for thumbnails, higher for images people will zoom into.</li>
<li><strong>Pick the format to match the image.</strong> Photographs: JPEG or WebP. Logos, screenshots and anything with transparency or crisp text: PNG — but expect a bigger file.</li>
<li><strong>Keep your original.</strong> Compression is one-way; detail discarded can't come back. Save the compressed copy under a new name and keep the master file untouched.</li>
<li><strong>Compress for the display size.</strong> A 4000-pixel-wide photo displayed in a 800-pixel slot is wasted megabytes before compression even starts. If your platform lets you resize, do both.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Compressing an already-compressed file, over and over.</strong> Every re-encode of a JPEG discards a little more. Always start from the original for a new version.</li>
<li><strong>Judging quality zoomed to 400%.</strong> Compression artifacts you can only see at extreme zoom don't matter at the size anyone will actually view the image. Judge at 100%.</li>
<li><strong>Using PNG for photographs.</strong> A PNG photo can be ten times the size of the same image as JPEG, with no visible benefit. PNG's strength is transparency and sharp edges, not photos.</li>
<li><strong>Uploading private images to random "free" compressors.</strong> Many send your file to their server. This tool never does — the compression happens on your device — but make it a habit to check.</li>
</ul>"""),
],
"faqs": [
("Are my images uploaded to a server?", "No — never. The compression runs entirely in your browser using your own device's processing power. Your photos don't leave your machine, which makes this safe for personal pictures, documents and client work."),
("Which quality setting should I use?", "80% is the right starting point for almost everything — big savings, minimal visible change. Use 85–95% for images that will be displayed large or printed, and 50–70% for thumbnails and previews where small size matters most."),
("What's the difference between JPEG, PNG and WebP output?", "JPEG is the universal photo format — small and supported everywhere. WebP is a modern format that's usually 25–35% smaller than JPEG at the same quality and works in all current browsers. PNG preserves transparency and sharp edges but produces much larger files for photos."),
("Will compressing ruin my photo?", "Not if you keep the quality sensible. At 80%, changes are typically invisible at normal viewing sizes. The preview shows you the actual result before you download, so you can always raise the quality and try again."),
("Can I compress several images at once?", "This tool handles one image at a time so you can check each result. There's no limit on how many you process in a row."),
("Why didn't my PNG get much smaller?", "PNG compression is lossless — it can't discard detail the way JPEG can, so photographic PNGs stay large. If transparency doesn't matter, re-save the image as JPEG or WebP instead and you'll see a dramatic drop."),
],
"related": [("qr-code-generator", "QR Code Generator"), ("color-converter", "Color Converter"), ("word-counter", "Word Counter")],
"guide": ("compress-images-without-losing-quality", "How to Compress Images Without Ruining Their Quality"),
}

TOOLS["age-calculator"] = {
"name": "Age Calculator", "h1": "Age Calculator",
"lead": "Enter a date of birth and get an exact age in years, months and days — plus total days and weeks lived, the day of the week you were born, and a countdown to your next birthday. Handy for forms, eligibility checks, and settling arguments.",
"sections": [
("Why “How Old Am I?” Is Trickier Than It Sounds",
"""<p>Quick: how many days old is someone born on March 15, 2000? You can't answer that in your head — not exactly. Exact age arithmetic means untangling leap years (including the awkward rule that years divisible by 100 aren't leap years unless divisible by 400), months of four different lengths, and whether this year's birthday has happened yet. Humans are bad at it; forms that demand an exact age — school admissions, insurance applications, visa paperwork, sports league registrations, pension and retirement eligibility — don't accept "about 34".</p>
<p>This calculator does the calendar math properly. Beyond the headline years-months-days answer, it tells you your total days and weeks alive (a number that surprises everyone — most 30-year-olds have passed 10,000 days without noticing), the weekday of your birth, and how many days remain until your next birthday. You can also set the "age at date" to any date, past or future, which is what makes it genuinely useful for deadlines: not just how old someone is today, but how old they'll be on the day that matters.</p>"""),
("How to Use the Age Calculator",
"""<ol>
<li>Enter the date of birth using the date picker.</li>
<li>Leave "Age at date" as today, or set any other date — the first day of school, a competition cutoff, a retirement date.</li>
<li>Click "Calculate Age" and read the full breakdown: years, months, days, totals, birth weekday and next-birthday countdown.</li>
<li>Try it for family members — kids find their "total days" number endlessly fascinating.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>Take someone born on <strong>June 10, 1998</strong>, and ask their age on October 22, 2026. The calculator reports <strong>28 years, 4 months and 12 days</strong> — with <strong>10,361 total days</strong> (1,480 weeks) lived, born on a <strong>Wednesday</strong>, and <strong>231 days</strong> until their next birthday.</p>
<p>Now move the "age at date" to September 1, 2026 — a typical school cutoff. A child born August 28, 2020 shows as 6 years and 4 days: just old enough. A child born September 3, 2020 shows 5 years, 11 months and 29 days: two days short, waits a year. This is why exact calculators exist — "he turns six in September" isn't precise enough when a deadline is doing the deciding.</p></div>"""),
("Tips for Getting Exact Answers",
"""<ul>
<li><strong>Use official documents for the birth date.</strong> A surprising number of birthdays celebrated at parties differ by a day (or a year) from the registered date. For forms, the document wins.</li>
<li><strong>Ask the question the form is asking.</strong> "Age" usually means age today, but eligibility rules often mean age on a specific date — an exam day, a term start, December 31. Set that date explicitly.</li>
<li><strong>Remember the birthday rule.</strong> You turn a year older on your birthday, not on January 1. Someone born in December is the younger age for almost the whole calendar year.</li>
<li><strong>Total days make a fun milestone.</strong> Your 10,000th day alive happens around age 27 years and 4 months. It needs no gifts, but it deserves cake.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Subtracting years and stopping there.</strong> 2026 minus 1998 is 28, but until the June birthday passes, that person is still 27. The months-and-days part is where errors live.</li>
<li><strong>Ignoring leap years in day counts.</strong> A quick 365 × years estimate undercounts by one day for every February 29 lived through — seven or eight days by age 30.</li>
<li><strong>Mixing date formats.</strong> 03/04/2005 is March 4 in the US and April 3 almost everywhere else. Use the date picker and double-check the result reads the way you intended.</li>
<li><strong>Assuming twins or siblings share an "age at date" answer</strong> when a cutoff falls between their birthdays — near deadlines, days decide.</li>
</ul>"""),
],
"faqs": [
("Does the calculator handle leap years correctly?", "Yes — including the full Gregorian rules. Years divisible by 4 are leap years, except century years, which are leap years only if divisible by 400 (so 2000 was a leap year, but 1900 wasn't). Total day counts reflect every February 29 actually lived."),
("Can I calculate age at a future or past date?", "Yes. Change the \"Age at date\" field to any date — an exam day, a school cutoff, a wedding anniversary — and the answer is exact for that moment."),
("How is the years/months/days breakdown worked out?", "It's calendar age: full years up to the last birthday, then full calendar months, then the remaining days. It's the same convention used on official forms, which is why the numbers match what administrators expect."),
("What day of the week was I born on?", "The result includes it — check the \"Born on\" line. It's computed from the calendar, not guessed, and it's a fun thing to verify against family memory."),
("Is my birth date stored or shared?", "No. The calculation happens in your browser and nothing is sent anywhere. Birth dates are exactly the kind of personal data that should never leave your device for a simple calculation."),
("Why do some cultures give a different age?", "A few traditions count age differently — for example, counting a newborn as one year old, or everyone aging together at New Year. This calculator uses the international standard (completed years since birth) that forms and officialdom use."),
],
"related": [("bmi-calculator", "BMI Calculator"), ("emi-calculator", "EMI Calculator"), ("unit-converter", "Unit Converter")],
}

TOOLS["bmi-calculator"] = {
"name": "BMI Calculator", "h1": "BMI Calculator",
"lead": "Work out your Body Mass Index in metric or imperial units and see which category it falls into — underweight, healthy, overweight or obese — along with the healthy weight range for your height. Quick context for your health, with honest explanations of what BMI can and can't tell you.",
"sections": [
("What BMI Is — and What It Isn't",
"""<p>BMI (Body Mass Index) is a simple formula with a long history: your weight in kilograms divided by the square of your height in meters. It was devised in the 1830s by the Belgian statistician Adolphe Quetelet and adopted worldwide because it needs nothing but a scale and a tape measure. Doctors and insurers use it as a first-pass screening tool: across large populations, BMI correlates reasonably well with body fat and with risk for conditions like type 2 diabetes and heart disease.</p>
<p>Here's the honest part, because it matters: BMI knows nothing about <em>you</em> specifically. It can't tell muscle from fat, so a strength athlete can land in "overweight" with low body fat. It doesn't show where fat is carried, it behaves differently across ethnicities and ages, and it was never designed to diagnose anything. Used properly, it's a conversation starter — one number to discuss with a doctor alongside waist size, blood pressure, activity and family history. Used carelessly, as a verdict on a person's health, it misleads. This calculator gives you the number and the context together.</p>"""),
("How to Use the BMI Calculator",
"""<ol>
<li>Choose your units: Metric (kilograms and centimeters) or Imperial (pounds, feet and inches).</li>
<li>Enter your weight and height. For the most consistent number, weigh yourself in the morning and measure height barefoot — most of us are a touch shorter by evening.</li>
<li>Click "Calculate BMI" to see your score, its category, and the healthy weight range calculated for your specific height.</li>
<li>Re-check over time rather than daily. Weight naturally fluctuates by a kilogram or two with water and meals; trends over months are what count.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>Meet a typical case: <strong>70 kg, 175 cm tall</strong>. The math is 70 ÷ 1.75² = 70 ÷ 3.0625 = <strong>22.9</strong> — comfortably inside the healthy band of 18.5 to 24.9.</p>
<p>The calculator also flips the formula around: for 175 cm, the healthy weight range is <strong>56.7 kg to 76.3 kg</strong>. Now the same person at 85 kg gets a BMI of 27.8 — "overweight" — and can see they'd need to lose about 8.7 kg to reach the top of the healthy range. At 52 kg, BMI drops to 17.0, "underweight", a reminder that the scale has a healthy floor as well as a ceiling, and that being underweight carries its own risks.</p></div>"""),
("Making Sense of Your Number",
"""<ul>
<li><strong>Underweight (below 18.5):</strong> may signal under-nutrition or an underlying condition. Worth a chat with a doctor, especially if unintentional.</li>
<li><strong>Healthy (18.5–24.9):</strong> the range associated with the lowest population-level risk. Staying active matters even here — a healthy BMI with zero exercise isn't the full picture.</li>
<li><strong>Overweight (25–29.9):</strong> a nudge, not an alarm. Many people in this band are metabolically healthy, but risk begins climbing, and waist circumference adds useful context.</li>
<li><strong>Obese (30 and above):</strong> risk of several chronic conditions rises more steeply. A doctor can help separate what the number means for you personally and what to do about it.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Using BMI for children and teens.</strong> Under-20s need age- and sex-specific percentile charts, not the adult cutoffs. A BMI of 22 means something different at 12 than at 32.</li>
<li><strong>Treating it as a body-fat percentage.</strong> It isn't one. Two people with identical BMIs can have very different body compositions — a rugby player and a sedentary office worker are the classic example.</li>
<li><strong>Obsessing over decimal points.</strong> The difference between 24.9 and 25.1 is a glass of water and a rounding line, not a health cliff. Categories are guide rails, not cliffs.</li>
<li><strong>Self-diagnosing from one number.</strong> BMI is a screening tool. Pregnant women, the elderly, and very muscular people in particular should interpret it only with professional guidance.</li>
</ul>"""),
],
"faqs": [
("How is BMI calculated?", "BMI = weight (kg) ÷ height (m)². In imperial units the equivalent is 703 × weight (lb) ÷ height (in)². This calculator handles the conversions for you, which is why metric and imperial entries for the same person give the same result."),
("What is a healthy BMI range?", "For adults, the standard categories are: underweight below 18.5, healthy 18.5–24.9, overweight 25–29.9, and obese 30 or above. These are the WHO cutoffs used by most doctors and health organizations."),
("My BMI says overweight but I'm muscular. Is it wrong?", "Quite possibly, for you. BMI can't distinguish muscle from fat, and muscle is denser. Athletes and manual workers often score “overweight” with genuinely low body fat. Waist circumference, body-fat measurements and a doctor's assessment fill in what BMI leaves out."),
("Does BMI apply to children?", "Not with these cutoffs. Children and teens are assessed with BMI-for-age percentiles that account for growth and sex. Use a pediatric chart or ask your child's doctor instead."),
("How often should I check my BMI?", "Monthly is plenty for tracking a trend. Daily weighing mostly measures water. What matters is the direction over months, combined with how you feel, your energy, and other health markers."),
("Can I lower my BMI safely?", "Gradual is the watchword — most guidance aims for steady changes in eating and activity rather than crash diets, which typically rebound. If your BMI is in the obese range or you have other conditions, involve a doctor or dietitian from the start rather than going it alone."),
],
"related": [("age-calculator", "Age Calculator"), ("percentage-calculator", "Percentage Calculator"), ("emi-calculator", "EMI Calculator")],
"guide": ("bmi-explained", "BMI Explained: What Your Number Really Means"),
}

TOOLS["percentage-calculator"] = {
"name": "Percentage Calculator", "h1": "Percentage Calculator",
"lead": "Three everyday percentage problems, solved instantly: what is X% of Y, X is what percent of Y, and the percentage change from one value to another. Discounts, tips, taxes, test scores and price rises — this is the math daily life keeps asking for.",
"sections": [
("The Three Questions Behind Almost Every Percentage",
"""<p>Strip away the context and nearly every real-world percentage problem is one of three questions. <strong>"What is X% of Y?"</strong> — a 20% discount on an $85 jacket, a 15% tip on a $64 dinner, 8% sales tax. <strong>"X is what percent of Y?"</strong> — you scored 43 of 50 on a test, your team won 31 of 82 games, a task is 17 of 20 steps done. <strong>"What's the percentage change from X to Y?"</strong> — rent went from $1,200 to $1,320, a stock moved from $48 to $42, your salary rose from $52,000 to $55,900. This page puts all three side by side, because in practice people constantly mix them up — especially the second and third.</p>
<p>Percentages feel slippery because they're relative: the same $10 is 50% of $20 and 1% of $1,000. They also hide a famous trap — percentages don't cancel out symmetrically. A price that rises 20% then falls 20% doesn't return to where it started, and this calculator is the quickest way to prove that to yourself (try it: 100 up 20% is 120; 120 down 20% is 96).</p>"""),
("How to Use the Percentage Calculator",
"""<ol>
<li>Find the section matching your question — the three calculators are numbered and labeled in plain language.</li>
<li>Enter your two numbers. Decimals are fine: 7.5% tax and 12.75 prices work exactly as you'd expect.</li>
<li>Read the result as you type. There's no equals button to hunt for.</li>
<li>Sanity-check big answers with a rough estimate — 10% is easy to find (just move the decimal), and most percentages are near a multiple of it.</li>
</ol>"""),
("A Worked Example for Each Question",
"""<div class="example"><p><strong>Discount:</strong> What is 30% off $129.99? The first calculator says 30% of 129.99 is 39.00 — so you pay $129.99 − $39.00 = <strong>$90.99</strong>.</p>
<p><strong>Score:</strong> You answered 37 of 45 questions correctly. The second calculator: 37 is <strong>82.2%</strong> of 45 — a solid B in most grading schemes.</p>
<p><strong>Change:</strong> Your monthly grocery spend went from $640 to $736. The third calculator reports a <strong>15% increase</strong> — (736 − 640) ÷ 640 × 100. Whether that's inflation or lifestyle creep, at least now it's a number you can act on.</p></div>"""),
("Tips for Not Getting Fooled by Percentages",
"""<ul>
<li><strong>"Percent of" vs "percentage points" are different.</strong> An interest rate rising from 4% to 5% is up 1 percentage point — but a 25% relative increase. News headlines exploit the confusion constantly.</li>
<li><strong>Anchor with 10%.</strong> To estimate any percentage mentally: find 10% (move the decimal one place), then scale — 30% is three times that, 5% is half of it.</li>
<li><strong>Successive changes multiply, they don't add.</strong> A 10% raise followed by a 10% raise is a 21% total increase, not 20% — each applies to a bigger base.</li>
<li><strong>Always ask "percent of what?"</strong> "50% more" is meaningless until the base is named. It's the oldest trick in advertising.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Reversing the change formula.</strong> Percentage change is always (new − old) ÷ old. Dividing by the new value instead gives a different, wrong answer — and the error grows with bigger changes.</li>
<li><strong>Believing up-then-down returns to zero.</strong> Up 50% then down 50% leaves you 25% below the start. The down percentage acts on the inflated value.</li>
<li><strong>Adding percentages of different bases.</strong> "20% off, then another 10% off" is 28% off total, not 30% — the second discount applies to the already-reduced price.</li>
<li><strong>Confusing a discount with the price paid.</strong> 30% off $100 is a $30 discount and a $70 payment. Reading the calculator's "30% of" result as the final price is the classic checkout error.</li>
</ul>"""),
],
"faqs": [
("How do I calculate a percentage of a number?", "Multiply the number by the percentage divided by 100. For example, 15% of 240 = 240 × 0.15 = 36. The first calculator on this page does it instantly, including decimals."),
("What's the difference between percentage change and percentage difference?", "Percentage change compares an old value to a new one over time and has a direction — up or down. It always divides by the old value. (Percentage difference, used when neither value is “first”, divides by the average instead — this page's third tool is the everyday change version.)"),
("How do I turn a fraction or score into a percentage?", "Divide the part by the whole and multiply by 100 — that's the second calculator. 37 ÷ 45 = 0.822, which is 82.2%."),
("Why doesn't a 20% rise followed by a 20% fall get me back to the start?", "Because the two percentages act on different amounts. 100 rising 20% becomes 120; 20% of 120 is 24, so falling 20% lands at 96. The bases differ, so the amounts differ."),
("How do I calculate a tip or tax quickly?", "For a tip, use the first calculator: 18% of a $64 bill is $11.52. For tax, calculate the percentage of the pre-tax price and add it on — or multiply the price by 1 plus the rate (× 1.08 for 8%)."),
("Can the calculator handle decimals and negative changes?", "Yes. Enter rates like 7.5% and values of any size. For the change calculator, if the new value is smaller, the result shows as a negative percentage — a decrease."),
],
"related": [("emi-calculator", "EMI Calculator"), ("bmi-calculator", "BMI Calculator"), ("unit-converter", "Unit Converter")],
}

TOOLS["case-converter"] = {
"name": "Case Converter", "h1": "Case Converter",
"lead": "Paste your text once, then flip it between UPPERCASE, lowercase, Title Case, Sentence case and more with a single click — plus a one-click fix for accidental double spaces. For anyone who has ever retyped a paragraph because Caps Lock betrayed them.",
"sections": [
("A Small Tool That Saves Real Annoyance",
"""<p>Everyone knows the moment: you look up from the keyboard and discover three paragraphs written entirely in capitals because Caps Lock was on — or a headline typed in lowercase that an editor wants in Title Case, or a product list that needs to be uniform before it goes into a spreadsheet. Retyping is slow and error-prone. Converting is instant and exact. This tool applies the standard case rules to your whole text at once, preserves your line breaks, and shows a live word and character count so you can confirm nothing was lost in the shuffle.</p>
<p>The regular users are a varied crowd. Writers and students fixing headings and titles. Social media managers who draft in one style and publish in another. Data-entry staff standardizing names and addresses ("JOHN SMITH", "john smith" and "John Smith" should not be three different customers). Developers renaming variables and labels. And anyone copying text from a PDF or an old system that shouts everything in capitals, who wants it to read like a human wrote it.</p>"""),
("How to Use the Case Converter",
"""<ol>
<li>Paste or type your text into the box.</li>
<li>Click the case you need — the result replaces the text immediately, so you can try another style just as fast.</li>
<li>Check the word and character count under the buttons if your destination has a limit.</li>
<li>Copy the result with the Copy button and paste it where it's going. Use Clear to start over.</li>
</ol>"""),
("The Cases, Explained With One Sentence",
"""<div class="example"><p>Take the sentence <em>"the quick brown fox jumps over the lazy dog"</em> and watch what each button does:</p>
<p><strong>UPPERCASE</strong> → THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG — for labels, warnings and acronyms; use sparingly, because on the internet it reads as shouting.</p>
<p><strong>lowercase</strong> → the quick brown fox jumps over the lazy dog — for normalizing messy data and casual text.</p>
<p><strong>Title Case</strong> → The Quick Brown Fox Jumps Over The Lazy Dog — every word capitalized; the convention for headlines, book titles and headings.</p>
<p><strong>Sentence case</strong> → The quick brown fox jumps over the lazy dog — only the first word and proper nouns capitalized; how normal prose (and most modern interfaces) are written.</p>
<p><strong>Capitalize Each Word</strong> works like Title Case across every line — handy for lists of names or menu items.</p>
<p><strong>aLtErNaTiNg</strong> → ThE qUiCk BrOwN fOx — alternating letters; mostly for playful social posts and memes.</p>
<p><strong>Remove Extra Spaces</strong> → collapses runs of spaces into one — the silent fix for text pasted from PDFs and emails.</p></div>"""),
("Tips for Cleaner Conversions",
"""<ul>
<li><strong>Proofread proper nouns after lowercasing.</strong> No converter knows that "apple" the company is Apple and "march" the month isn't a name. A quick skim for names, places and brands is worth it.</li>
<li><strong>Fix double spaces while you're here.</strong> Pasted text often hides them, and they make justified text look gappy. One click before you copy saves embarrassment later.</li>
<li><strong>Match the style guide you answer to.</strong> Newsrooms and universities often specify sentence case for headlines even where Title Case is common elsewhere. Convert to what your editor expects, not your habit.</li>
<li><strong>Convert before formatting.</strong> Case-changing after you've bolded pieces and added links inside another editor can mangle the formatting. Convert the plain text first, then style it.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Using ALL CAPS for emphasis in professional text.</strong> It reads as shouting and actually slows reading — our eyes recognize lowercase word shapes faster. Use bold instead.</li>
<li><strong>Title-Casing everything in a document.</strong> Headings in Title Case, body in sentence case. When everything is emphasized, nothing is.</li>
<li><strong>Assuming conversion fixes spelling.</strong> It changes only letter case. "Teh quick" stays "teh quick" — in very neat capitals.</li>
<li><strong>Forgetting acronyms.</strong> Sentence case will turn "NASA" into "Nasa" if it isn't at the start of a sentence. Scan for NASA, USA, DIY and similar after converting long text.</li>
</ul>"""),
],
"faqs": [
("What is the difference between Title Case and Capitalize Each Word?", "On ordinary text they look the same — every word starts with a capital. \"Capitalize Each Word\" applies that rule mechanically to every line, which is what you want for lists and labels. Title Case follows the same convention used for headlines and publication titles."),
("Will converting case change my line breaks or spacing?", "No. Only the letters change case; your paragraph structure stays intact. The one exception is the dedicated Remove Extra Spaces button, which deliberately collapses multiple spaces into single ones."),
("Does Sentence case handle names correctly?", "It capitalizes the first word of each sentence. It can't know that a mid-sentence word is a name, so give the result a quick skim and re-capitalize people, places and brands — a ten-second job that no automated tool can fully do for you."),
("Is there a limit to how much text I can convert?", "No practical limit — full chapters convert instantly, because the work happens in your browser rather than on a server."),
("Does my text leave my computer?", "No. Like every ToolNova tool, the conversion happens locally in your browser. Paste confidential drafts without worry."),
("Can I undo a conversion?", "The fastest undo is to click a different case — conversions are reversible as long as the original information survives. Note that lowercasing is partly destructive: “McDonald” becomes “mcdonald”, and no tool can know the capital D belonged there. For precious text, keep a copy of the original."),
],
"related": [("word-counter", "Word Counter"), ("remove-duplicate-lines", "Remove Duplicate Lines"), ("lorem-ipsum-generator", "Lorem Ipsum Generator")],
}

TOOLS["json-formatter"] = {
"name": "JSON Formatter", "h1": "JSON Formatter & Validator",
"lead": "Format messy JSON into clean, readable output, minify it back down, or just validate it — with a plain-language error message when something's wrong instead of a cryptic failure. Built for developers, and for anyone an API has ever sent a wall of unformatted text.",
"sections": [
("Why JSON Always Needs a Formatter Eventually",
"""<p>JSON is the world's default data hand-off format — APIs, configuration files, app storage and logs all speak it. It's also routinely delivered in the least readable form possible: one enormous line, no indentation, thousands of characters deep. Humans can't debug what they can't scan. Formatting (or “beautifying”) restructures the same data with line breaks and indentation so nesting becomes visible at a glance: which keys belong to which object, where an array opens and closes, whether a value is a string, a number or a boolean.</p>
<p>The other half of the job is validation. JSON's rules are simple but unforgiving — one trailing comma, one set of single quotes, one unquoted key, and the whole document is invalid. Parsers in production code often fail silently or with useless messages. This tool tells you not just <em>that</em> your JSON is broken but <em>where</em>, so you can fix the actual character at fault instead of proofreading 4,000 lines by eye. And when you're done reading, Minify compresses it back to the compact form machines prefer — smaller payloads, faster transfers.</p>"""),
("How to Use the JSON Formatter",
"""<ol>
<li>Paste your JSON into the input box — a minified API response, a config file, a log fragment, anything.</li>
<li>Pick an indentation style: 2 spaces (the most common convention), 4 spaces, or tabs.</li>
<li>Click “Format / Beautify” for readable output, “Minify” for the compact version, or “Validate Only” to check validity without reformatting.</li>
<li>If there's an error, read the message, fix the spot it identifies in your input, and run it again. Copy the finished output with one click.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>An API returns this single line:</p>
<p><code>{"user":{"id":4815,"name":"Sara","roles":["admin","editor"],"prefs":{"theme":"dark","alerts":true}}}</code></p>
<p>Formatted with 2-space indentation, the same data becomes a tidy tree: <code>user</code> opens, and inside it <code>id</code>, <code>name</code>, the <code>roles</code> array with its two entries on separate lines, and the nested <code>prefs</code> object — structure you can verify in seconds. Nothing about the data changed; only its readability did. Then suppose the original had a trailing comma after <code>true</code>. Instead of a mystery failure, the validator flags a syntax error at that position — delete the comma, re-run, done.</p></div>"""),
("Common JSON Errors This Catches",
"""<ul>
<li><strong>Trailing commas</strong> after the last item in an object or array — legal in JavaScript, illegal in JSON, and the number-one culprit.</li>
<li><strong>Single quotes</strong> around keys or strings. JSON demands double quotes, everywhere.</li>
<li><strong>Unquoted keys</strong> — <code>{name: "Sara"}</code> is a JavaScript object, not JSON.</li>
<li><strong>Comments</strong> pasted in from a config file. Standard JSON allows none.</li>
<li><strong>Mismatched brackets</strong> — a <code>}</code> where a <code>]</code> belongs, usually after hand-editing a long file.</li>
<li><strong>Special values</strong> like <code>NaN</code>, <code>undefined</code> or <code>Infinity</code>, which JSON doesn't recognize.</li>
</ul>"""),
("Tips for Working With JSON Day to Day",
"""<ul>
<li><strong>Validate before you integrate.</strong> Pasting a sample API response here takes ten seconds and can save an hour of wondering why your app shows nothing.</li>
<li><strong>Keep one formatting convention per project.</strong> Two spaces is the most common in web tooling; consistency keeps diffs clean when JSON lives in version control.</li>
<li><strong>Never hand-edit minified JSON.</strong> Format it, edit the readable version, then minify again if the destination needs it compact.</li>
<li><strong>Be careful with secrets.</strong> Real API responses can contain tokens and personal data. This formatter runs entirely in your browser, so nothing is uploaded — a habit worth demanding from any online JSON tool.</li>
</ul>"""),
],
"faqs": [
("What's the difference between formatting and validating?", "Formatting restructures valid JSON so it's easy to read. Validating only answers one question — is this legal JSON or not — and points at the error if it isn't. Formatting a document also validates it; invalid JSON can't be formatted."),
("Why does the validator reject my JavaScript object?", "Because JSON is stricter than JavaScript. Keys must be double-quoted, strings must use double quotes, and trailing commas and comments aren't allowed. The error message will point at the first place your input breaks a JSON rule."),
("Does formatting change my data?", "No. Whitespace between tokens isn't data. The formatted and minified versions contain exactly the same keys, values and structure — parse either one and you get identical data back."),
("Is my JSON uploaded to a server?", "No. Parsing and formatting happen in your browser with JavaScript. You can safely format payloads containing private or internal data — though you should still treat real credentials with care everywhere."),
("Which indentation should I choose?", "Two spaces is the most widely used convention in web APIs and tooling, and keeps wide documents on screen. Four spaces is easier for some readers. Tabs let every viewer set their own visual width. There's no wrong answer — consistency matters more than the choice."),
("Can this handle very large JSON files?", "Yes, within reason — multi-megabyte documents format fine on a modern device, since everything is processed locally. Extremely deep nesting may become hard to read rather than hard to process; the validator will still check it."),
],
"related": [("base64-encoder-decoder", "Base64 Encoder / Decoder"), ("word-counter", "Word Counter"), ("remove-duplicate-lines", "Remove Duplicate Lines")],
}

TOOLS["base64-encoder-decoder"] = {
"name": "Base64 Encoder / Decoder", "h1": "Base64 Encoder / Decoder",
"lead": "Encode text to Base64 or decode Base64 back into readable text — UTF-8 safe, so accents, emoji and non-English scripts survive the round trip. For developers, and for anyone who has ever received a mysterious block of characters ending in = signs.",
"sections": [
("What Base64 Actually Is (and Isn't)",
"""<p>Base64 is a way of writing arbitrary data using only 64 safe characters: A–Z, a–z, 0–9, plus <code>+</code> and <code>/</code>, with <code>=</code> as padding. It exists because many systems — email being the classic example — were built to carry plain text and mangle anything else. Encode binary or special-character data as Base64 and it travels through those systems untouched, then decodes back to exactly what it was. That's why you'll find it inside email attachments, embedded images in web pages (data URIs), authentication headers, tokens, and API payloads.</p>
<p>Two clarifications save a lot of confusion. First, <strong>Base64 is not encryption</strong>. It hides nothing; anyone can decode it in a second — as this very page demonstrates. Never treat a Base64 string as a way to keep a secret. Second, encoding isn't free: Base64 output is about 33% larger than the input, because it spends 4 characters representing every 3 bytes. It's a transport format, not a compression format. This particular tool is UTF-8 safe, which matters more than it sounds: naive encoders choke on characters outside plain English ASCII, while this one round-trips Arabic, Chinese, emoji and accented European text correctly.</p>"""),
("How to Use the Base64 Tool",
"""<ol>
<li>Type or paste your text into the Input box.</li>
<li>Click “Encode to Base64” to encode it, or paste a Base64 string and click “Decode from Base64” to recover the original.</li>
<li>Read the result in the Output box and copy it with one click.</li>
<li>Handy shortcut: “Use Output as Input” feeds the result back in, so you can decode twice (some systems double-encode) or verify an encode by immediately reversing it.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>Type the word <strong>Hello</strong> and encode it. The output is <code>SGVsbG8=</code>. Five letters became eight characters — the ≈33% growth, plus an <code>=</code> padding character rounding the output to a multiple of four.</p>
<p>Now the more revealing test: encode <strong>“Café ☕”</strong>. The output is <code>Q2Fmw6kg4piV</code>. The é and the coffee emoji are multi-byte characters in UTF-8, and a UTF-8-safe encoder like this one handles them properly — decode the result and you get your exact text back, accents and emoji intact. With a naive encoder you'd get corrupted characters or an outright error; that's the difference UTF-8 support makes, and it's why text “breaks” in some lesser tools.</p></div>"""),
("Everyday Places You'll Meet Base64",
"""<ul>
<li><strong>Authentication headers:</strong> HTTP Basic auth sends credentials as Base64 — convenient, and exactly why it must travel over HTTPS, since it's trivially reversible.</li>
<li><strong>Data URIs:</strong> small images and fonts embedded directly in HTML/CSS as Base64 text, saving a network request.</li>
<li><strong>Email attachments:</strong> MIME encoding turns files into Base64 so mail servers built for text can carry them.</li>
<li><strong>Tokens and IDs:</strong> many API keys, session tokens and JWT parts are Base64url (a cousin using <code>-</code> and <code>_</code> instead of <code>+</code> and <code>/</code>).</li>
<li><strong>Config and DevOps:</strong> Kubernetes secrets and countless config formats store values Base64-encoded — again, encoding, not protection.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Using Base64 as security.</strong> Encoding a password or key in Base64 conceals it from nobody. It's the textbook equivalent of a “no peeking” sign.</li>
<li><strong>Decoding a truncated string.</strong> Copy-paste often clips the ends. If decoding fails or produces garbage, check that the full string — including any trailing <code>=</code> padding — made it across.</li>
<li><strong>Mixing up standard and URL-safe variants.</strong> A string containing <code>-</code> or <code>_</code> is Base64url, common in tokens. Standard decoders may reject it; the giveaway is those two characters.</li>
<li><strong>Double-encoding by accident.</strong> Encoding an already-encoded string produces a longer string that needs two decodes. If your decoded output still looks like Base64, decode once more.</li>
</ul>"""),
],
"faqs": [
("Is Base64 a form of encryption?", "No — it's an encoding, like writing a word in capital letters. It changes representation, not secrecy. Anyone with any decoder (including this page) can reverse it instantly. For secrecy you need real encryption; for passwords, proper hashing."),
("Why does the encoded text end with = signs?", "Base64 output is always a multiple of 4 characters. If your input doesn't divide neatly, = characters pad the end to complete the final group. One or two padding characters is perfectly normal."),
("Why is the output longer than my input?", "Base64 stores 3 bytes of input in 4 characters of output, so the result grows by about a third. That's the trade for making data safe to pass through text-only systems."),
("Can this tool handle emoji and non-English text?", "Yes. It's UTF-8 safe, so Arabic, Chinese, accented characters and emoji all encode and decode correctly. Many simpler tools fail here because they assume every character is a single byte."),
("What if decoding gives me an error or nonsense?", "Usually the input isn't valid Base64: characters outside the Base64 alphabet, a clipped beginning or end, or line breaks and spaces pasted into the middle. Copy the complete string — padding included — and try again."),
("What's the difference between Base64 and Base64url?", "Base64url swaps + and / for - and _ so the result is safe inside URLs and filenames, and often drops the padding. You'll meet it in tokens and links. If a string contains - or _, it's probably the URL-safe variant."),
],
"related": [("json-formatter", "JSON Formatter"), ("password-generator", "Password Generator"), ("qr-code-generator", "QR Code Generator")],
}

TOOLS["lorem-ipsum-generator"] = {
"name": "Lorem Ipsum Generator", "h1": "Lorem Ipsum Generator",
"lead": "Generate classic placeholder text by the paragraph, sentence or word — with the option to start with the traditional “Lorem ipsum dolor sit amet…” Designer-friendly filler that looks like real copy, so layouts get judged on design, not on unfinished writing.",
"sections": [
("Why Designers Still Reach for Fake Latin",
"""<p>Placeholder text solves a real problem: real copy is distracting. Show a client a website mockup filled with their actual draft text and they'll spend the meeting proofreading instead of looking at the layout. Show them a headline that says “HEADLINE GOES HERE” and the design looks broken and empty. Lorem ipsum threads the needle — it has the rhythm, word lengths and texture of real prose, so spacing, typography and hierarchy can be judged honestly, while carrying no meaning anyone can argue with.</p>
<p>That's why, five centuries after it first appeared in print, it remains the default filler for designers, developers, typesetters and template builders. This generator gives you three useful granularities: full <strong>paragraphs</strong> for body copy, <strong>sentences</strong> for cards, testimonials and captions, and <strong>words</strong> when you need an exact length for a headline or button-adjacent blurb. You can start with the canonical opening or dive straight into varied text, generate as much as you need, and copy it in one click.</p>"""),
("How to Use the Lorem Ipsum Generator",
"""<ol>
<li>Enter how much text you need in the Amount field.</li>
<li>Choose the unit: Paragraphs, Sentences or Words.</li>
<li>Leave the “Start with Lorem ipsum…” box ticked for the classic opening, or untick it for text that starts mid-flow — better for filling later paragraphs.</li>
<li>Click “Generate”, check the result in the output box, and copy it straight into your design, document or code.</li>
</ol>"""),
("A 30-Second History of Lorem Ipsum",
"""<div class="example"><p>Here's the part most people never learn: lorem ipsum isn't gibberish, and it isn't random. It's scrambled from a real book — Cicero's <em>de Finibus Bonorum et Malorum</em> (“On the Ends of Good and Evil”), written in 45 BC. The famous opening, “Lorem ipsum dolor sit amet…”, is a chopped-up fragment of “dolorem ipsum” — “pain itself” — from a passage about pleasure and suffering.</p>
<p>A printer in the 1500s scrambled the text to make a type specimen book, and it has been the printing industry's dummy text ever since. It survived letterpress, phototypesetting, and desktop publishing — Letraset sheets popularized it in the 1960s — before Aldus PageMaker carried it into the digital era. When you generate it here, you're using the same filler that demonstrated Gutenberg-era typefaces. (Probably.)</p></div>"""),
("Tips for Using Placeholder Text Well",
"""<ul>
<li><strong>Match real-world lengths.</strong> Generate roughly as much text as the final copy will have. A design that looks balanced with two lines of lorem can fall apart under a real six-line paragraph.</li>
<li><strong>Mix your units.</strong> A realistic page needs paragraphs for the body, sentences for cards and captions, and a handful of words for headings. Generating all three from here keeps the texture consistent.</li>
<li><strong>Test the ugly cases too.</strong> Fill one section with a single very long paragraph and another with one short sentence. Layouts should survive both, because real content will eventually do both.</li>
<li><strong>Never ship it.</strong> Set a hard rule: lorem ipsum in a live product is a bug. It slips through embarrassingly often — search your site for “lorem” before every launch.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Presenting lorem-filled designs without saying so.</strong> Clients have approved mockups thinking the Latin was a styling choice. A ten-second explanation at the start saves a confused email later.</li>
<li><strong>Using it where meaning matters.</strong> Navigation labels, buttons, error messages and forms should always be designed with real words — usability lives there, and dummy text hides real problems like a checkout button that needs the word “Checkout”.</li>
<li><strong>Generating far more than you need and trimming randomly.</strong> Cut mid-sentence and your mockup quietly looks sloppy. Generate the right amount instead — that's what the Words and Sentences options are for.</li>
<li><strong>Telling clients it's “just Greek”.</strong> It's Latin — and now you know whose. (The saying is “it's all Greek to me”; the filler is Cicero.)</li>
</ul>"""),
],
"faqs": [
("What does “lorem ipsum dolor sit amet” mean?", "It's a scrambled fragment of Cicero, not a clean sentence, so it doesn't translate exactly. The recognizable piece, “dolorem ipsum”, means “pain itself”, from a passage discussing pleasure and pain in de Finibus (45 BC). The scrambling is deliberate — the point is text that looks like language without communicating anything."),
("How much text can I generate?", "As much as you need — set the amount and unit and generate again for more. Paragraphs for long-form layouts, sentences for components, words for precise lengths like headlines and labels."),
("Can I use lorem ipsum in a real, published project?", "As temporary filler during design and development, absolutely — that's its purpose. Just replace it with real content before anything goes live; published lorem ipsum is a classic and very visible oversight."),
("Why not just type “text text text” or repeat a sentence?", "Repeated words create visible patterns that distort how a layout reads — every line looks identical, so spacing and typography can't be judged fairly. Lorem ipsum's varied word lengths mimic real prose, which is precisely its value."),
("Is this the traditional version of the text?", "Yes — it draws on the standard lorem ipsum vocabulary and sentence patterns in circulation since the 1500s, including the classic opening when you keep the start option ticked."),
("Do designers still use lorem ipsum with real content available?", "Many do for early stages, then switch to realistic draft content as a project matures. Lorem ipsum is best for judging pure layout and typography before copy enters the conversation — use it early, replace it deliberately."),
],
"related": [("word-counter", "Word Counter"), ("case-converter", "Case Converter"), ("remove-duplicate-lines", "Remove Duplicate Lines")],
}

TOOLS["unit-converter"] = {
"name": "Unit Converter", "h1": "Unit Converter",
"lead": "Convert length, weight and temperature between metric and imperial units — meters to feet, kilograms to pounds, Celsius to Fahrenheit and more — with a swap button for instant reverse conversions. The translator for a world that refuses to agree on measurements.",
"sections": [
("Two Measurement Worlds, One Converter",
"""<p>Most of the world measures in metric: meters, kilograms, Celsius. The United States — plus a stubborn pocket of everyday British usage — runs on inches, pounds and Fahrenheit. Everyone else lives in the collision zone: recipes from American blogs weighed in cups and ounces, luggage limits in kilograms, a height asked for in feet and inches on a form, a weather forecast in a unit you don't think in. Conversion errors in these moments range from funny (a cake with ten times the flour) to famous — NASA lost a $125 million Mars orbiter in 1999 because one team's software output pound-force seconds while another expected newton-seconds.</p>
<p>This converter covers the three categories daily life actually needs. <strong>Length:</strong> millimeters through miles, including the inches-feet-yards chain. <strong>Weight:</strong> grams, kilograms, tonnes, ounces, pounds and stone. <strong>Temperature:</strong> Celsius, Fahrenheit and Kelvin — handled by formula rather than a simple ratio, because temperature scales start at different zeros, which is why it's the category everyone gets wrong by hand.</p>"""),
("How to Use the Unit Converter",
"""<ol>
<li>Pick a category — Length, Weight or Temperature. The unit lists update to match.</li>
<li>Type your value, then choose the From and To units.</li>
<li>Read the converted result, shown with the full equation so you can see exactly what was computed.</li>
<li>Hit the swap button (⇅) to reverse the conversion instantly — perfect for checking your answer or pricing both directions.</li>
</ol>"""),
("A Worked Example for Each Category",
"""<div class="example"><p><strong>Length:</strong> You're 5 feet 10 inches and a form wants centimeters. Convert 70 inches (5×12 + 10): <strong>177.8 cm</strong>.</p>
<p><strong>Weight:</strong> Your suitcase reads 154 lb on a US scale and the airline limit is in kilograms. 154 lb = <strong>69.9 kg</strong> — better check that limit twice.</p>
<p><strong>Temperature:</strong> A recipe says bake at 350°F; your oven is Celsius. 350°F = <strong>176.7°C</strong> — call it 175°C, Gas Mark 4. And normal body temperature, 98.6°F, is the 37°C you already knew.</p></div>"""),
("Reference Points Worth Memorizing",
"""<ul>
<li><strong>1 inch = 2.54 cm</strong> exactly — the anchor of the whole length system. A foot is 30.48 cm, a mile is 1.609 km.</li>
<li><strong>1 kg ≈ 2.205 lb.</strong> For a quick estimate, double the kilograms and add a tenth: 70 kg → 140 + 14 = 154 lb, almost exact.</li>
<li><strong>Water boils at 100°C / 212°F</strong> and freezes at 0°C / 32°F. Room temperature is about 20–22°C (68–72°F).</li>
<li><strong>1 stone = 14 lb = 6.35 kg</strong> — still the everyday unit for body weight in the UK.</li>
<li><strong>−40° is where Celsius and Fahrenheit meet</strong> — the one temperature that's identical in both, and a fact that wins pub quizzes.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Converting temperature like a ratio.</strong> 20°C is not “twice” 10°C in Fahrenheit terms, because the scales don't share a zero. Use the formulas — or this tool — never a multiplier.</li>
<li><strong>Confusing fluid ounces with ounces of weight.</strong> One measures volume, the other mass; they coincide only for water, approximately. This converter handles weight; for cooking volumes, check whether your recipe means cups or grams.</li>
<li><strong>Rounding mid-calculation.</strong> Converting a converted number compounds rounding errors. Always start again from the original value.</li>
<li><strong>Forgetting which ton you mean.</strong> A metric tonne is 1,000 kg; a US ton is 2,000 lb (907 kg); a British long ton is 2,240 lb. In shipping and industry, that 10% gap matters.</li>
</ul>"""),
],
"faqs": [
("How do I convert Celsius to Fahrenheit?", "Multiply by 9/5 and add 32. For example, 25°C × 9/5 = 45, + 32 = 77°F. The converter does it instantly, including Kelvin — but for a mental estimate, doubling Celsius and adding 30 gets you close (25°C → ≈80°F)."),
("How many centimeters are in an inch?", "Exactly 2.54 — it's defined that way internationally, not measured approximately. A foot (12 inches) is therefore exactly 30.48 cm, and a yard exactly 0.9144 m."),
("Why does temperature convert differently from length and weight?", "Length and weight scales share a true zero, so conversions are simple multiplications. Celsius and Fahrenheit set their zeros at different points (and Kelvin at absolute zero), so converting needs an offset as well as a scale factor — add or subtract 32 as well as multiplying."),
("Which units does this converter support?", "Length: millimeters, centimeters, meters, kilometers, inches, feet, yards and miles. Weight: grams, kilograms, tonnes, ounces, pounds and stone. Temperature: Celsius, Fahrenheit and Kelvin."),
("How accurate are the results?", "The conversion factors are the exact international definitions (2.54 cm per inch, 0.45359237 kg per pound), and results are shown rounded sensibly for everyday use. For engineering work, convert here and keep extra decimal places from the equation shown."),
("What's the fastest way to estimate pounds from kilograms mentally?", "Double the kilograms, then add 10% of that doubled figure. 80 kg → 160 → +16 → 176 lb. The exact answer is 176.4 lb — close enough for luggage and gym plates."),
],
"related": [("percentage-calculator", "Percentage Calculator"), ("emi-calculator", "EMI Calculator"), ("age-calculator", "Age Calculator")],
}

TOOLS["emi-calculator"] = {
"name": "EMI Calculator", "h1": "EMI / Loan Calculator",
"lead": "See your exact monthly payment, total interest and total cost for any loan — home, car, personal or business — before you sign anything. Change the amount, rate or term and watch what each one really costs you. The numbers lenders quote monthly look very different yearly.",
"sections": [
("EMI, Explained Without the Jargon",
"""<p>EMI stands for Equated Monthly Installment: the fixed amount you pay a lender every month until a loan is cleared. Each payment is part interest, part principal (the amount you borrowed). Early payments are mostly interest; late payments are mostly principal — a split that shifts month by month, called amortization. The inputs are always the same three: how much you borrow, the annual interest rate, and the term in months. The output that matters most isn't the monthly figure, though — it's the <strong>total interest</strong>, the true price of borrowing, which never appears in the advertisements.</p>
<p>This calculator is deliberately currency-neutral: enter dollars, pounds, euros or rupees, and the math is identical. Use it for mortgages, auto loans, personal loans, student loans and business credit. Use it before you talk to a lender, while you compare two offers that both sound “affordable”, and whenever a salesperson tries to sell you a longer term as if it were a discount. It usually isn't — it's interest wearing a friendlier monthly costume.</p>"""),
("How to Use the EMI Calculator",
"""<ol>
<li>Enter the loan amount — what you'll actually borrow, after any down payment.</li>
<li>Enter the annual interest rate. Use the real APR from the offer if you have it, not a teaser rate.</li>
<li>Enter the term in months: 12 per year, so a 5-year loan is 60, a 30-year mortgage is 360.</li>
<li>Click “Calculate Payment” and study all four results: monthly payment, total interest, total repayment, and the interest share — the percentage of everything you pay that buys you nothing.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>Borrow <strong>$25,000 at 7.5% for 60 months</strong> (the defaults in the tool — a typical car loan). The monthly payment is <strong>$500.95</strong>. Sounds manageable — until you read the totals: you'll repay <strong>$30,057</strong>, meaning <strong>$5,057 of interest</strong> — an interest share of about 17% of everything you pay.</p>
<p>Now try the salesperson's suggestion: stretch to 84 months and the payment drops to about $383 — but total interest climbs to roughly <strong>$7,200</strong>. You “saved” $118 a month and paid about $2,150 extra for the privilege. Run the same loan at 36 months and interest falls to about $3,000. Same car, same rate — the term alone swings the cost by thousands. That's the experiment to run on every loan offer you ever receive.</p></div>"""),
("Tips for Borrowing Cheaper",
"""<ul>
<li><strong>Shorten the term before you shrink the payment.</strong> If you can afford the higher monthly figure, a shorter term is the single biggest interest saver.</li>
<li><strong>Compare total interest, not monthly payments.</strong> Monthly payment is the number lenders want you to judge by, because any loan can be made to look cheap by stretching it.</li>
<li><strong>A bigger down payment beats a rate discount.</strong> It reduces the principal from day one — every dollar not borrowed is a dollar never charged interest.</li>
<li><strong>Watch the rate's effect at mortgage scale.</strong> On a $300,000, 30-year loan, 6% costs about $347,500 in interest; 7% costs about $418,500. One percentage point: roughly $71,000. Negotiate accordingly.</li>
<li><strong>Check for prepayment penalties</strong> before planning extra payments — some loans charge you for the favor of paying early.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Entering years where months belong.</strong> This tool's term is in months. “30” means a 2.5-year loan, not a 30-year mortgage — that one is 360.</li>
<li><strong>Using the sticker price as the loan amount.</strong> Taxes, fees and add-ons often get financed too. Borrow the out-the-door number, and remember a down payment reduces it.</li>
<li><strong>Trusting a “0% APR” offer without reading further.</strong> Sometimes it's genuinely free credit; sometimes the price was raised to compensate, or a missed payment triggers backdated interest. The totals still tell the truth.</li>
<li><strong>Forgetting that fixed EMI ≠ fixed split.</strong> If you settle a loan early, you've already paid a disproportionate share of interest in the early months — another reason shorter terms protect you.</li>
</ul>"""),
],
"faqs": [
("What does EMI stand for?", "Equated Monthly Installment — the fixed monthly payment that clears a loan over an agreed term. The payment stays the same each month (on a fixed-rate loan), while the interest/principal split inside it gradually shifts from mostly interest to mostly principal."),
("How is the monthly payment calculated?", "With the standard amortization formula: EMI = P × r × (1+r)ⁿ ÷ ((1+r)ⁿ − 1), where P is the loan amount, r is the monthly interest rate (annual rate ÷ 12), and n is the number of monthly payments. This calculator runs it precisely and shows the totals it implies."),
("Does this work for mortgages and car loans in any currency?", "Yes. The mathematics of amortization is identical worldwide and currency-free. Enter amounts in dollars, pounds, euros, rupees or any other currency; just make sure the rate is the annual rate and the term is in months."),
("Why is so much of my early payment interest?", "Interest each month is charged on the outstanding balance, which is largest at the start. As the balance falls, the interest portion shrinks and more of your fixed payment attacks the principal. It's the design of amortized loans, not a trick — but it's why early settlement saves less than people expect."),
("What is the “interest share” figure?", "It's the percentage of your total repayment that is interest rather than principal. A 30-year mortgage at typical rates can have an interest share above 50% — you repay more in interest than you borrowed. Shorter terms push it down dramatically."),
("Can I use this for a loan with a variable rate?", "As a snapshot, yes — enter the current rate to see today's payment and totals. Just remember the real cost will drift as the rate resets, so treat the output as the “if nothing changes” scenario, not a guarantee."),
],
"related": [("percentage-calculator", "Percentage Calculator"), ("unit-converter", "Unit Converter"), ("bmi-calculator", "BMI Calculator")],
}

TOOLS["color-converter"] = {
"name": "Color Converter", "h1": "Color Converter — HEX, RGB & HSL",
"lead": "Pick any color — or type its HEX code — and instantly get the same color as HEX, RGB and HSL values, each with a one-click copy button. For designers matching a brand color, developers translating a mockup into CSS, and anyone who has ever asked “what color is #0E7C86, exactly?”",
"sections": [
("One Color, Three Languages",
"""<p>Screens don't care what you call a color; they mix light. But the tools of design and development describe that mixing in three different dialects, and work constantly forces translation between them. <strong>HEX</strong> (like #0E7C86) is the compact six-character code of web design — three pairs of hexadecimal numbers for red, green and blue. <strong>RGB</strong> states the same mix as ordinary numbers from 0 to 255: rgb(14, 124, 134). <strong>HSL</strong> re-describes it the way humans actually think — a hue around the color wheel (0–360°), saturation as a percentage, and lightness as a percentage: hsl(185, 81%, 29%).</p>
<p>Why keep all three? Because each is best at something. HEX is shortest for copying into code and brand guidelines. RGB is what most software, from image editors to CSS color pickers, displays natively. HSL is the one you can actually <em>reason</em> with: need a darker version of a color? Drop the lightness. A muted one? Lower the saturation. Try doing that in HEX, where every change is hexadecimal guesswork. This converter shows all three side by side, updates as you pick, accepts a typed HEX when you already have one, and copies any value with a single click.</p>"""),
("How to Use the Color Converter",
"""<ol>
<li>Use the color picker to choose a color visually — or type a HEX code into the field if you already know it.</li>
<li>Watch the large swatch: that's your color, full-size, the way it will actually appear.</li>
<li>Read the same color expressed as HEX, RGB and HSL in the panels below.</li>
<li>Click Copy next to the format you need and paste it straight into your CSS, design tool or document.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>The classic reference color: pure red. In HEX it's <strong>#FF0000</strong>. In RGB it's <strong>rgb(255, 0, 0)</strong> — maximum red, no green, no blue. In HSL it's <strong>hsl(0, 100%, 50%)</strong>: hue 0 (red sits at the top of the wheel), full saturation, and halfway lightness.</p>
<p>Now use HSL's superpower. Keep hue 0 and saturation 100%, drop lightness to 25% and you've designed maroon. Raise lightness to 75% and you get a soft pastel pink-red. Same hue family, three coordinated colors — the practical way designers build palettes, and it took ten seconds because HSL separates “which color” from “how strong” and “how light”.</p></div>"""),
("When to Use Each Format",
"""<ul>
<li><strong>HEX:</strong> CSS, design handoffs, brand guidelines, anywhere brevity wins. Add two more digits (like #0E7C86CC) and it carries transparency too — that's the alpha channel, 0–255 written in hex.</li>
<li><strong>RGB / RGBA:</strong> when you need transparency in CSS (rgba(14, 124, 134, 0.5)), when matching values shown in photo editors, or when a tool asks for the three channels separately.</li>
<li><strong>HSL / HSLA:</strong> building hover states, shades and tints (adjust lightness ±10%), accessible variants, and design systems where a whole palette derives from one hue.</li>
<li><strong>Named colors</strong> (“teal”, “crimson”): fine in conversation, unreliable in production. Always pin the actual code — one person's teal is another's turquoise.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Guessing a color from a screenshot.</strong> Compression and screen settings shift values. A color that “looks like” #0E7C86 may really be #12767E — close on screen, visibly off when placed side by side in a design. Always convert from the source value.</li>
<li><strong>Forgetting that HEX pairs are hexadecimal.</strong> The “86” in #0E7C86 is 134 in decimal, not 86. That's exactly the conversion the RGB panel exists to do for you.</li>
<li><strong>Designing shades by random tweaking.</strong> Random darker colors drift in hue and look muddy. Adjust lightness in HSL and the family resemblance is guaranteed.</li>
<li><strong>Ignoring contrast.</strong> A beautiful color can be unreadable text on the wrong background. Light pastel text on white fails accessibility guidelines — check important text/background pairs against WCAG contrast ratios (4.5:1 for body text).</li>
</ul>"""),
],
"faqs": [
("How do HEX codes work?", "A HEX code is three numbers written in base 16, one per channel: red, green, blue. Each pair runs 00 (none) to FF (full, 255 in decimal). #FF0000 is full red; #000000 is black; #FFFFFF is white. A leading # marks it as a color code."),
("What is the difference between RGB and HSL?", "RGB describes a color as amounts of red, green and blue light. HSL describes the same color by hue (position on the color wheel), saturation (intensity) and lightness. They're two coordinate systems for the identical color — this page converts between them losslessly."),
("How do I make a color darker or lighter?", "Convert it to HSL and change only the lightness: lower for darker, higher for lighter, keeping hue and saturation fixed. It's the reliable way to create matching shades and hover states without the color turning muddy."),
("What does the A in RGBA or HSLA mean?", "Alpha — transparency. It runs from 0 (fully transparent) to 1 (fully opaque) in RGBA/HSLA, or 00–FF as an extra pair in 8-digit HEX. A shadow or overlay color is usually a semi-transparent black, like rgba(0, 0, 0, 0.25)."),
("Can I enter a color I found as RGB and get its HEX?", "Yes — the panels stay in sync. Adjust via the picker or the HEX field and all three formats update together; there's always a copy button for the one your destination needs."),
("Why does my color look different on another screen?", "Screens vary in calibration, brightness and color gamut, and some colors in the HEX/RGB space sit outside what a given display can reproduce. The code is the ground truth; the rendering is an approximation. For brand-critical work, check on a calibrated monitor."),
],
"related": [("image-compressor", "Image Compressor"), ("qr-code-generator", "QR Code Generator"), ("base64-encoder-decoder", "Base64 Encoder / Decoder")],
}

TOOLS["remove-duplicate-lines"] = {
"name": "Remove Duplicate Lines", "h1": "Remove Duplicate Lines",
"lead": "Paste any list and strip out the repeated lines in one click — with options to sort A–Z, ignore letter case, trim stray spaces and drop blank lines. Mailing lists, keyword lists, inventories, invite lists: if it's one item per line, this cleans it.",
"sections": [
("The Two-Minute Job That Eats an Afternoon by Hand",
"""<p>Duplicates creep into every list that more than one person — or one person, twice — has touched. Two exports merged. Sign-ups collected from a form and a spreadsheet. Keywords gathered from three tools. Products typed by hand over months. The result is a list where “Acme Corp”, “acme corp” and “Acme Corp ” (with a trailing space, invisible and infuriating) are three separate lines, and any system importing the list treats them as three different entries. Finding duplicates by eye works for twenty lines. For two thousand, it's this tool.</p>
<p>Paste the list, choose your rules, click once. <strong>Sort A→Z</strong> gives you a tidy alphabetical result. <strong>Ignore case</strong> treats “Apple” and “apple” as the same entry. <strong>Trim spaces</strong> removes leading and trailing whitespace — the silent cause of most “but I deleted that duplicate!” arguments. <strong>Remove blank lines</strong> clears the gaps. The counters show lines before, unique lines after, and exactly how many duplicates were removed, so you can verify the cleanup before you trust it — all processed in your browser, so even a customer list never leaves your machine.</p>"""),
("How to Use the Duplicate Line Remover",
"""<ol>
<li>Paste your list into the input box — one item per line. Spreadsheet columns paste in perfectly, one row per line.</li>
<li>Tick your options. For most real-world lists, “Trim spaces” and “Remove blank lines” should be on; add “Ignore case” for names, emails and tags.</li>
<li>Click “Remove Duplicates” and check the counters: lines before, unique lines, duplicates removed.</li>
<li>Copy the clean list from the output box and paste it back where it belongs.</li>
</ol>"""),
("A Worked Example",
"""<div class="example"><p>A small shop merges two staff-collected lists of customer phone numbers for a WhatsApp broadcast: <strong>1,240 lines</strong> total. With trim spaces and blank lines removed, the tool reports <strong>861 unique lines and 379 duplicates removed</strong> — nearly a third of the list was repeats, including the same number pasted by both staff members and a few numbers with spaces copied from the contacts app.</p>
<p>The payoff isn't just tidiness. Sending the broadcast from the cleaned list means no customer gets the same promotional message three times in a minute — the kind of thing that gets a number blocked. And when the shop's owner glanced through the sorted output, two numbers with transposed digits stood out as obvious typos. Sorted, deduped lists are simply easier to trust.</p></div>"""),
("Which Options Should You Choose?",
"""<ul>
<li><strong>Email and username lists:</strong> turn ON Trim spaces + Ignore case. Addresses are case-insensitive in practice, and pasted ones always carry stray spaces.</li>
<li><strong>Passwords, codes, SKUs, and IDs:</strong> leave Ignore case OFF. “AB12” and “ab12” may genuinely be different items, and case is the only thing distinguishing them.</li>
<li><strong>Keyword and tag lists:</strong> Ignore case ON, Sort ON — you'll spot near-duplicates (“running shoe” vs “running shoes”) while scanning the sorted result, even though no tool can merge those automatically.</li>
<li><strong>Code and config lines:</strong> be careful — sometimes a repeated line is meaningful (firewall rules, cron entries). Dedupe a copy, compare the counts, and think before replacing the original.</li>
</ul>"""),
("Common Mistakes to Avoid",
"""<ul>
<li><strong>Deduping without trimming first.</strong> “item” and “item ” (trailing space) are different lines to a computer. If your duplicate count comes back suspiciously low, you forgot the Trim spaces option.</li>
<li><strong>Assuming ignore-case is always safe.</strong> For names and emails, yes. For anything case-sensitive — codes, case-sensitive IDs, programming text — it can merge things that were never the same.</li>
<li><strong>Overwriting your only copy.</strong> Clean into the output box, verify the counts make sense, then replace. Keep the messy original until the clean list is confirmed in its new home.</li>
<li><strong>Expecting it to catch near-duplicates.</strong> “Jon Smith” and “John Smith” are different lines, and no deduplication rule will merge them. The sorted output is your friend here — adjacent near-matches are easy to eyeball.</li>
</ul>"""),
],
"faqs": [
("How does the tool decide two lines are duplicates?", "It compares lines exactly as written — after applying the options you chose. With Trim spaces on, “ apple ” becomes “apple” before comparing. With Ignore case on, “Apple” and “apple” compare as equal. The first occurrence is kept (or its position in the sorted output), and later repeats are removed."),
("Does sorting happen before or after deduping?", "Either way you get the same unique set — sorting is about how the output is presented. Sorted output is easier to scan for near-duplicates and typos, which is why most people leave it on."),
("Can I remove duplicate lines from a really long list?", "Yes. Because processing happens in your browser, lists of hundreds of thousands of lines are handled in moments on a typical computer. There's no upload, so the list can be as private as you need."),
("Will it remove blank lines in the middle of my list?", "If you tick “Remove blank lines”, yes — empty lines and lines containing only spaces are dropped from the output. Leave it unticked if blank lines are meaningful separators in your data."),
("Is my data stored anywhere?", "No. The list is processed locally in your browser and disappears when you close the tab — safe for customer data, email lists and anything else you'd never paste into a server-side tool."),
("What if I want to keep duplicates but see them?", "Run the tool on a copy of your list and compare the counters: “Lines before” minus “Unique lines” tells you exactly how many repeats exist, and sorting both versions side by side shows you where they cluster — then dedupe the real list when you're ready."),
],
"related": [("case-converter", "Case Converter"), ("word-counter", "Word Counter"), ("json-formatter", "JSON Formatter")],
}

if __name__ == "__main__":
    import shutil
    backup = "/tmp/toolnova-v1-backup"
    os.makedirs(backup, exist_ok=True)
    for slug, data in TOOLS.items():
        src = os.path.join(BASE, slug, "index.html")
        dst = os.path.join(backup, slug + ".html")
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        ex = extract(src)
        if slug == "color-converter":
            for k in ("toolbox", "scripts"):
                ex[k] = ex[k].replace("#7c5cff", "#0e7c86").replace("#7C5CFF", "#0E7C86")
        build_page(slug, data, ex)
    print("done:", len(TOOLS), "pages")
