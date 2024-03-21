function display() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function (){
        if (this.readyState === 4 && this.status === 200){
            const response = JSON.parse(this.responseText);
            if (response.username) {
                console.log("hello");
                console.log(response.username);  // Log the username.
                document.getElementById("usernameHolder").innerHTML = response.username;
            } else {
                console.log("Error:", response.error);  // Log the error.
            }
        }
    };
    request.open("GET", "/get-username", true);
    request.send();
}



const ws = false;
let socket = null;

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('ws://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType
        if(messageType === 'chatMessage'){
            addMessageToChat(message);
        }else{
            // send message to WebRTC
            processMessageAsWebRTC(message, messageType);
        }
    }
}


// function deleteMessage(messageId) {
//     const request = new XMLHttpRequest();
//     request.onreadystatechange = function () {
//         if (this.readyState === 4 && this.status === 200) {
//             console.log(this.response);
//         }
//     }
//     request.open("DELETE", "/chat-messages/" + messageId);
//     request.send();
// }

function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    let messageHTML = "<br><button onclick='deleteMessage(\"" + messageId + "\")'>X</button> ";
    messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}



function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const message = chatTextBox.value;
    const hiddenXSRF = document.getElementById('xsrf');
    const token = hiddenXSRF.value;
    chatTextBox.value = "";
    if (ws) {
        // Using WebSockets
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message, 'token':token}));
    } else {
        // Using AJAX
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log(this.response);
            }
        }
        const messageJSON = {"message": message, "token":token};
        request.open("POST", "/chat-messages");
        request.setRequestHeader("Content-Type", "application/json"); 
        request.send(JSON.stringify(messageJSON));
    }
    chatTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-messages");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    document.getElementById("chat-text-box").focus();

    updateChat();

    if (ws) {
        initWS();
    } else {
        setInterval(updateChat, 5000);
    }
}