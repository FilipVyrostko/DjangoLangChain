I have decided to learn LangChain and wanted to test it out with by creating veeery simple web application using Django. 
The application offers its users to upload link to a webpage, converting it to pdf and then feeding that (embedded) pdf to pinecone database.
Users can then view the uploaded links as documents and can have simple chat with OpenAIs GPT model.

To run this, you would require two main thing: 
1. OpenAI API key for the chat bot and for the embeddings (unfortunatelly you need to have some credit a.k.a. pay at least $5)
2. Pinecode database set up (using pods so it is free)

At the moment the chat is simple and does not support continuous conversations. Also the forntend is pure HTML so brace yourself.


Special thanks to Udemy for offering great LangChain course that got me into this.


Example:

    
![Screenshot from 2024-03-25 20-49-59](https://github.com/FilipVyrostko/DjangoLangChain/assets/77462803/b1239f22-a941-47f7-b8bc-392e8b067a8e)
