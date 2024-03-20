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

function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const message = chatTextBox.value;
    const hiddenXSRF = document.getElementById('xsrf');
    const token = hiddenXSRF.innerText;
    chatTextBox.value = "";
    //hiddenXSRF.value = "{{XSRF}}";
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
        request.send(JSON.stringify(messageJSON));
    }
    chatTextBox.focus();
}
