import { sendJson, download } from "./functions.js"

const api_port = 5001

fetch(`http://localhost:${api_port}/api/tables`).then(res => res.json()).then(tables => {
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

    sendJson(json, api_port).then(data => {
        for (const [key, value] of Object.entries(data)) {
            download(key, value);
        }
    })
})