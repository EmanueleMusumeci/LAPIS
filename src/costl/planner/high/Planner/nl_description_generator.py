from dotenv import load_dotenv
import os
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel

class NLDescription(BaseModel):
    domain: str
    problem: str
    actions: str
    goal: str
    constraints: str

def nl_description_generation(nl_file, agent):
    system_prompt = """
You are an expert at explaining planning problems in clear, conversational language.

Analyze the input and provide:

1. **Domain**: Describe the domain in detail - what it's about, what actions are available, how they work, what their preconditions and effects are. Explain this thoroughly as if teaching someone unfamiliar with the domain.

2. **Problem**: Summarize the specific problem instance concisely - what objects exist, what the initial state is, and what the goal is.

3. **Actions**: This is CRITICAL - describe the available actions with CLEAR EMPHASIS on their constraints and limitations. Include:
   - What the action accomplishes (the capability)
   - IMPORTANT LIMITATIONS (e.g., "you can only hold ONE block at a time", "you must put down what you're holding before picking up another")
   - Physical constraints (e.g., "you can only pick up a block if nothing is on top of it")
   - Preconditions in natural language (what must be true before you can do the action)
   
   Express this in natural, conversational language. For example:
   "You can move blocks around by picking them up and placing them. However, you can ONLY hold one block at a time, so you must put down whatever you're holding before picking up another block. You can only pick up blocks that are clear (nothing on top of them)."

4. **Goal**: State what needs to be achieved.

5. **Constraints**: Describe any additional constraints that must be satisfied in form of a list with 1 item for each constraint.

Important: Write naturally as a human would. Instead of technical names like "black_block_1", say "the black block number 1" or "the first black block". Make the physical constraints and limitations very clear and explicit in everyday language.
"""

    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate this into LTL: {nl_file}"}
        ],
        temperature=0,
        seed=42,
        response_format=NLDescription,
    )
    description = response.choices[0].message.parsed

    
    print('NL DESCRIPTION: ', description)
    domain = description.domain
    problem = description.problem
    actions = description.actions
    goal = description.goal
    constraints = description.constraints

    print('\nDOMAIN: ', domain)
    print('\nPROBLEM: ', problem)
    print('\nACTIONS: ', actions)
    print('\nGOAL: ', goal)
    print('\nCONSTRAINTS: ', constraints)


    
    return domain,problem,actions,goal,constraints