# Brag Plan: Incident Desk

## What is this app?
Incident Desk turns an incident report into a first read on severity, likely cause, and possible next steps for an engineer to review.

## The angle
A polished, human-centered incident-response mini-film: take one familiar payment timeout, show the app turning a report into a structured investigation starting point, and make clear that the engineer remains in charge.

## Hook (first 2-3 seconds)
An incident card lands with the real sample title, “Payment API timeouts after deployment.” A restrained alert pulse makes the problem immediate without suggesting a live production connection.

## Key moments (the middle)
- The Incident Desk intake form receives the sample incident and the “Analyze incident” action is pressed.
- The product’s real three-part workflow—Triage, Investigate, Recommend—arrives in sequence.
- An explicitly illustrative result shows HIGH severity, Payments, 83% confidence, a possible connection-pool cause, and a proposed check.

## Outro / punchline
The analysis resolves into the real product line, “Turn incidents into understanding.” A small footer clarifies that recommendations are for engineer review, not autonomous repair.

## User flow worth showing
Choose the Payment API sample → analyze the incident report → review the severity, likely cause, and recommended next step.

## Tone
- Preset: polished
- Creative direction: quiet premium product film for an SRE tool
- Interpretation: confident pacing, generous holds, restrained motion, and a clear human-review boundary; no invented reliability or speed claims.

## Format: vertical — 1080x1920
## Duration: 20 seconds

## Visual identity (from the project)
- Background: `#f3f5fb` with the UI’s subtle lavender and aqua radial gradients
- Accent: `#7867f7`, with `#6889ff` as a secondary blue
- Text: `#18233b`
- Display font: Inter, falling back to system sans-serif
- Body font: Inter, falling back to system sans-serif
- Strongest visual element: the Incident Desk’s pale glass cards against its dark navy-to-violet hero treatment, plus the violet analyst mark.

## Share copy (draft)
Incident Desk turns an incident report into a clearer first read—severity, likely cause, and next steps for an engineer to review.

## Audio direction
- Role: warm, upbeat music bed with sparse professional accents
- Music: `happy-beats-business-moves-vol-1-by-ende-dot-app.mp3`
- Music treatment: quiet under the opening; gently lift through the workflow; fade under the final product line.
- Music cue guidance: bundled cue preset at `assets/music/cues/happy-beats-business-moves-vol-1-by-ende-dot-app.music-cues.md`, estimated 120.19 BPM. Keep the form action near 4.53s and the workflow sequence near the 7.02–8.02s beat grid; land the outro around the strong cue at 17.02s. Optional cues—readability takes priority.
- Audio-reactive treatment: subtle; let the existing violet halo breathe slightly with the music, with no waveform or strobing.
- SFX posture: sparse, low-volume, motion-matched UI taps and soft transitions.
- Audio-coupled moments: a quiet click on “Analyze incident”; the three short workflow labels reveal in sequence; one soft accent on the final mark.
- Restraint rule: keep the music and effects secondary to readable copy; no voiceover.

## Storyboard

### Scene 1 — Payment incident — 3s
An example incident card settles into the dark Incident Desk visual language: `INC-2048`, “Payment API timeouts after deployment,” and a small “SAMPLE INCIDENT” label. No live-system claims.
Sequential/interaction: none.
Audio intent: establish a calm, attentive tone.
Audio-coupled idea: soft opening swell only.
Music: warm upbeat bed at a restrained level.
Transition mood: soft slide → Scene 2

### Scene 2 — Start the investigation — 4s
Recreate the project’s intake card in its light glass UI. The sample title and symptoms appear in the form; a cursor presses “Analyze incident.” The button and label match the Streamlit UI.
Sequential/interaction: simulate selecting the Payment API sample and pressing the analyze button.
Audio intent: make the action feel deliberate and tactile.
Audio-coupled idea: a single quiet UI click, not per-character typing.
Music: continue, slightly lift after the action.
Transition mood: clean crossfade → Scene 3

### Scene 3 — Three-part workflow — 4s
Show the actual product workflow labels—Triage, Investigate, Recommend—as three clean cards. They arrive one by one, then remain together long enough to read.
Sequential/interaction: yes—three short labels appear in order, with a final hold.
Audio intent: signal forward progress without implying unattended remediation.
Audio-coupled idea: reveal the labels near consecutive beat-grid points around 7.02–8.02s; use at most two soft accents.
Music: continue at a steady level.
Transition mood: soft slide → Scene 4

### Scene 4 — Illustrative analysis — 5s
A result card is headed “ILLUSTRATIVE EXAMPLE.” It shows `HIGH`, `Payments`, `83% confidence`, “Possible database connection pool exhaustion,” and the proposed next step “Check payment service database connection-pool usage.” The use of “Possible” and the illustrative label stay visible.
Sequential/interaction: severity and domain arrive first; the hypothesis and next step follow and hold.
Audio intent: give the first read weight while avoiding a definitive-diagnosis tone.
Audio-coupled idea: one soft card landing; keep all result text static while readable.
Music: gently open up, never overpower the words.
Transition mood: soft crossfade → Scene 5

### Scene 5 — Engineer in control — 4s
The Incident Desk mark and “Turn incidents into understanding.” resolve over the project’s navy/violet gradient. Footer: “Recommendations for engineer review—not autonomous repair.”
Sequential/interaction: none.
Audio intent: finish warm and composed.
Audio-coupled idea: settle the product mark around the strong cue at 17.02s, then fade music out.
Music: fade under the closing line.
Transition mood: soft fade to end.

**Music mood for this video:** upbeat, restrained, professional.
**Audio summary:** A warm, low-key bed supports one sample incident, a concise workflow reveal, and a calm human-centered close, with only a few quiet UI accents.
