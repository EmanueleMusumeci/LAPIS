from dotenv import load_dotenv
import os
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel
from typing import Optional, List

# Import GPTAgent to subclass for a specialized NL->LTL agent
from src.lapis.agents.gpt import GPTAgent

class NLDescription(BaseModel):
    domain: str
    problem: str
    actions: str
    initial_state: str
    goal: str
    constraints: List[str]
    object_list: List[str]
    predicates_list: List[str]
    predicates_meaning: List[str]

class NLDescriptionAgent(GPTAgent):
    """Specialized agent for NL->LTL description parsing.

    Keeps its own system prompt (can be provided as text or from a file)
    and exposes a `parse_nl` helper that uses the OpenAI `parse` endpoint
    with a pydantic `response_format` model (e.g., `NLDescription`).
    """
    def __init__(self, model: str, system_prompt: Optional[str] = None, prompt_file: Optional[str] = None, max_history: int = 5):
        super().__init__(model, max_history=max_history)
        prompt_path = os.path.join(os.path.dirname(__file__), "Prompts", "nl_description_generator_prompt.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as pf:
                self.system_prompt = pf.read().strip()
        except Exception:
            print('ERROR: Could not load system prompt from file for NLDescriptionAgent.')
            #input('Press Enter to continue...')

    def set_system_prompt(self, prompt: str):
        """Set or update the system prompt stored by the agent.

        This does not automatically push the prompt into `prompt_chain`.
        Use `init_prompt_chain` or `update_prompt_chain` to affect the chain.
        """
        self.system_prompt = prompt

    def step(self, nl_text: str, response_model, temperature: Optional[float] = 0):
        """Parse an NL description into the provided `response_model`.

        Returns the raw parse response (the library will return an object
        according to `response_model` when successful).
        """
        user_msg = {"role": "user", "content": f"{nl_text}"}

        # Initialize or update the agent's prompt_chain instead of recreating system prompt each call
        if not getattr(self, "prompt_chain", None):
            # start chain with the stored system prompt and this user message
            self.init_prompt_chain(self.system_prompt, user_msg["content"])
        else:
            # append the new user message, preserving system prompt at index 0
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

        # Append assistant response to history so subsequent calls see it
        try:
            assistant_content = resp.choices[0].message.content
        except Exception:
            assistant_content = None

        if assistant_content:
            self.update_prompt_chain_with_response(assistant_content, role="assistant")

        return resp

def nl_description_generation(nl_file,agent):
    # Load system prompt from external Prompts/nl_description_generator_prompt.txt
   
    response = agent.step(nl_file, response_model=NLDescription)
    description = response.choices[0].message.parsed

    
    print('NL DESCRIPTION: ', description)
    domain = description.domain
    problem = description.problem
    actions = description.actions
    initial_state = description.initial_state
    goal = description.goal
    constraints = description.constraints
    object_list = description.object_list
    predicates_list = description.predicates_list
    predicates_meaning = description.predicates_meaning

    print('\nDOMAIN: ', domain)
    print('\nPROBLEM: ', problem)
    print('\nACTIONS: ', actions)
    print('\nINITIAL STATE: ', initial_state)
    print('\nGOAL: ', goal)
    print('\nCONSTRAINTS: ', constraints)
    print('\nOBJECT LIST: ', object_list)
    print('\nPREDICATES LIST: ', predicates_list)
    print('\nPREDICATES MEANING: ', predicates_meaning)
    #input('test to continue')


    
    return domain,problem,actions,initial_state,goal,constraints, object_list, predicates_list, predicates_meaning