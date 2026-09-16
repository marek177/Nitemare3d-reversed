# SDL3

Install SDL3 through your package manager (recommended) or configure with
`-DN3D_FETCH_SDL3=ON` to let CMake fetch SDL3.

On Windows with vcpkg:

```powershell
vcpkg install sdl3:x64-windows
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
```
