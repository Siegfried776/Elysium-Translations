# Changelog

## 1.1 — 2026-11-08

- Made for game v1.21 (BOOTH). v1.21 ships EasyRPG Player and the RPG Maker 2000 RTP, so the installer no longer swaps the runtime or downloads anything; the zip shrinks from 12.7 MB to 3.6 MB.
- The creator's own corrections to the English images (text aligned with the menu cursor, touching letters separated, frame shading restored, a clearer title subtitle), used exactly as made. The same letter-spacing fix applied to the remaining 24 images that needed it.
- v1.21's new and changed lines translated: herb pickups show their heal amount, a new traveler line, the official notice for Elliot's heal.
- The Elliot heal this patch added in 1.0 is now part of the game, so the patch no longer adds it.
- Manual: follows the game's v1.21 manual (now `manual.htm` in the game folder, new tip on the Swiftfoot Leaf for boss fights, new pictures).
- Installer: computes file hashes with .NET directly (works where PowerShell's Get-FileHash can't load).

## 1.0.1 — 2026-10-26

- Manual (`data\manual.htm`): English edited to match the game's translation (natural wording, one tense, no passive phrasing). The game itself is unchanged.
- Installer: installing over an earlier version no longer keeps files that version added as "originals", so Uninstall still restores the game exactly. Installing 1.0.1 over 1.0 is safe.

## 1.0 — 2026-10-25

- First release: complete English translation of LostMaria -名もなき花- v1.20 (BOOTH): script, database, menus, about 550 images and the manual.
- Runs on EasyRPG Player 0.8.1.1, installed in place of the original runtime so `start.exe` works.
- Ark Pixel 12 px proportional font, with message boxes fitted to it.
- Installer fetches the official RPG Maker 2000 RTP sounds from KADOKAWA when they're missing.
- Photosensitivity, UI-sound and softlock changes (listed in the README).
