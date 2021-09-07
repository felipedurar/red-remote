
runas /user:Administrator cmd

REM Build the Red Client Viewer
cd client_viewer
ng build --base-href ./ 
cd ..
REM npm run --prefix client_viewer build

rmdir dist /s /q
electron-packager client_viewer RedRemote --platform=win32 --arch=x64 --out=dist/viewer --app-version=0.0.1 --icon=images/temporary-logo.ico
mv dist/viewer/RedRemote-win32-x64 dist/win

PAUSE