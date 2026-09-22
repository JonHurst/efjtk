"use strict";

// const EFJTOOL_URL = "https://yu3zknipfl.execute-api.eu-west-2.amazonaws.com/default/efj-tool";
const EFJTOOL_URL = "https://u8ei87fcgi.execute-api.eu-west-2.amazonaws.com/default/efj-tool-staging";

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
        ID("error_message").innerText =
            `Line ${sections[1]} : ${sections[2]} : ${sections[3]}`;
    }
    else {
        ID("error_message").innerText = text;
    }
    ID("error_dialog").showModal();
}


async function process(action) {
    push_history(ID("output").value);
    let result = await post(ID("output").value, action);
    if(!result)
        return;
    if(result[1] == "success")
        ID("output").value = result[0];
    else
        show_error(result[0]);
}


function push_history() {
    history.push(ID("output").value);
}


async function save_output_to_file() {
    save_to_file(ID("output").value, "text/plain", "efj.txt");
}


async function copy_output_to_clipboard() {
    let cb = window.navigator.clipboard;
    await cb.writeText(ID("output").value);
    window.alert("eFJ copied to clipboard");
}


function get_full_date_range(efj) {
    let dates = [];
    for(let line of efj.split("\n")) {
        let match = /\s*(\d{4}-\d{2}-\d{2})|([+]+)/.exec(line);
        if(match && match.length == 3) {
            if(match[1]) {
                dates.push(new Date(match[1]));
            } else if(match[2] && dates.length > 0) {
                let date = new Date(dates[dates.length - 1]);
                date.setDate(date.getDate() + match[2].length);
                dates.push(date);
            }
        }
    }
    if(dates.length == 0) {
        return null;
    }
    dates.sort((a, b) => a - b);
    let to_date = dates[dates.length - 1];
    to_date.setDate(to_date.getDate() + 1);
    return [dates[0].toISOString().slice(0, 10),
            to_date.toISOString().slice(0, 10)];

}


async function post(efj, action) {
    return new Promise((resolve, reject) => {
        let full_date_range = get_full_date_range(efj);
        if(full_date_range && full_date_range.length == 2) {
            ID("dr_from").value = full_date_range[0];
            ID("dr_to").value = full_date_range[1];
        }
        ID("date_range_dialog").showModal();
        ID("dr_ok").onclick = async () => {
            ID("date_range_dialog").close();
            let from = ID("dr_from").value;
            let to = ID("dr_to").value;
            let daterange = null;
            if(from && to) {
                daterange = [from, to];
            }
            ID("working").classList.remove("hidden");
            let response;
            try {
                response = await fetch(EFJTOOL_URL, {
                    method: "POST",
                    body: JSON.stringify({
                        "efj": efj,
                        "action": action,
                        "daterange": daterange
                    }),
                    cache: "no-cache"
                });
                ID("working").classList.add("hidden");
                if(response.ok) {
                    resolve(response.json());
                } else {
                    reject(Error(`HTTP error: ${response.status}`));
                }
            } catch (error) {
                ID("working").classList.add("hidden");
                reject(Error("Network error"));
            }
        };
    });
}


async function get_fcl_logbook() {
    let result = await post(ID("output").value, "logbook");
    if(!result)
        return;
    if(result[1] == "success") {
        save_to_file(result[0], "text/html", "fcl-logbook.html");
    } else {
        show_error(result[0]);
    }
}


async function get_summary() {
    let result = await post(ID("output").value, "summary");
    if(!result)
        return;
    if(result[1] == "success") {
        save_to_file(result[0], "text/html", "summary.html");
    } else {
        show_error(result[0]);
    }
}


async function get_cumulative() {
    let result = await post(ID("output").value, "cumulative");
    if(!result)
        return;
    if(result[1] == "success") {
        save_to_file(result[0], "text/html", "cumulative.html");
    } else {
        show_error(result[0]);
    }
}


function main() {
    const input = ID("input");
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
        () => {if(history.length) ID("output").value = history.pop();});
    ID("save").addEventListener(
        "click",
        () => save_output_to_file());
    ID("copy").addEventListener(
        "click",
        () => copy_output_to_clipboard());
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
    ID("cumulative").addEventListener(
        "click",
        get_cumulative);
    ID("error_ok").addEventListener(
        "click",
        () => ID("error_dialog").close());
    ID("help").addEventListener("click", () => window.open(
        "https://hursts.org.uk/efjtkdocs/webapp.html", "_blank"));
    const body = document.getElementsByTagName("body")[0];
    body.addEventListener("drop", dropHandler);
    body.addEventListener("dragover", dragoverHandler);
}

window.addEventListener("load", main);
