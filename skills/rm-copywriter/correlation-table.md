# The correlation table — data pattern ↔ framework family (FRFRMU-1061)

This is the ONE file that answers the founder's question: "we already have a
proven viral hook and these are frameworks — how do we correlate it?"

Three different things, three different jobs, one order of precedence:

1. **Pattern (DATA)** — the proven hook template / structure / CTA, with a
   receipt (`n`, spread, median) from the plan. A **CONSTRAINT**. The
   copywriter never swaps it.
2. **Framework (FROM-EXPERT)** — the book families below. A **GENERATOR**:
   how to fill the pattern's slots, produce variants, and explain WHY it
   works. A labelled fallback when data is thin.
3. **Substance (FIRST-PARTY)** — the Creator Brief's own words, facts,
   stories, offer. The **MATERIAL** — every noun, number and phrase.

**Precedence: data pattern > framework > the agent's own words.** A
framework never overrides a pattern that has a receipt; the agent's
vocabulary never overrides the audience's own words.

## The mechanical join

Every analysed hook the pipeline classifies carries a `hook_subcategory`
(`backend/app/services/taxonomy/labels.py`, `hook_subcategory` block) grouped
under a `hook_primary_category`. A plan's receipt names the subcategory it
proved works for this account. That subcategory is the lookup key below —
it tells the copywriter which framework families are LEGAL generators for
this slot, and which are not.

**A framework row applies to a subcategory ONLY if that subcategory appears
in the row's `applies_to` column.** Using a framework whose row does not list
the slot's subcategory is a pattern swap and fails
(`skills/rm-copywriter/tests/test_frfrmu1061_scaffold.py`,
`test_framework_outside_table_is_illegal`).

| framework_family | applies_to (hook_subcategory) | what it generates |
| --- | --- | --- |
| how_to | shortcut, transformation | numbered steps toward the promised outcome |
| n_ways_mistakes | open_loop, warning | a counted list of ways/mistakes; the count IS the open loop |
| warning_stop_doing | warning | a direct "stop doing X" / "don't do Y" beat |
| unlikely_character | results, twist | timing + unlikely subject + concrete result, in that order |
| result_minus_pain | transformation, shortcut | before → after, with the friction removed named explicitly |
| proven_method | credentials, transformation | authority statement + the transformation it produced |
| profitable_promise | shortcut, save_time, save_money | hurdle · prize · timing · eliminator (eliminator maps to `shared_struggle`, see below) |
| secret_telling | open_loop | insider-knowledge framing; NEVER the literal word "secret" (compliance) |
| us_vs_them | us_vs_them | group-identity framing, never a protected-class attack |
| myth_bust | myth_buster | states the myth, then the correction |
| story_open | story_open | opens mid-scene, not with an explanation |
| shared_struggle_bridge | shared_struggle, everyday_moment | names the shared problem before offering the fix (also the eliminator beat inside `profitable_promise`) |

Subcategories with **no row above** (`testimonial`, `numbers`, `comparison`,
`endorsement`, `deadline`, `hot_take`, `callout`, `humor`, `trend`, `shock`,
`you_are`, `other`) have no framework family assigned yet. The copywriter
writes directly from the pattern + brief substance for those, and notes the
gap — it never invents a framework family to fill the table.

## Reading a slot

If the plan's receipt says: *"this slot's hook subcategory is `open_loop`,
n=41, median 18k"* — the legal framework families are `n_ways_mistakes` and
`secret_telling`. Writing that slot with, say, `how_to` (legal only for
`shortcut`/`transformation`) is a pattern swap and fails.

Every line the copywriter writes cites the row it used:
`pattern_ref: {hook_subcategory, framework_family}`.
