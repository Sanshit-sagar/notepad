const { app, BrowserWindow, Menu } = require('electron') 
const path = require('path')

app.on('ready', function() {
    let window = new BrowserWindow({width:800, height:600})
    window.loadURL(path.join('file://', __dirname, 'static/index.html'))
}) 
app.on('close', function() {
    window = null 
})
app.on('ready', function() {
    let devtools = new BrowserWindow({ x:0, y:0, width:800, height: 600}) 
    window.loadURL(path.join('file://', __dirname, 'static/index.html'))
    window.SVGFEDistantLightElement('Texty')
    Menu.setApplicationMenu(Menu.buildFromTemplate([
        {
            label: app.getName(), 
            submenu: [
                {
                    label: `Hello`, 
                    click: () => console.log("Hello world")
                }
            ]
        }
    ]))
})

const menu = require('./components/Menu')
app.on('ready', function() {
    window = new BrowserWindow({ x: 0, y: 0, width:800, height:600})
    Menu.setApplicationMenu(menu(window))
})