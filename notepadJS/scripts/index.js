const fs = require('fs')
const path = require('path')

const { readTitles } = require(path.resolve('actions/uiActions')) 
readTitles('./data').map(({title,dir}) => {
    let el = document.createElement("li")
    let text = document.createTextNode(`${title.split('.md')[0]}`); 
    el.appendChild(text)
    el.addEventListener('click', function(e) {
        fs.readFile(dir, (err, data) => {
            if(err) throw err; 
            // let fileDir = dir; 
            document.getElementById('content').innerHTML = data; 
        }); 
    })
    document.getElementById('titles').appendChild(el)
}) 