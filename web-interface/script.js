"use strict";

const EFJTOOL_URL = "https://yu3zknipfl.execute-api.eu-west-2.amazonaws.com/default/efj-tool";

let ID = x => document.getElementById(x);
let history = new Array;


function dragoverHandler(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "copy";
}


function dropHandler(ev) {
    ev.preventDefault();
    if (!ev.dataTransfer.items) return;
    for(const item of ev.dataTransfer.items) {
        if (item.kind === "file") {
            const file = item.getAsFile();
            load_file(file);
            break;
        }
    }
}


async function load_file(file) {
    if (file) {
        push_history(ID("output").value);
        const text = await file.text();
        ID("output").value = text;
    }
}


async function save_to_file(text, mimetype, suggested_name) {
    const file = new window.Blob([text], {type: mimetype});
    const a = document.createElement("a");
    const url = window.URL.createObjectURL(file);
    a.href = url;
    a.download = suggested_name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}


function show_error(text) {
    const sections = text.split(" : ");
    if(sections && sections[0] == "efj_parser") {
        ID("error_message").innerHTML =
            `<dl><dt>Line:</dt><dd>${sections[1]}</dd>
<dt>Message:</dt><dd>${sections[2]}</dd>
<dt>Text:</dt><dd><code>${sections[3]}</code></dd></dl>`;
    }
    else {
        ID("error_message").innerText = text;
    }
    ID("error_dialog").showModal();
}


async function process(action) {
    push_history(ID("output").value);
    let result = await post(ID("output").value, action, "");
    if(!result)
        return;
    if(result[1] == "success")
        ID("output").value = result[0];
    else
        show_error(result[0]);
}


function push_history() {
    history.push(ID("output").value);
    console.log(history);
}


async function save_output_to_file() {
    save_to_file(ID("output").value, "text/plain", "efj.txt");
}


async function copy_output_to_clipboard() {
    let cb = window.navigator.clipboard;
    await cb.writeText(ID("output").value);
    window.alert("eFJ copied to clipboard");
}


async function post(efj, action, config) {
    ID("working").classList.remove("hidden");
    let response;
    try {
        response = await fetch(EFJTOOL_URL, {
            method: "POST",
            body: JSON.stringify({
                "efj": efj,
                "action": action,
                "config": config
            }),
            cache: "no-cache"
        });
        ID("working").classList.add("hidden");
        if(!response.ok) {
            show_error(`HTTP error: ${response.status}`);
            return null;
        }
    } catch (error) {
        ID("working").classList.add("hidden");
        show_error("Network error");
        return null;
    }
    return await response.json();
}


async function get_fcl_logbook() {
    let config = window.localStorage.getItem("ini");
    let result = await post(ID("output").value, "logbook", config || "");
    if(!result)
        return;
    if(result[1] == "success") {
        save_to_file(result[0], "text/html", "fcl-logbook.html");
    }
    else if(result[1] == "config") {
        edit_config(result[0], true);
    }
    else
        show_error(result[0]);
}


const class_description = {
    "spse": "Single Pilot, Single Engine",
    "spme": "Single Pilot, Multi Engine",
    "mc": "Multi Crew"
};


function change_class_value() {
    switch(this.value) {
    case "spse":
        this.value = "spme";
        break;
    case "spme":
        this.value = "mc";
        break;
    case "mc":
        this.value = "spse";
    }
    this.textContent = class_description[this.value];
}


async function edit_config(ini, retry_logbook=false) {
    let lines = ini.split("\n");
    if(lines[0] != "[aircraft.classes]") {
        show_error("Bad ini");
        return;
    }
    let class_div = ID("aircraft_classes");
    class_div.innerHTML = "";
    let template = ID("class_selector");
    for(let class_str of lines.slice(1).sort()) {
        if(!class_str) continue;
        let fields = class_str.split(" = ");
        let clone = template.content.cloneNode(true);
        clone.querySelector(".aircraft_type").textContent =
            fields[0].toLocaleUpperCase();
        let button = clone.querySelector(".class_selector");
        button.value = fields[1];
        button.textContent = class_description[fields[1]];
        button.addEventListener("click", change_class_value);
        class_div.append(clone);
    }
    ID("config_dialog").retry_logbook = retry_logbook;
    ID("config_dialog").showModal();
}


async function save_config() {
    let ini = ["[aircraft.classes]"];
    let rows = ID("aircraft_classes").querySelectorAll("tr");
    for(let row of rows) {
        let type = row.querySelector(".aircraft_type").textContent;
        let class_ = row.querySelector(".class_selector").value;
        ini.push(`${type} = ${class_}`);
    }
    window.localStorage.setItem("ini", ini.join("\n"));
    ID("config").classList.remove("hidden");
    if(ID("config_dialog").retry_logbook) {
        ID("config_dialog").retry_logbook = false;
        get_fcl_logbook();
    }
    ID("config_dialog").close();;
}


async function get_summary() {
    let result = await post(ID("output").value, "summary", "");
    if(!result)
        return;
    if(result[1] == "success")
        save_to_file(result[0], "text/html", "summary.html");
    else
        show_error(result[0]);
}


function main() {
    const input = ID("input");
    if(!window.localStorage.getItem("ini"))
        ID("config").classList.add("hidden");
    input.addEventListener(
        "change",
        async () => { if(input.files.length == 1) load_file(input.files[0]);});
    input.addEventListener(
        "click",
        function () {this.value = null;});
    ID("load_efj").addEventListener(
        "click",
        () => {ID("output").value = ""; input.click();});
    ID("clear").addEventListener(
        "click",
        () => {push_history(ID("output").value); ID("output").value = "";});
    ID("back").addEventListener(
        "click",
        () => {console.log(history); if(history.length) ID("output").value = history.pop();});
    ID("save").addEventListener(
        "click",
        () => save_output_to_file());
    ID("copy").addEventListener(
        "click",
        () => copy_output_to_clipboard());
    ID("config").addEventListener(
        "click",
        () => {
            edit_config(window.localStorage.getItem("ini"), false);
        });
    ID("expand").addEventListener(
        "click",
        () => process("expand"));
    ID("night").addEventListener(
        "click",
        () => process("night"));
    ID("vfr").addEventListener(
        "click",
        () => process("vfr"));
    ID("ins").addEventListener(
        "click",
        () => process("ins"));
    ID("fo").addEventListener(
        "click",
        () => process("fo"));
    ID("logbook").addEventListener(
        "click",
        get_fcl_logbook);
    ID("summary").addEventListener(
        "click",
        get_summary);
    ID("error_ok").addEventListener(
        "click",
        () => ID("error_dialog").close());
    ID("config_cancel").addEventListener(
        "click",
        () => {
            ID("config_dialog").retry_logbook = false;
            ID("config_dialog").close();});
    ID("config_save").addEventListener(
        "click",
        () => {save_config();});
}

window.addEventListener("load", main);
