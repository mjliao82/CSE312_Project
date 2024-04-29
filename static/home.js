var socket = io()


function display() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function (){
        if (this.readyState === 4 && this.status === 200){
            const response = JSON.parse(this.responseText);
            if (response.username) {
                // console.log("hello");
                // console.log(response.username);  // Log the username.
                document.getElementById("usernameHolder").innerHTML = response.username;
            } else {
                console.log("Error:", response.error);  // Log the error.
            }
        }
    };
    request.open("GET", "/get-username", true);
    request.send();
}


socket.on('connect', function() {
    console.log('Connected to the server');
});

socket.on('disconnect', function() {
    console.log('Disconnected from the server');
});


function fetchonline() {
    fetch("/online")
        .then(response => response.json())
        .then(data => {
            const onlineUserElement = document.getElementById("OnlineUsers");
            onlineUserElement.innerHTML = '';
            data.users.forEach((user, index) => {
                onlineUserElement.innerHTML += `
                    <div>
                        ${user} 
                        <input id="chat-text-box-${index}" type="text" />
                    </div>
                `;
                remoteUserId = user;
            });
        })
        .catch(error => console.error('Error fetching online users:', error));
}





function sendDM(user, index){
    const chatTextBox = document.getElementById(`chat-text-box-${index}`);
    const message = chatTextBox.value;
    chatTextBox.value = "";
    socket.emit('send_dm', {'messageType': 'DMMessage', 'message': message, 'dm': user});
}



function deleteMessage(messageId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response); 
        }
    };
    request.open("DELETE", "/chat-messages", true); 
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    // add message_id to end
    request.send(JSON.stringify({id: messageId})); 
}


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

function addMessageToDM(messageJSON) {
    const chatMessages = document.getElementById("chat-messages2");
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
        // Using AJAX
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // console.log(this.response);
        }
    }
    const messageJSON = {"message": message, "token": token};
    socket.emit('send_chat', messageJSON);

    // const messageJSON = {"message": message, "token":token};
    // request.open("POST", "/chat-messages");
    // request.setRequestHeader("Content-Type", "application/json"); 
    // request.send(JSON.stringify(messageJSON));
    chatTextBox.focus();
}

socket.on('receive_chat', function(message) {
    addMessageToChat(message)
    console.log('New chat message received:', message);
});

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

function clearDM() {
    const chatMessages = document.getElementById("chat-messages2");
    chatMessages.innerHTML = "";
}

function updateDM() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearDM();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToDM(message);
            }
        }
    }
    request.open("GET", "/DM-messages");
    request.send();
}

function startGame(){
    const request = new XMLHttpRequest();
    request.open("POST", "/start-game")
    request.send()
}

function profPic() {
    const payload = document.getElementById("image-upload-form");
    const request = new XMLHttpRequest();
    request.open("POST", "/profPic");
    request.setRequestHeader('Content-Type', 'image/jpg')
    request.send(payload);
}

document.getElementById('startGame').addEventListener('click', startGame)

function new_game() {
    function waitForGame() {
        var interval = setInterval(function() {
            fetch('/findGame', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Received updates from server:', data);
                    if (data.message === "GameStart") {
                        clearInterval(interval);
                        playGame();
                    } else {
                        console.log("Still waiting");
                    }
                })
                .catch(error => {
                    console.error('Error polling server:', error);
                });
        }, 3000);
    }

    waitForGame();
}

function playGame() {
    let interval = setInterval(function () {
        fetch('/whosTurn')
            .then(response => response.json())
            .then(data => {
                console.log("Got the whos turn response: ", data);
                if (data.message === "Yes") {
                    console.log("Its your turn");
                }
            })
            .catch(error => {
                console.log("error finding the turn");
            })
    }, 3000);
}

function blockSelect(position) {
    const request = new XMLHttpRequest();
    request.open("POST", "/move");
    request.setRequestHeader('Position', position);
    request.onload = function() {
        if (request.status === 200) {
            console.log("Move successful");
        } else {
            console.error("Error making move:", request.statusText);
        }
    };
    console.log(request);
    request.send();
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "" : "dark";  // Toggle theme
    document.documentElement.setAttribute("data-theme", newTheme);
}


function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    document.getElementById("theme-toggle").addEventListener('click', toggleTheme);

    document.getElementById("chat-text-box").focus();

    updateChat();
    // updateDM();

    // setInterval(updateChat, 30000);
    setInterval(fetchonline, 30000);
}