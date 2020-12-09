const {app, Menu} = require('electron')
const { NEW_DOCUMENTS_NEEDED } = require('../actions/types')

module.exports = function(win) {
    return Menu.buildFromTemplate([
        {
            label: app.getName(), 
            submenu: [
                { label: `Hello`, click: () => console.log("Hello world")}
            ]
        }, 
        {
            label: 'Edit', 
            submenu: [
                {label: 'Undo', role: 'undo' }, 
                {label: 'Redo', role: 'redo' }, 
                {label: 'Cut', role: 'cut'},
                {label: 'Copy', role:'copy' }, 
                {label: 'Paste', role: 'paste'}, 
            ]
        }, 
        {
            label: 'Custom Menu', 
            submenu: [/*TODO*/]
        }
    ])
}