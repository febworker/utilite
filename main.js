const formChat = document.getElementById('formChat');
const textField = document.getElementById('textField');
const subscribe = document.getElementById('subscribe');

const ws = new WebSocket('ws://localhost:8080');

ws.onopen = function(event) {
    console.log('Connected to WebSocket server');
};

ws.onmessage = function(event) {
    const message = event.data;
    const elMsg = document.createElement('div');
    elMsg.textContent = message;
    subscribe.appendChild(elMsg);
};

ws.onclose = function(event) {
    console.log('Connection to WebSocket server closed');
};

ws.onerror = function(event) {
    console.error('WebSocket error:', event);
};

formChat.addEventListener('submit', function(event) {
    event.preventDefault();
    const message = textField.value;
    ws.send(message);
    textField.value = '';
});