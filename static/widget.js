(function () {

    function initWidget() {

        // Obtener token desde el script cargado
        let token = null;

        try {
            const scripts = Array.from(document.querySelectorAll("script[src]"));
            const widgetScript = scripts.find(s => s.src.includes("/static/widget.js"));

            if (widgetScript) {
                const url = new URL(widgetScript.src);
                token = url.searchParams.get("token");
            }

            if (!token) {
                console.error("Token no encontrado.");
                return;
            }

        } catch (error) {
            console.error("Error obteniendo token:", error);
            return;
        }

        // HTML del widget
        const chatHTML = `
            <div id="ciip-widget-button">💬</div>

            <div id="ciip-widget-chat">
                <div class="header" id="ciip-header">Asistente</div>
                <div class="messages" id="ciip-messages"></div>
                <div class="input-area">
                    <input type="text" id="ciip-input" placeholder="Escribe tu consulta..." />
                    <button id="ciip-send-btn">Enviar</button>
                </div>
            </div>
        `;

        const style = document.createElement("style");
        style.innerHTML = `
            #ciip-widget-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #2563eb;
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 26px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 9999;
            }

            #ciip-widget-chat {
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 15px;
                display: none;
                flex-direction: column;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                z-index: 9999;
            }

            #ciip-widget-chat .header {
                background: #2563eb;
                color: white;
                padding: 15px;
                border-radius: 15px 15px 0 0;
                font-weight: bold;
            }

            #ciip-widget-chat .messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: #f8fafc;
                font-size: 14px;
            }

            #ciip-widget-chat .input-area {
                display: flex;
                padding: 10px;
                border-top: 1px solid #ddd;
            }

            #ciip-widget-chat input {
                flex: 1;
                padding: 8px;
            }

            #ciip-widget-chat button {
                margin-left: 5px;
                padding: 8px;
                background: #2563eb;
                color: white;
                border: none;
                cursor: pointer;
            }
        `;

        document.body.insertAdjacentHTML("beforeend", chatHTML);
        document.head.appendChild(style);

        const button = document.getElementById("ciip-widget-button");
        const chat = document.getElementById("ciip-widget-chat");
        const header = document.getElementById("ciip-header");
        const messages = document.getElementById("ciip-messages");
        const input = document.getElementById("ciip-input");
        const sendBtn = document.getElementById("ciip-send-btn");

        button.onclick = function () {
            chat.style.display = chat.style.display === "flex" ? "none" : "flex";
        };

        // Función para agregar mensaje del bot
        function addBotMessage(text) {
            messages.innerHTML += `<div><strong>Bot:</strong> ${text}</div>`;
            messages.scrollTop = messages.scrollHeight;
        }

        // Cargar configuración dinámica
        fetch(`http://127.0.0.1:8000/config/${token}`)
            .then(res => res.json())
            .then(config => {
                header.innerText = config.name;
                header.style.backgroundColor = config.primary_color;
                sendBtn.style.backgroundColor = config.primary_color;
                button.style.backgroundColor = config.primary_color;
                addBotMessage(config.welcome_message);
            })
            .catch(error => {
                console.error("Error cargando configuración:", error);
            });

        // Enviar mensaje al backend
        sendBtn.onclick = async function () {
            const message = input.value.trim();
            if (!message) return;

            messages.innerHTML += `<div><strong>Tú:</strong> ${message}</div>`;
            input.value = "";

            try {
                const response = await fetch("http://127.0.0.1:8000/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        message: message,
                        name: "Visitante",
                        company: "Web",
                        token: token
                    })
                });

                const data = await response.json();
                addBotMessage(data.response);

            } catch (error) {
                addBotMessage("Error conectando con el servidor.");
            }
        };
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initWidget);
    } else {
        initWidget();
    }

})();
