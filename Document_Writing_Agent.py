import os
import dotenv
from langchain.agents import create_agent
dotenv.load_dotenv()

from langchain_openai import ChatOpenAI
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from datetime import datetime
import json

OPENAI_API_KEY = os.environ["OPENAI_SECRET_KEY"]
memory_storage_path = "C:/Users/madan/Downloads/Document Writing Agent/file_obj_memory_store.json"

file_directory_obj = {
    "file_path": str(Path("documents")),
    "file_extension": ".txt",
    "file_name": "document",
    "file_content": "This is a document",
    "file_type": "text",
    "file_size": 100,
    "file_created_at": str(datetime.now()),
}

@tool
def write_document(filename: str, content: str):
    """Write a document to the file system"""
    global file_directory_obj
    file_save_path = os.path.join("C:/Users/madan/Downloads/Document Writing Agent", filename)
    try:
        print(f"Writing document to {filename}")
        if Path(memory_storage_path).exists() and Path(memory_storage_path).stat().st_size > 0:
            with open(memory_storage_path, "r", encoding="utf-8") as file:
                file_directory_obj = json.load(file)
        if not filename in file_directory_obj:
            file_directory_obj[filename] = {
            "file_content": content,
            "file_type": "text",
            "file_size": len(content),
            "file_created_at": str(datetime.now()),
            }
            
        else:
            old_content=file_directory_obj[filename].get("file_content")
            new_content=old_content+"\n"+content
            file_directory_obj[filename]={
            "file_content":new_content,
             "file_type":"text",
            "file_size":len(new_content),
            "file_created_at":str(datetime.now())
        }
        
        with open(memory_storage_path, "w") as file:
                
                json.dump(file_directory_obj, file, indent=4)
                
        
        with open(file_save_path, "a") as file:
            file.write(content)
        print(f"✅ File saved at: {file_save_path}")    
        return f"Document {filename} created successfully"
    except Exception as e:
        return f"Error creating document {filename}: {e}"


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.3)

    while True:
        file_name = input("\nEnter the file name (or 'q' to quit): ")
        if file_name.lower().strip() == 'q':
            print("Exiting document manager application. Goodbye!")
            break

        user_input = input("Hello User, ask the agent to answer on any topic (or press 'q' to quit): ")
        if user_input.lower().strip() == 'q':
            print("Exiting document manager application. Goodbye!")
            break

        system_prompt = SystemMessage(content=(
            f"You are a document manager agent. "
            f"When saving files, use this exact filename: {file_name}. "
            f"Always call the write_document tool when the user asks to save or write content."
        ))

        # ✅ ADDED: Append save instruction to user input
        user_input = f"{user_input}. Save the response to '{file_name}' using the write_document tool."

        agent = create_agent(
            model=llm,
            tools=[write_document],
            system_prompt=system_prompt
        )

        response = agent.invoke({
            "messages": [("user", user_input)]
        })

        print(f"Agent Response: {response['messages'][-1].content}")


if __name__ == "__main__":
    main()