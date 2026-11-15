# Architecture and contributor guide

`main.py` creates one Ursina application and one Game controller. `core/game.py` owns navigation and binds player actions to a `systems.mission.Mission`. It does not perform orbital calculations itself.

| Module | Responsibility |
| --- | --- |
| `systems/engineering.py` | JSON catalog, totals, rocket equation, capture, period, validation |
| `systems/mission.py` | Deterministic phase transitions, resources, science, events, score |
| `core/save_manager.py` | Atomic JSON write, schema/range validation, settings defaults |
| `core/game.py` | Screen composition, UI callbacks, autosave, results/history |
| `objects/spacecraft.py` | Original modular orbiter geometry |
| `objects/world.py` | Planets, starfield, orbital visuals, camera modes and effects |
| `ui/widgets.py` | Consistent labels, panels, buttons and resource bars |
| `audio/manager.py` | Safe cached audio playback and volume settings |
| `data/*.json` | Editable component, mission and target definitions |
| `tools/make_assets.py` | Reproducible original textures/audio |
| `tools/make_data.py` | Catalog authoring script; intentionally overwrites the three JSON catalogs |
| `tools/graphical_smoke.py` | Offscreen screenshots plus UI callback smoke run |
| `tests/test_mission.py` | Rendering-independent regression and full-flight scenarios |

Physics advances in substeps of at most 0.1 real simulation seconds. Model calls cap externally supplied elapsed time at one second; the app caps large frame stalls to avoid a large resource jump. 1x/4x/12x are model multipliers. Pause freezes simulation and scene animation. Numeric UI refresh is throttled to avoid rebuilding labels each rendered frame.

Mission design is copied at launch. Redesigning cannot retroactively alter an in-progress craft. Result records retain their design and route snapshots; the compare screen shows score, success and cost. Saves include the entire live model, settings and up to ten completed results.

Extending the game: add options to the catalogs, then update totals/visuals if the option introduces a new property. Never put operational rules only in a button callback; keep them in `systems/` and test them without importing Ursina. The visual layer must not award extra science or fuel.

Do not regenerate assets/data casually after teammates edit them. Pull before work, use feature branches, and keep `.venv` out of version control. No remote repository changes were made while preparing this source delivery.
