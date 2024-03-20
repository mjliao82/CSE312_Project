function display() {
    //make ajax call here
    const request = new XMLHttpRequest();
    request.onreadystatechange = function (){
        if (this.readyState === 4 && this.status === 200){
            const username = JSON.parse(this.responseText); 
            document.getElementById("usernameHolder").innerHTML = username;
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
