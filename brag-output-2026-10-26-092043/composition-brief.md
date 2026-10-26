# Hyperframes Composition Brief: Incident Desk

## Objective
Create a short, polished launch video for the AI Incident Resolution Platform, presented in the project UI as Incident Desk.

## Output
- Composition directory: `brag-output-2026-10-26-092043/composition/`
- Rendered video: `brag-output-2026-10-26-092043/brag.mp4`
- Format: vertical — 1080x1920
- Duration: 20 seconds

## Source Material
- Project root: repository root
- Primary files read: `README.md`, `ui/streamlit_app.py`, `app/api/routes.py`, `app/schemas/incident.py`
- Product name: Incident Desk / AI Incident Resolution Platform
- Tagline / strongest claim: “Turn incidents into understanding.”
- Key UI or visual moment to recreate: the Streamlit incident intake card, sample Payment API incident, analyze action, and analysis overview.
- Copy that must appear verbatim:
  - “Payment API timeouts after deployment”
  - “Triage”
  - “Investigate”
  - “Recommend”
  - “Turn incidents into understanding.”
  - “Recommendations for engineer review—not autonomous repair.”
- The sample result is illustrative per the README. Keep “ILLUSTRATIVE EXAMPLE” visible alongside its values and preserve “Possible” in the root-cause line.

## Creative Direction
- Tone preset: polished
- Creative direction: quiet premium product film for an SRE tool
- Interpretation: restrained, readable, and human-centered; animate the real user flow without implying a production integration or autonomous repair.
- Angle: A polished, human-centered incident-response mini-film takes the app’s documented Payment API sample from intake through its real Triage / Investigate / Recommend workflow to an explicitly illustrative result.
- Hook: “Payment API timeouts after deployment” appears as a sample incident card.
- Outro / punchline: The Incident Desk mark lands with “Turn incidents into understanding.” and an engineer-review caveat.
- Avoid:
  - Generic SaaS language or unsupported performance claims
  - Abstract filler visuals or unrelated redesigns
  - Showing credentials, personal data, or live operational systems
  - Presenting illustrative sample output as a real diagnosis

## Visual Identity
- Background: `#f3f5fb` and the UI’s lavender/aqua radial gradients
- Text: `#18233b`
- Accent: `#7867f7`, secondary `#6889ff`
- Display font: Inter, system sans-serif fallback
- Body font: Inter, system sans-serif fallback
- Visual references from the project: glass incident form, dark navy/violet analyst card, violet mark, workflow chips, severity/domain/confidence metrics.

## Storyboard
Use `brag-plan.md` as the creative contract.

1. Payment incident — 3s — sample incident card and title.
2. Start the investigation — 4s — real intake UI, sample details, simulated analyze click.
3. Three-part workflow — 4s — Triage, Investigate, Recommend reveal and hold.
4. Illustrative analysis — 5s — clearly labeled example metrics, possible root cause, and next step.
5. Engineer in control — 4s — real tagline and human-review boundary.

## Audio
- Audio role: warm upbeat bed with sparse professional accents.
- Audio arc: low opening, gently builds through the workflow, fades under the closing line.
- Music: `happy-beats-business-moves-vol-1-by-ende-dot-app.mp3`
- Music treatment: low and supportive; use the bundled cue preset only as optional timing guidance.
- Music cue guidance: `../.agents/skills/brag/assets/music/cues/happy-beats-business-moves-vol-1-by-ende-dot-app.music-cues.json`; estimated 120.19 BPM, with workflow beat-grid points around 7.02–8.02s and an optional outro cue near 17.02s.
- Audio-reactive treatment: subtle movement in the existing violet halo only; no waveform or generic visualizer.
- Audio-coupled moments:
  - Analyze button — one quiet click.
  - Workflow cards — short sequence, at most two soft accents.
  - Final mark — one restrained landing.
- SFX selection guidance: choose low high-frequency-risk sounds that match UI taps and soft card arrivals.
- SFX analysis guidance: `../.agents/skills/brag/assets/sfx/sfx-analysis.md`
- Audio files: copy selected assets into `composition/assets/`; retain the track’s CC BY 4.0 attribution.

## Hyperframes Instructions
Use the current Hyperframes composition conventions and its `check` gate. Keep all creation and rendering local. Run the render with one worker to reduce memory pressure. Do not publish the composition through Hyperframes cloud.
