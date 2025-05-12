# GPT_Assistant.py

from openai import OpenAI

class LuisAssistant:
    def __init__(self, api_key_path: str):
        with open(api_key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.vector_store_id = "xxxxx" #ADD here

    def ask(self, question: str, history: list = None) -> str:
        """
        Sends a question to the GPT agent using the responses API with vector store.
        History is optional (list of message dictionaries).
        """
        # Input format for responses.create() — includes history if any
        inputs = history if history else []

        # Append the user's question to the input sequence
        inputs.append({
            "role": "user",
            "content": [
                {"type": "input_text", "text": question}
            ]
        })

        try:
            response = self.client.responses.create(
                model=self.model,
                input=inputs,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [self.vector_store_id]
                    }
                ],
                temperature=0.25, #like 0.2 will make it morefocused and deterministic
                top_p=1,
                max_output_tokens=256,
                store=True,
                text={"format": {"type": "text"}},
                reasoning={}
            )
            # ✅ Loop through response.output and return assistant message content
            for item in response.output:
                if item.type == "message" and hasattr(item, "content"):
                    for content_block in item.content:
                        if content_block.type == "output_text":
                            return  content_block.text.strip()

            return "❌ No assistant message found in response."
            # return response.output[0].text["text"].strip()

        except Exception as e:
            return f"Error: {str(e)}"
