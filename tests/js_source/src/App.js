import React from 'react';
import './App.css';
import { CSourceB } from './c_source';

function App() {
    return (
        <div>
            <div>Sending messages to the server and waiting for responses.</div>
            <ul id="list"></ul>
        </div>
  );
}

var websocket = new WebSocket("ws://127.0.0.1:8765/");
websocket.binaryType = "arraybuffer";
websocket.onmessage = function (event) {
    var message = new CSourceB();
    message.fromUint8Array(new Uint8Array(event.data));
    console.log(message);

    if (message.choice === CSourceB.CHOICE_A) {
        appendList("Received: " + message.value.a);
    }
};

function appendList(text) {
    var node = document.createElement("li");
    var textnode = document.createTextNode(text);
    node.appendChild(textnode);
    document.getElementById("list").appendChild(node);
    window.scrollTo(0, document.body.scrollHeight);
}

var message = new CSourceB();
message.choice = CSourceB.CHOICE_A;
message.value.a = 0;

function tick() {
    message.value.a++;

    if (message.value.a > 127) {
        message.value.a = -128;
    }

    appendList("Sending: " + message.value.a);
    websocket.send(message.toUint8Array());
}

setInterval(tick, 500);

export default App;
