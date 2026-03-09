from ollama import chat,ChatResponse
from langchain_ollama import ChatOllama
from fastapi import FastAPI , File, UploadFile

app = FastAPI(title="demo")
llm = ChatOllama(model="gemma3:1b")
# response:ChatResponse = chat(model="gemma3:1b",messages=[
#     {
#     'role':'user',
#     'content':'why the sky is blue?',
# },
# ])
messages= [
    ("system",
    "You are helpful for summarize the data with 5 lines"),
    ("human",
     "how to cook biriyani?"),
]

ai_res = llm.invoke(messages)
print(ai_res.content)
#print(response['message']['content'])
# print(response.message.content)

@app.post("/files")
async def upload_File(file:UploadFile):
    return { "filename": file.filename}