# Changelog

## 1.0 — 2026-10-05

- First release: the whole script retranslated from the Traditional Chinese, covering all story dialogue, side scenes, village NPCs, tips and shop scenes.
- Retranslated non-dialogue text: quest log, items and gear, skills, map and area names, menus, loading hints and speaker name plates.
- Line breaks fitted to the dialogue box using the game's own font (including scenes that enlarge the text), so text no longer wraps on its own and strands a word on a new line. Breaks fall at sentence ends, commas and phrase boundaries.
- Ellipses cut from about 1,580 to 600, and tildes from 1,000 to 170. Both are kept only where they do real work (trailing off, pregnant pauses and halting speech; teasing, sing-song and drawn-out delivery). Stacked "!!" and "!!!" are down from 260 to 11.
- Quest log: no more "~~", and ellipses use "..." because the quest window's font draws "…" as raised dots.
- Interjections follow their meaning: "Mhm" for yes, "Hmm" for thinking, "Mm" for a soft acknowledgment.
- UI letter spacing made for Chinese characters is tightened for English: area titles and region names (map banner and death screen), equipment names (no more "Uzato Azure Warrio"), and equipment descriptions (no longer squeezed). The equipment submenu says "Clothing".
- Loading-screen tips re-broken to fit the tip screen.
- Location names revised against the Chinese: Tazanaheim (Zero 2's spelling, was Tazarra Mun), Serpent's Hideaway, Red Cypress Path, Rite Passage, Forgotten Hall Path, Inner Sanctum, Rotmire, Mistshadow Valley, Toxic Marshlands, Toxic Spring Cave, Bramble Path.
- Checked with a full play-through.
- Speaker name plates no longer have a space between every letter ("O l e g o n" → "Olegon").
- The game starts in fullscreen (a two-byte change in Assembly-CSharp.dll). Alt+Enter still toggles.
- The three volume sliders default to 70% instead of maximum.
- Controller stick dead zone raised from 0.25 to 0.5, so a sideways push no longer registers as Up (interact).
- Data fixes: a nonexistent item drop (enemy 230005), and a tip scene that never triggered (quest 95022 map ID typo).
