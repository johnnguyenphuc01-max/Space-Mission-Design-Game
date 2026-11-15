# Windows application folder build

**Status:** reproducible build script supplied; Windows compilation and executable runtime are not verified in this Linux workspace. Use source execution for the first laptop test.

1. Extract the full source folder.
2. Run `START_GAME.bat` and confirm the default mission works.
3. Run `BUILD_WINDOWS.bat` (or `.venv\Scripts\python.exe tools\build_windows.py`).
4. PyInstaller 6.22.0 is installed into the virtual environment. It collects Ursina, Panda3D, `direct`, glTF/simplepbr resources, project JSON, textures, sounds and documentation.
5. Test `dist\MarsMissionArchitect\MarsMissionArchitect.exe`. A console is deliberately retained to expose startup errors.
6. Copy the **whole** `dist\MarsMissionArchitect` folder to a second Windows machine. Keep `_internal` beside the executable. Test again without relying on the development `.venv`.

The build script uses argument lists, so spaces in paths are supported. It stops on pip or packaging failures. It never force-pushes, uploads, signs, publishes or changes repository visibility.

Manual acceptance checklist: new game; change every component; blocked overbudget launch; default capture; all five targets; downlink; score; retry; save/exit/continue; mute and separate volumes; no audio device; fullscreen and 1280×720 window; clean source/packaged startup; target-laptop frame rate. The same checks should be repeated on the demonstration computer.

References: [Ursina deployment guidance](https://www.ursinaengine.org/building.html), [PyInstaller usage](https://pyinstaller.org/en/stable/usage.html). The installed Ursina 8.3.0 `build.py` differs from older website instructions and expects a particular nested project layout. This package uses the explicit PyInstaller script instead of relying on those older command examples.
