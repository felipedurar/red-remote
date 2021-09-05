
REM Build the Red Client Viewer
npm run --prefix client_viewer build
rd /s /q "dist"
electron-packager client_viewer RedRemote --platform=win32 --arch=x64 --out=dist/viewer --app-version=0.0.1 --icon=images/temporary-logo.ico
mv dist/win/RedRemote-win32-x64 dist/win
