export async function sendJson(json, api_port) {
    const res = await fetch(`http://localhost:${api_port}/api/generate`, {
        method: 'POST',
        headers: {"Content-type": "application/json; charset=UTF-8"},
        body: JSON.stringify(json)
    })
    const data = await res.json()
    return data
}

export function download(filename, textInput) {
    let element = document.createElement('a');
    element.setAttribute('href','data:text/plain;charset=utf-8, ' + encodeURIComponent(textInput));
    element.setAttribute('download', filename);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}