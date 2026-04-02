from dotenv import load_dotenv
import os

from src.lapis.agents.gpt import GPTAgent
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel
from typing import Optional, List


class ConstraintSelectionDescription(BaseModel):
    reasoning: str
    constraint_order: List[str]
    conditional_constraints: List[str]
    global_constraints: List[str]


class ConstraintOrderSelector(GPTAgent):
    """Specialized agent for NL->LTL description parsing.

    Keeps its own system prompt (can be provided as text or from a file)
    and exposes a `parse_nl` helper that uses the OpenAI `parse` endpoint
    with a pydantic `response_format` model (e.g., `FormulaDescription`).
    """
    def __init__(self, model: str, system_prompt: Optional[str] = None, prompt_file: Optional[str] = None, max_history: int = 1):
        super().__init__(model, max_history=max_history)
        prompt_path = os.path.join(os.path.dirname(__file__), "Prompts", "constraint_order_selector_prompt.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as pf:
                self.system_prompt = pf.read().strip()
        except Exception:
            print('ERROR: Could not load system prompt from file for ConstraintOrderSelector.')
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
    
def constraint_order_selection(domain, problem, initial_state, goal, constraints, agent, object_list, predicates_list, predicates_meaning):
    # Normalize constraints into a list (one constraint per LLM call)
    
    constraint_order = ''

    user_input = f"""
    Domain: {domain}
    Problem: {problem}
    Initial State: {initial_state}
    Goal: {goal}
    Constraints: {constraints}
    Objects: {object_list}
    Predicates: {predicates_list}
    Predicates Meaning: {predicates_meaning}
    """

    response = agent.step(user_input, response_model=ConstraintSelectionDescription)
    description = response.choices[0].message.parsed

    reasoning = description.reasoning
    ordered_constraints = description.constraint_order
    conditional_constraints = description.conditional_constraints
    global_constraints = description.global_constraints

    print('######################################')
    print('REASONING: ', reasoning)
    print('CONSTRAINT ORDER: ', ordered_constraints)
    print('CONDITIONAL CONSTRAINTS: ', conditional_constraints)
    print('GLOBAL CONSTRAINTS: ', global_constraints)
    #input('\nPRESS ENTER TO CONTINUE...')


    return reasoning, ordered_constraints, conditional_constraints, global_constraints