# Validation report — November 15, 2026

## Executed in this environment

Environment: Linux, Python 3.12.14, Ursina 8.3.0, Panda3D 1.10.16. Graphics: Panda3D headless OpenGL/EGL, with null audio. This is not the target Windows laptop.

**18 automated tests passed.** The suite covers:

- Hohmann time, Mars orbital period and capture delta-v reference ranges.
- Mass conservation, rocket equation and fuel/solar/camera trade-offs.
- Full default success, inadequate fuel, inadequate radio and power-shortage failure.
- Storage capacity, returned-data conservation, pause, speed and fixed-step equivalence.
- Launch C3/budget blockers and circular/elliptical orbit trade-offs.
- Save round-trip, resumed successful flight and malformed/out-of-range save rejection.
- Deterministic dust, eclipse and communication windows.
- All shipped texture decoding, nonempty valid PCM audio and catalog integrity.

**Graphical smoke and UI callback tests passed at 1280×720, 1920×1080 and 1024×768.** The test rendered menu, briefing, designer, planning, transfer diagram, review, guide, settings, credits, launch, departure, cruise, arrival, mapping, results, comparison and redesign. Screenshots of representative screens were visually inspected and are included in `docs/screenshots/`.

UI callbacks exercised Start → briefing → design → planning → transfer diagram → review → launch; every one of the 27 component choices; blocked review; pause/resume; speed; camera selection; save/menu/continue; end-confirmation cancellation; complete successful mission; result comparison; redesign; volume, mute, reduced motion and low graphics. Hover callbacks are invoked programmatically. This is not an OS-level mouse/keyboard or human usability test.

`compileall` also passed for the Python source. The test environment reported a pytest plugin deprecation warning unrelated to this project's logic. Headless runtime messages note the lack of physical monitors/input devices and default EGL display initialization; offscreen rendering subsequently completed using the available graphics path. No missing project assets or unhandled application exceptions remained in the final smoke logs.

## Reproducible outcomes

The `fly` helper in `tests/test_mission.py` is a deterministic test operator, not a player-facing autopilot. It switches targets, avoids the scheduled dust interval, arms imaging when storage permits and keeps downlink scheduled.

| Design | Outcome | Score | Operations time | Key result |
| --- | --- | --- | --- | --- |
| Default balanced | Success | 91 | 9.46 h | 90% coverage in every region, 93.37% data returned |
| Lean fuel tank | Capture failure | 3 | 0 h | Cannot pay capture delta-v |
| Low-gain radio | Deadline failure | 48 | 24.00 h | 2.42% returned; storage limits further observations |
| Compact solar + small battery + precision camera | Spacecraft lost | 43 | 5.39 h | Electrical shortage exhausts battery and health |

The successful design retains approximately 16.66 kg propellant after the capture/correction budget. Scores depend on operations; these are deterministic test results, not guaranteed player scores.

## Not verified here

- Native Windows 11 launch, actual audio playback/device loss, hardware input and fullscreen behavior.
- PyInstaller Windows compilation or running/distributing a generated `.exe`.
- Hardware GPU compatibility, memory profiling or a sustained 60 FPS target.
- Manual end-to-end play by a beginner, precise geographic registration or scientific flight accuracy.

The included Windows build recipe and manual acceptance checklist are the next validation step on the team's demonstration laptop. No standalone executable is claimed to have been built.
