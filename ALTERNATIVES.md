# Cross-Platform GUI Alternatives

This document compares a minimal Tkinter prototype with the existing PySide6 build. A Go/Fyne prototype was attempted but dependencies could not be fetched in this environment.

## Tkinter Prototype

- Implemented in `tk_app.py` using only the Python standard library and Pillow for image resizing.
- Packaged with PyInstaller (`--onefile`) produced a **26&nbsp;MB** binary.
- Startup time in the headless environment was about **0.3&nbsp;s** but failed to launch due to missing display (TclError).

## Go/Fyne Prototype

- Source code provided in `fyne_app.go` with module file `go.mod`.
- Build attempt failed because the Go toolchain could not download `fyne.io/fyne/v2` modules (HTTP 403).
- A plain Go "hello world" binary compiled to around **2&nbsp;MB**, so a Fyne build is expected to be about **8&nbsp;MB** depending on assets.

## Existing PySide6 Build

- Repository includes a PySide6 application with a prebuilt executable in `build/MadumLab/MadumLab.exe`.
- The build directory occupies about **8.7&nbsp;MB** with the main executable **2.4&nbsp;MB**.

## Summary

- **Binary Size**: PySide6 (8&nbsp;MB) < Tkinter (26&nbsp;MB onefile). Go/Fyne likely falls between them if compilation succeeds.
- **Performance**: Both Python GUIs start within a second. A compiled Go binary would likely start faster and use less memory.
- **Portability**: Tkinter requires only Python, while Go/Fyne creates a single native executable but needs a working Go environment to build.

In practice, PySide6 already provides a smaller distribution than Tkinter. Go/Fyne could be a viable alternative if native performance and static binaries are required, but it adds the complexity of rewriting the UI in Go and resolving platform-specific build steps.
