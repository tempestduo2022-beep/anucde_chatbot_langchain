(function() {
    // --- CONFIGURATION ---
    const BACKEND_URL = 'http://localhost/faq';
    const WHATSAPP_URL = 'https://wa.me/91XXXXXXXXXX'; 
    const PRIMARY_COLOR = '#4B0082';

    // --- CSS INJECTION ---
    const style = document.createElement('style');
    style.innerHTML = `
        :root {
            --widget-primary: ${PRIMARY_COLOR};
            --widget-white: #ffffff;
            --widget-grey: #f3f4f6;
            --widget-text: #1f2937;
        }

        /* Launcher */
        #chat-widget-launcher {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: var(--widget-primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 9999;
            transition: transform 0.3s ease;
        }
        #chat-widget-launcher:hover { transform: scale(1.1); }
        #chat-widget-launcher svg { width: 30px; height: 30px; }

        /* Widget Container */
        #chat-widget-container {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 380px;
            height: 600px;
            max-height: 80vh;
            background: var(--widget-white);
            border-radius: 16px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9998;
            font-family: 'Inter', -apple-system, sans-serif;
        }

        /* Mobile Responsiveness */
        @media (max-width: 480px) {
            #chat-widget-container {
                bottom: 0;
                right: 0;
                width: 100%;
                height: 100%;
                max-height: 100vh;
                border-radius: 0;
            }
            #chat-widget-launcher { bottom: 10px; right: 10px; }
        }

        #chat-widget-header {
            background: var(--widget-primary);
            color: white;
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        #chat-widget-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #fafafa;
        }

        .widget-msg {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.6;
            word-wrap: break-word;
        }
        .user-msg { align-self: flex-end; background: var(--widget-primary); color: white; border-bottom-right-radius: 2px; }
        .bot-msg { align-self: flex-start; background: white; color: black; border: 1px solid #e5e7eb; border-bottom-left-radius: 2px; }
        .bot-msg a { color: #0000EE; text-decoration: underline; }

        #chat-widget-input-area {
            padding: 15px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        #chat-widget-input {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            outline: none;
            font-size: 16px; /* Prevents iOS auto-zoom */
        }
        #chat-widget-send {
            background: var(--widget-primary);
            color: white;
            border: none;
            width: 44px; /* Touch friendly */
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #chat-widget-send:disabled { background: #ccc; cursor: not-allowed; }

        .widget-typing { font-style: italic; color: #6b7280; font-size: 12px; padding: 5px 15px; display: none; }
    `;
    document.head.appendChild(style);

    // --- HTML INJECTION ---
    const container = document.createElement('div');
    container.innerHTML = `
        <div id="chat-widget-launcher">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </div>
        <div id="chat-widget-container">
            <div id="chat-widget-header">
                <span>ANUCDE Assistant</span>
                <button id="chat-widget-close" style="background:none;border:none;color:white;font-size:24px;cursor:pointer;">&times;</button>
            </div>
            <div id="chat-widget-messages">
                <div class="widget-msg bot-msg">Welcome to ANUCDE Assistant. How can I help you today?</div>
            </div>
            <div id="chat-widget-typing" class="widget-typing">Assistant is thinking...</div>
            <div id="chat-widget-input-area">
                <input type="text" id="chat-widget-input" placeholder="Type your query...">
                <button id="chat-widget-send">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(container);

    // --- LOGIC ---
    const launcher = document.getElementById('chat-widget-launcher');
    const widget = document.getElementById('chat-widget-container');
    const closeBtn = document.getElementById('chat-widget-close');
    const sendBtn = document.getElementById('chat-widget-send');
    const input = document.getElementById('chat-widget-input');
    const messages = document.getElementById('chat-widget-messages');
    const typing = document.getElementById('chat-widget-typing');

    let sessionId = Math.random().toString(36).substring(2, 15);

    launcher.onclick = () => { widget.style.display = 'flex'; launcher.style.display = 'none'; input.focus(); };
    closeBtn.onclick = () => { widget.style.display = 'none'; launcher.style.display = 'flex'; };

    function appendMsg(text, isUser = false, isHtml = false) {
        const div = document.createElement('div');
        div.className = `widget-msg \${isUser ? 'user-msg' : 'bot-msg'}`;
        if (isHtml) div.innerHTML = text; else div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    function renderMd(text) {
        let r = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        r = r.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        r = r.replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>');
        if (r.includes('<li>')) r = r.replace(/(<li>[\s\S]*<\/li>)/, '<ul style="margin:5px 0;padding-left:20px;">$1</ul>');
        return r.replace(/\n/g, '<br>');
    }

    async function ask() {
        const text = input.value.trim();
        if (!text) return;

        // Cool-down
        sendBtn.disabled = true;
        appendMsg(text, true);
        input.value = '';
        typing.style.display = 'block';

        const botDiv = appendMsg('', false, true);
        botDiv.style.display = 'none';

        try {
            const res = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, session_id: sessionId })
            });

            if (res.status === 429) {
                typing.style.display = 'none';
                botDiv.style.display = 'block';
                botDiv.innerHTML = 'Too many requests! Please wait a minute before asking again.';
                return;
            }

            if (!res.ok) throw new Error('Server Error');

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let full = "";
            typing.style.display = 'none';
            botDiv.style.display = 'block';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                full += decoder.decode(value, { stream: true });
                botDiv.innerHTML = renderMd(full);
                messages.scrollTop = messages.scrollHeight;
            }
        } catch (e) {
            typing.style.display = 'none';
            botDiv.style.display = 'block';
            botDiv.innerHTML = `Unable to connect to the assistant. Please try again later or reach out via <a href="\${WHATSAPP_URL}" target="_blank">WhatsApp Support</a>.`;
        } finally {
            // Enable button after 3s cool-down
            setTimeout(() => { sendBtn.disabled = false; }, 3000);
        }
    }

    sendBtn.onclick = ask;
    input.onkeypress = (e) => { if (e.key === 'Enter') ask(); };
})();
