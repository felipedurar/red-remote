const { app, BrowserWindow, Menu } = require('electron')
const url = require("url");
const path = require("path");

let mainWindow

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        //autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true
        }
    })

    mainWindow.loadURL(
        url.format({
            pathname: path.join(__dirname, `/dist/index.html`),
            protocol: "file:",
            slashes: true
        })
    );
    // Open the DevTools.
    //mainWindow.webContents.openDevTools()

    var menu = Menu.buildFromTemplate([
        {
            label: 'File',
            submenu: [
                {label:'File Management'},
                {label:'Clipboard Management'},
                {label:'Exit'}
            ]
        },
        {
            label: 'Input',
            submenu: [
                {label:'Show On Screen Keyboard'},
            ]
        },
        {
            label: 'View',
            submenu: [
                {label:'Full Screen'},
                {label:'Take Screenshoot'},
            ]
        },
        {
            label: 'Help',
            submenu: [
                {label:'About'}
            ]
        }
    ])
    Menu.setApplicationMenu(menu); 

    mainWindow.on('closed', function () {
        mainWindow = null
    })
}

app.on('ready', createWindow)

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
    if (mainWindow === null) createWindow()
})