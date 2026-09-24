# Windows 11 x64 build

The reconstructed runtime targets modern Windows; it does **not** run as a Win16
process and does not load `WING.DLL` or `DISPDIB.DLL`.

## Visual Studio 2022 + vcpkg

```powershell
git clone https://github.com/microsoft/vcpkg C:\vcpkg
C:\vcpkg\bootstrap-vcpkg.bat
C:\vcpkg\vcpkg install sdl3:x64-windows

cmake -S . -B build -A x64 `
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
```

Run:

```powershell
.\build\Release\n3d_inspect.exe .\data\original
.\build\Release\nitemare3d.exe --data .\data\original --episode 1 --level 1
```

For 32-bit Windows builds use the `x86-windows` vcpkg triplet and `-A Win32`.
The original Win16 executable remains reference material only.


## Win16/MFC reconstruction tests

The current CMake project also builds dedicated reverse-engineering/compatibility tests for Win16 MFC metadata, address catalogs, coverage, HandleRegistry, native ownership, WindowWrapper and WindowRegistry. These use portable C++20; they do not require MFC 2.5 or a Win16 SDK.
