function display() {
    //make ajax call here
    const request = new XMLHttpRequest();
    request.onreadystatechange = function (){
        if (this.readyState === 4 && this.status === 200){
            const username = JSON.parse(this.responseText); 
            document.getElementById("usernameHolder").innerHTML = username;
        }
    };
    request.open("GET", "/home", true); 
    request.send(); 
}
