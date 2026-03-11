(function() {

const chatBox = document.createElement("div");
chatBox.style.position = "fixed";
chatBox.style.bottom = "20px";
chatBox.style.right = "20px";
chatBox.style.width = "300px";
chatBox.style.height = "400px";
chatBox.style.background = "white";
chatBox.style.border = "1px solid #ccc";
chatBox.style.borderRadius = "10px";
chatBox.style.boxShadow = "0 0 10px rgba(0,0,0,0.2)";
chatBox.style.display = "flex";
chatBox.style.flexDirection = "column";

const messages = document.createElement("div");
messages.style.flex = "1";
messages.style.padding = "10px";
messages.style.overflowY = "auto";

const input = document.createElement("input");
input.placeholder = "Escribe tu pregunta...";
input.style.border = "none";
input.style.borderTop = "1px solid #ccc";
input.style.padding = "10px";

chatBox.appendChild(messages);
chatBox.appendChild(input);
document.body.appendChild(chatBox);

input.addEventListener("keypress", async function(e) {

if (e.key === "Enter") {

const text = input.value;

messages.innerHTML += "<div><b>Tu:</b> " + text + "</div>";

const response = await fetch("https://TUAPP.onrender.com/chat", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({
message: text
})
});

const data = await response.json();

messages.innerHTML += "<div><b>Bot:</b> " + data.response + "</div>";

input.value = "";

}

});

})();