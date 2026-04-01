import os
from anthropic import Anthropic
from src.costl.agents.agent import Agent


class ClaudeAgent(Agent):
    def __init__(self, model, max_history: int = 5):
        super().__init__(model)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.prompt_chain = []
        self.max_history = None if max_history is None else int(max_history)

    def _chat(self, messages, temperature=None, top_p=None):
        # Separate system message from user/assistant turns
        system_prompt = ""
        conv_messages = []
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
            else:
                conv_messages.append(m)

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": conv_messages if conv_messages else [{"role": "user", "content": "Hi"}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def llm_call(self, prompt, question, **kwargs):
        messages = []
        if prompt:
            messages.append({"role": "user", "content": prompt})
            messages.append({"role": "assistant", "content": "Understood."})
        messages.append({"role": "user", "content": question})
        return self._chat(messages)

    def reset(self):
        self.prompt_chain = []
