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

// function fetchData() {
//     fetch('/login')
//         .then(response => response.json())
//         .then(data => {
//             document.getElementById('data').textContent = JSON.stringify(data);
//         })
//         .catch(error => console.error('Error fetching data:', error));
// }
