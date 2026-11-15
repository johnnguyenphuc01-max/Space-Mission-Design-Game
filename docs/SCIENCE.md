# Science, assumptions and credits

## What comes from published sources

- Mars mean radius **3389.5 km**, gravitational parameter **42828 km³/s²**, and mean orbital distance **1.524 AU**: [NASA NSSDC Mars Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html). These constants drive the period, capture and solar calculations.
- `assets/textures/mars.jpg`: [NASA 3D Resources, Mars Image Texture](https://science.nasa.gov/3d-resources/mars/). Credit **NASA / Jet Propulsion Laboratory & Caltech**; Viking imagery processed at USGS. Downloaded November 15, 2026 from `https://assets.science.nasa.gov/content/dam/science/cds/3d/resources/image/mars/Mars.jpg` (972,896 bytes). Used as the sphere's surface image; no claim of survey-grade geographic registration of the game markers.
- Gale, Eberswalde, Holden and Mawrth Vallis science themes: [NASA, Four Finalist Landing Site Candidates for Mars Science Laboratory](https://science.nasa.gov/resource/four-finalist-landing-site-candidates-for-mars-science-laboratory/). They illustrate how orbital mapping informs landing-site assessment. Gale is a historical selected site; this game does not call all five unused future sites.
- Approximate candidate-region coordinates, rounded for the game: [PDS Geosciences Orbital Data Explorer](https://ode.rsl.wustl.edu/mars/pagehelp/Content/Missions_Instruments/Landing_Sites.htm). Gale uses the older candidate-region coordinate (-4.49, 137.42), not Curiosity's exact touchdown position. Jezero uses an approximate region position (18.38, 77.58), also used in the [USGS Astrogeology mosaic tutorial](https://stac.astrogeology.usgs.gov/docs/tutorials/mosaic_json/); markers identify regions, not precise image footprints.
- Mission engineering reference: supplied **NASA CubeSat 101** and the supplied mission-design papers. Used conceptually for subsystem trade-offs, integration and readiness reviews. Their CubeSat masses/launch prices are **not** transplanted into a Mars launch-capacity table.

NASA imagery is used for an educational computer simulation under [NASA Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/). NASA names identify sources only; logos and endorsement claims are absent. NASA/JPL content retains its attribution and is excluded from the project's original-asset license.

## Established formulas

All hardware masses are kg; power is W; battery storage is Wh; image data is decimal MB; communication rates are decimal Mb/s. Orbital calculations use km and seconds, converting resulting km/s to m/s.

- **Rocket equation:** `available_dv = g0 * Isp * ln(wet_mass / dry_mass)` with `g0 = 9.80665 m/s²`.
- **Capture:** hyperbolic periapsis speed is `sqrt(v_inf² + 2*mu/rp)`. Target ellipse speed is `sqrt(mu*(2/rp - 1/a))`. Their difference, times 1000, plus an explicit correction allowance, is charged to the spacecraft's delta-v budget.
- **Remaining fuel:** `wet_mass * exp(-required_dv/(g0*Isp)) - dry_mass`. Failed capture cannot magically leave the craft in orbit.
- **Orbit period:** `2*pi*sqrt(a³/mu)`; `a = Mars radius + (periapsis_altitude + apoapsis_altitude)/2`.
- **Hohmann reference:** `365.256/2 * ((1+1.524)/2)^1.5`, approximately 259 days for circular coplanar orbits. The game uses rounded, idealized excess speeds/C3 near this reference, not launch-date ephemerides.
- **Solar power:** rated 1-AU watts divided by `1.524²`; zero in the simplified eclipse interval.
- **Battery update:** `(generation - load)*elapsed_seconds/3600`, bounded between zero and capacity.
- **Downlink:** `Mbps / 8 * elapsed_seconds`, limited by data actually stored. Each region tracks collected and returned quantities separately.

Earth escape energy is delivered by the selected launch vehicle. The spacecraft's chemical fuel is reserved for Mars capture and the bundled correction allowance. No low-Earth-orbit payload number is represented as Mars-injection capacity.

## Explicit gameplay assumptions

All component names, masses, prices, storage values, specific impulses and performance figures in `components.json` are fictional educational choices. All Aster launchers are fictional, with a simplified capacity at their stated departure C3. Costs are **M credits**, not published NASA cost estimates.

- Dry spacecraft bus mass: 150 kg; base program cost: 18 M credits; idle bus load: 55 W.
- Transfer scenarios: Hohmann (259 days, C3 8.7, arrival excess 2.65 km/s); fast (210 days, 15, 3.4); off-window (300 days, 23, 4.2). The last two are illustrative energy budgets, not optimized trajectories.
- Three Mars orbits: 300×300, 600×600 and 400×8000 km. Elliptical imaging is abstracted to periapsis altitude; there is no continuous camera footprint integrator. The drawn orbit is schematic and uses exaggerated altitude; it is not a physical scale representation.
- Polar survey opportunities use deterministic phase offsets for five regions. They are not computed from longitude, latitude, spacecraft attitude or a physical ground track. Target coordinates ground the scientific labels and markers only.
- Eclipse occupies the last 35% of each orbit; Earth visibility occupies the first 52%. These are scheduled teaching windows, not Sun/Earth geometry or a Deep Space Network availability model.
- One real second of mapping is 60 simulated seconds; speed multipliers are 1, 4 and 12. Imaging integration takes 8–16 real seconds at 1x, further scaled by computer performance. The 24-hour operations contract is a demo deadline, not hardware lifetime.
- Each image adds `min(55, 40*(altitude/400)*min(1,15/resolution))` coverage points. This illustrates swath/resolution trade-offs; it is not area measured in km². Sharpness combines camera GSD and pointing blur in quadrature, then scales linearly with altitude.
- Dust blocks imaging of two regions during hours 2–5; no random failures or live weather feed. The orbiter's solar arrays are **not** falsely treated as covered by surface dust.
- The battery, thermal and science simulation begins in Mars mapping. Cruise and launch resources are pre-budgeted abstractions, not numerically propagated.
- The thermal model converts excess load beyond the chosen rejection capacity into a slow temperature rise and relaxes toward 18°C. Temperatures above 45°C reduce image yield; above 55°C degrade health. These thresholds/rates are gameplay values, not hardware specifications.
- When power is exhausted, the camera/radio shut down, but persistent idle shortage still damages health. Larger batteries delay the problem; sustainable generation matters.

## Scoring

`50 * mean(min(coverage/80,1)) + 30 * returned_fraction + 10 * capture_success + 10 * max(0,1-cost/260)`; round once to an integer. Coverage points are awarded per region, not image count. The displayed 80% criterion uses all collected image data. Low-cost failed missions may earn a few budget points, but are never marked successful.

The balanced design has 427 kg dry mass, 450 kg propellant, 877 kg wet mass and 2294 m/s available delta-v. Low mapping capture and corrections require about 2172 m/s, leaving roughly 16.66 kg propellant. Its total cost is 188 M credits.

## Original assets and third-party software

The spacecraft meshes, solar/foil textures, stylized Earth texture, starfield and PCM WAV sounds are generated by the supplied code. Earth artwork is **not** a NASA Earth dataset. The 24-second ambient loop is a new synthesized composition; no commercial music or external voice service is used. `tools/make_assets.py` regenerates these original assets with Pillow and Python's standard library. The NASA Mars texture is shipped separately and is not overwritten by that script.

Ursina: MIT. Panda3D: BSD-style license. panda3d-gltf and panda3d-simplepbr: BSD-3-Clause. Runtime installations retain their package licenses. Original project code and original assets: see `LICENSE`. No copied commercial spacecraft models, fonts or music. Ursina's installed default font and built-in primitives remain part of the dependency distribution.
