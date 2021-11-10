fetch('../tables.json').then(res => res.json()).then(tables => {
    let html = ""
    let show = true
    tables.forEach(table => {
        html += '<div class="accordion-item">'
        html += `<h2 class="accordion-header" id="heading${table.NAME}">`
        html += `<button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${table.NAME}" aria-expanded="true" aria-controls="collapse${table.NAME}">
                    ${table.NAME}
                </button>`
        html += '</h2>'
        html += `<div id="collapse${table.NAME}" class="accordion-collapse collapse ${(show) ? 'show' : ''}" aria-labelledby="heading${table.NAME}" data-bs-parent="#accordionExample">`
        html += '<div class="accordion-body">'

        table.ELEMENTS.forEach(element => {
            html += `<div class="form-check">
            <input class="form-check-input" type="checkbox" value="${table.NAME};${element}">
            <label class="form-check-label">
            ${element}
            </label>
            </div>`
        })

        html += '</div></div></div>'
        show = false
    })

    document.getElementById('tables').innerHTML = html
})

async function sendJson(json) {
    const res = await fetch('http://localhost:8000/api/dump', {
        method: 'POST',
        headers: {"Content-type": "application/json; charset=UTF-8"},
        body: JSON.stringify(json)
    })
    const data = await res.json()
    return data
}

function download(filename, textInput) {
    var element = document.createElement('a');
    element.setAttribute('href','data:text/plain;charset=utf-8, ' + encodeURIComponent(textInput));
    element.setAttribute('download', filename);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

const form = document.getElementById('main')
form.addEventListener('submit', e => {
    e.preventDefault()
    let ckBoxes = document.getElementsByClassName('form-check-input')
    let projectId = document.getElementById('projectId').value
    let basis = document.getElementById('basis').value
    let tableJson = {}
    let table
    let element
    for (let ck of ckBoxes) {
        if (ck.checked) {
            table = ck.value.split(';')[0]
            element = ck.value.split(';')[1]

            if (tableJson[table] == undefined) {
                tableJson[table] = [element]
            } else {
                tableJson[table].push(element)
            }
        }
    }

    let json = {
        PROJECT_ID: projectId,
        BASIS: basis,
        TABLES: tableJson
    }

    sendJson(json).then(data => {
        for (const [key, value] of Object.entries(data)) {
            download(key, value);
        }
    })
})