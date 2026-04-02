from dotenv import load_dotenv
import os

from src.lapis.agents.gpt import GPTAgent
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel
from typing import Optional, List


class TraceDescription(BaseModel):
    reasoning: str
    new_state: str


class TraceGenerationAgent(GPTAgent):
    """Specialized agent for NL->LTL description parsing.

    Keeps its own system prompt (can be provided as text or from a file)
    and exposes a `parse_nl` helper that uses the OpenAI `parse` endpoint
    with a pydantic `response_format` model (e.g., `TraceDescription`).
    """
    def __init__(self, model: str, system_prompt: Optional[str] = None, prompt_file: Optional[str] = None, max_history: int = 1):
        super().__init__(model, max_history=max_history)
        prompt_path = os.path.join(os.path.dirname(__file__), "Prompts", "trace_generator_prompt.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as pf:
                self.system_prompt = pf.read().strip()
        except Exception:
            print('ERROR: Could not load system prompt from file for TraceGenerationAgent.')
            input('Press Enter to continue...')

    def set_system_prompt(self, prompt: str):
        """Set or update the system prompt stored by the agent.

        This does not automatically push the prompt into `prompt_chain`.
        Use `init_prompt_chain` or `update_prompt_chain` to affect the chain.
        """
        self.system_prompt = prompt

    def step(self, user_input: str, response_model, temperature: Optional[float] = 0):
        """Generate a LTL formula from an NL description into the provided `response_model`.
        Returns the raw parse response (the library will return an object
        according to `response_model` when successful).
        """
        user_msg = {"role": "user", "content": f"{user_input}"}

        # If prompt_chain is empty, initialize it with the system prompt and this user message.
        if not getattr(self, "prompt_chain", None):
            self.init_prompt_chain(self.system_prompt, user_msg["content"])
        else:
            # Append this user message to the existing chain (keeps system prompt at index 0)
            # Use current system prompt stored in chain to avoid duplicating it
            current_system = self.prompt_chain[0]["content"] if self.prompt_chain and self.prompt_chain[0].get("role") == "system" else self.system_prompt
            self.update_prompt_chain(current_system, user_msg["content"])

        # Use the lower-level parse API on the agent's prompt_chain to get typed output
        resp = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=self.prompt_chain,
            temperature=temperature,
            seed=42,
            response_format=response_model,
        )

        # Append assistant response to the history so subsequent calls see it
        try:
            assistant_content = resp.choices[0].message.content
        except Exception:
            assistant_content = None

        if assistant_content:
            self.update_prompt_chain_with_response(assistant_content, role="assistant")

        return resp
    
def trace_generation(domain, problem, current_state, plan_step, goal, agent):
    # Normalize constraints into a list (one constraint per LLM call)
   
    user_input = f"""
    Domain: {domain}
    Problem: {problem}
    Current State: {current_state}
    Plan: {plan_step}
    Goal: {goal}
    """

    response = agent.step(user_input, response_model=TraceDescription)
    description = response.choices[0].message.parsed

    reasoning = description.reasoning
    new_state = description.new_state

    print('######################################')
    print('Reasoning: ', reasoning)
    print('NEW STATE: ', new_state)


    #print('\nNEW SUBGOALS (if any): ', new_subgoals)

    # Return reasoning, the combined formula, fluent syntax, the (possibly updated) goal,
    # and the list of individual sub-formulas corresponding to each constraint.
    return reasoning, new_state