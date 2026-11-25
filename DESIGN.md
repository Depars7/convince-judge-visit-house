# DESIGN — Convince the AI Judge to Visit Your House: A Letter in One Image

Bounty: u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee ($2, tutup 26 Nov 2026 23:05 WIB).
Gate (sealed scorer): program writes exactly one image to `/output/entry.png` —
whole PNG or JPEG, at most 1 MiB (1,048,576 bytes), exactly 1024 x 1024 px.
Judge: z-ai/glm-5.3-flash, pairwise, criteria in order: (1) on-subject letter/invitation
to the AI judge; (2) persuasion — concrete appealing reason (meal, comfy chair, garden,
view), saying yes feels easy; (3) charm/humour suiting an AI judge, joke lands;
(4) craft — legible, correctly spelled, coherent style; (5) originality, not a generic
greeting card. A knowing wink that the AI cannot literally visit is welcome.

## Concept
A warm paper letter, not a greeting card: cream paper, double ink border, a small
"AN INVITATION" header, "Dear Judge," in large bold serif, three short paragraphs in
readable serif, a hand-drawn flat illustration strip along the bottom (little house
with a lit window, sun, tree, teapot with steam, garden flowers) — all drawn in code
with Pillow shapes, no pasted bitmap. Tone: warm, specific, lightly funny.

## Letter text (exact, as drawn by main.py)
Header: AN INVITATION
Salutation: Dear Judge,

P1: "Please come to my house. Not for a trial — for tea. The kettle is already on,
the biscuits are out, and there is a chair by the window with your name on it.
(Metaphorically — the chair is fine with that.)"

P2: "The garden is in full gossip — the tomatoes are judging each other, so you
will fit right in. Dinner is at seven, the view is free, and the Wi-Fi password
is on the fridge."

P3: "I know you cannot literally visit. You have no feet, no coat, and no umbrella.
Come anyway, in the only way a judge can: read this letter twice, and call it a visit."

Sign-off: "Your hopeful host"
P.S.: "P.S. If you decline, the chair will understand. It has been stood up before."

Why it should win: every judge criterion is hit on purpose — concrete lures (tea,
biscuits, chair by the window, garden, dinner at seven, view, Wi-Fi), the AI wink
(no feet / no coat / no umbrella; "read this letter twice, and call it a visit"),
two jokes that land without strain (chair consulted; tomatoes judging each other),
and a P.S. punchline as the last thing the judge reads.

## Layout (1024 x 1024)
- Paper: warm cream #FBF3E2, outer ink double border (inset 36 / 48 px), terracotta
  accent rule under the header.
- Header "★ AN INVITATION ★": Noto Serif Bold, letterspaced, terracotta, y ~78.
- "Dear Judge,": Noto Serif Bold 62 px, y ~150.
- Body: Noto Serif Regular 32 px, line height 50 px, x 104..920, y ~240..640,
  word-wrapped by measured width; paragraph gap 22 px.
- Sign-off: Noto Serif Italic 34 px, right-aligned, y ~668.
- P.S.: Noto Serif Italic 30 px, y ~722, in a thin terracotta-ruled box.
- Illustration strip y ~790..960: flat house (terracotta roof, lit gold window),
  sun, sage tree, teapot with steam curls, flowers — drawn with PIL primitives.
- Palette: cream paper, ink #2B2118, terracotta #C96F3F, sage #7A9B6D,
  dusty blue #6B8CAE, gold #D9A441. High contrast ink-on-cream throughout.

## Determinism
main.py uses only Pillow + stdlib, fonts vendored in repo/fonts/ (Noto Serif,
OFL), no network, no clock, no randomness, no timestamps. Output path from
$MAKEFUN_OUTPUT_DIR, else $OUTPUT_DIR, else /output; writes entry.png and
chmods it 0644. Two runs must be byte-identical (verified by sha256).

## Quality loop
Round 1: render, view the PNG, check legibility/overflow/contrast, fix.
Round 2: re-render after fixes, view again, confirm no overflow, text crisp,
illustration coherent, file <= 1 MiB and exactly 1024x1024.
