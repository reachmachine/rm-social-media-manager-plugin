> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 4.5**, after Step 4 (stage) and Step 1.6 (self-account data) — the
> identity chair below needs BOTH; recommending it earlier is a guess (dependency-audit
> correction, FRFRMU-1036). Completes p09 "Build the Attractive Character"
> (`marketing/rules/process-cards/p09-build-attractive-character.md`, FRFRMU-1043) — the
> QUESTION half already ran at `step-01-4-persona-questions.md`.

## Step 4.5 — The persona, assembly half (p09)

**Ask per `asking-rules.md`.**

### F4 — Identity: describe four chairs, recommend one, let them choose

Four honest sentences: **A · Leader** — "I've done it, follow me" (needs a checkable result).
**B · Adventurer** — "I'm figuring this out live." **C · Reporter** — "I collect what works
from people who've done it" (the honest newcomer chair). **D · Reluctant Hero** — "I'd rather
not be on camera, but this matters."

**Recommend FIRST**, from Step 4's stage + the first-party proof on file: no checkable result
→ Reporter or Adventurer; a result achieved → Leader; has the result but avoids camera →
Reluctant Hero. **A no-proof newcomer recommended as Leader is a defect.** Record the reason
and a **graduation condition** (e.g. "Reporter → Leader once 3 client results exist").

### F7 — Bio line: three drafts, one pick

Draft three variants = identity chair + audience + stance, each ≤150 characters, Gate-1 clean
(no guaranteed result), passing the 100-others test (a stranger could tell it from 100 other
bios). Creator picks or edits.

### Storyline ↔ structure map (idea from the cards; pattern from the tool)

Map each of six storyline templates to the structure/beats `get_content_structures` proves for
THIS niche, with `n`:

| Storyline | Structure/beats |
|---|---|
| Before & After | `transformation`; `story_setup → story_turn → transformation` |
| Loss & Redemption | same + `proof`; the identity/origin reel |
| Us vs Them | `myth_bust`/stance reels — an idea, never a group or a person |
| Amazing Discovery | `demo`/`teach_step` with a discovery hook |
| Secret-telling | curiosity-structured reels — **the word "secret" and hype never appear** |
| Third-person testimonial | `proof` beats — **a real, user-supplied result only** (S14); unavailable until the creator supplies one |

### Save it — completes `attractive_character`

Add to the same Creator Brief key from `step-01-4-persona-questions.md`:

```
{"item_id": "identity", "label": "Identity chair", "text": "<chair + reason + graduation>",
 "who": "you", "provenance": "FROM-EXPERT"},
{"item_id": "bio_line", "label": "Bio", "text": "<the picked line>", "who": "you",
 "provenance": "FROM-EXPERT"},
{"item_id": "storyline_map", "label": "Storyline -> structure", "text": "<the table, filled>",
 "who": "agent", "provenance": "DATA-INFERRED"}
```

Flip `status` to `confirmed` once F4 and F7 are both answered.

### What this step refuses to do

Recommend a chair before the stage/proof are known · recommend Leader for a no-proof newcomer
· a Secret-telling reel containing the word "secret" · a testimonial storyline with no real,
user-supplied result.

### Wired in (each does nothing when `attractive_character` is absent)

`step-08-hook-recipe.md` H.4b (voice descriptors, avoid-words, identity join the phrase-candidate
pool) · `step-08-outline-recipe.md` S.4 (voice pass) and S.3 (`story_setup`/`story_turn` draw
from `parables`, write back `used_in`) · `step-08-deliverable.md` Section 00 (a "Profile" bio
line) · `check_persona_consistency` (advisory validator — a reel that contradicts the stance or
claims a chair the creator hasn't earned is flagged).
