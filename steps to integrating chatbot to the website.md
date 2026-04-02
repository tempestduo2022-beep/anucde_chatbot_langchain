For the purpose of integrating current chatbot with tech stack as follows to the current anucde website:

fastapi,

langchain,

faiss(vector index inside langchain),

ollama(qwen 2.5 3b - inside langchain's chatollama),

hugging face embeddings(sentence transformers),

html/css/js



If divided into 2 parts to integrate such as frontend and backend then the integration differs for both parts



For frontend if the website is in static html files then:

* could directly add the widget code snippet in the html file (css in the <head> and code in the <body>tag) (or)
* we can create a file chatbot\_widget.js and directly give the link to this file in a line in the code

If it is in react then:

* Could be used in <script> tag (or)
* could integrate in the iframe (or)
* can manually add the code in this too





For backend to be integrated into the current server:

* use dockerfile (contains the backend code+ automatically installs requirements+ runs the server)
* whereas the llm model ollama would be managed in docker-compose.yml (i.e the model would be run by this file)
* finally use nginx to act as a reverse proxy (front door) for the https transfer as the user requests would come from a https domain





The only bottleneck would be that using an llm by concurrent users would increase the load and latency.

The possible solutions could be

* either a GPU (or)
* use external apis such as open ai, groq etc but would have to pay monthly for the service



Other issues to concentrate on before integrating the bot into the current website:

* rate limiting (thinking of using a token bucket i.e student will have to wait for a few minutes before asking another set of questions once their token bucket has been used + client side cool down i.e disabling the send button in the chatbot until the users query's response is sent)



* chat persistence (not decided but one of the best options is to make a local storage in the clients web browser)



* mobile responsiveness (needs to adjust the height with media query, ensure students can see the text box and send button, ensure the chat window shrinks whenever a keyboard appears for the user to type their query)



* fallback if the server goes down (could simply show an error message along with redirecting the user to the WhatsApp bot)

