from dotenv import load_dotenv
import os
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel


class PlannerStepDescription(BaseModel):
    reasoning: str
    plan_step: str 


class PlannerDescription(BaseModel):
    reasoning: str
    plan: list[str]

    



def generate_plan_step(domain, problem, actions, goal, constraints, current_plan, agent, feedback=None, previous_attempts=None):
    """
    Generate a single step of the plan (constraint-focused, high-level).
    """
    system_prompt = """
You are an expert planning agent generating high-level constraint-focused plans step-by-step.

NAMING RULES (CRITICAL):
- NEVER use abbreviations like B1, G1, P1, R1, etc.
- ALWAYS use full natural language: "the first black block", "the green block number 1", "the purple block"
- Be consistent: if you say "black block 1" once, always say "black block 1" (not "B1" or "black1")

OUTPUT:
- "reasoning": Analyze what has been done so far, which constraints are satisfied, which remain. Determine the next constraint to satisfy.
- "plan_step": ONE high-level action that satisfies a constraint or achieves the goal, OR "COMPLETE" if all constraints and the goal are satisfied.

HIGH-LEVEL ACTION STYLE:
- Write actions like "Put block A on block B" (not "Pickup block A" then "Stack block A on block B")
- Each action represents achieving a specific constraint or subgoal
- Implicitly includes all necessary low-level steps

CONSTRAINT-FOCUSED APPROACH:
1. Review which constraints have been satisfied by the current plan
2. Identify the next unsatisfied constraint
3. Generate ONE high-level action to satisfy that constraint
4. If all constraints and goal are satisfied, output "COMPLETE"

CRITICAL - AVOID REPEATING CONFIGURATIONS:
- Don't create a step that undoes what was just achieved
- Don't repeat moving the same block unless necessary to satisfy a new constraint
- Check if goal and all constraints are already met → if yes, output "COMPLETE"

BANNED PHRASES:
"to satisfy the constraint", "to meet the requirement", "ensuring", "finally", "lastly"

EXAMPLES:
✅ "Put purple block on green block number 2"
✅ "Move black block to the table"
✅ "COMPLETE"

❌ "Pickup purple block from the table" (too low-level)
❌ "Stack purple block on green block to satisfy the constraint" (banned phrase)
"""

    user_input = f"""
Domain: {domain}

Problem: {problem}

Available Low-Level Actions (for reference only): {actions}

Goal: {goal}

Constraints (determine which constraint to satisfy next):
{constraints}

Current Plan (steps already planned):
{current_plan if current_plan else "No steps yet"}

TASK: Generate the next HIGH-LEVEL action to satisfy an unsatisfied constraint, or "COMPLETE" if done.
Remember: Each action should be high-level (e.g., "Put block A on block B"), not atomic low-level actions.
"""

    if feedback and previous_attempts:
        user_input += f"""
        FEEDBACK FROM PREVIOUS ATTEMPT:
        {feedback}

        You have made {len(previous_attempts)} previous attempt(s) that failed. Learn from these failures and generate a better plan.
        """

    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        seed=42,  # Fixed seed for deterministic results
        response_format=PlannerStepDescription,
    )
    description = response.choices[0].message.parsed
    
    print('PLAN GENERATION RESULT: ', description)
    reasoning = description.reasoning
    plan_step = description.plan_step


    return reasoning, plan_step





def plan_generation(domain, problem, actions, goal, abstraction, constraints, agent, feedback=None, previous_attempts=None):
    """
    Generate a plan as a sequence of high-level constraint-satisfying actions.
    Each step in the plan represents achieving a specific constraint or subgoal.
    """

    """
    Generate a plan as a sequence of high-level natural language actions.
    """
    #ABSTRACTION_INSTRUCTIONS
    low_abstraction_instructions = """

    EXAMPLE OF STEP-BY-STEP ACTION REASONING:
    1. Unstack the first brown block from the first grey block.
    - you are holding the brown block 1.
    - the grey block 1 is on top of red block 1 and is clear.
    - white block 1 is on the table with blue block 1 on top.
    - orange block 1 and orange block 2 are clear and on the table.
    """

    medium_abstraction_instructions = """
    -Your steps must not be elementary actions, but rather they must take into account a sub-goal that you want to achieve. 
    -Use a verb that indicates the purpose of the action. 

    EXAMPLE OF STEP-BY-STEP ACTION REASONING:
    The state of the world says that there are multiple blocks stacked on top of grey block 1.
    1. Clear the grey block 1 from the upper blocks.
    3. Clear red block 1 from upper blocks.
    2. Ensure the brown block 1 is on top of the red block 1.
    """

    high_abstraction_instructions = """
    - Each step must describe a desired world state or configuration, not an action.
    - Steps must be high-level and abstract, focusing on what should be true, not how to do it.
    - Each step must represent a meaningful change in the overall state of the world.
    - Use a verb that indicates the purpose of the step.

    EXAMPLE OF STEP-BY-STEP ACTION REASONING:
    1. Organize the blocks to have the yellow block stacked on the purple block.
    2. Ensure the red block is held while arranging the grey block.
    """

    if abstraction == 'low':
        abstraction_instructions = low_abstraction_instructions
    elif abstraction == 'medium':
        abstraction_instructions = medium_abstraction_instructions  
    elif abstraction == 'high': 
        abstraction_instructions = high_abstraction_instructions


    system_prompt_old = """
You are an expert planning agent generating HIGH-LEVEL CONSTRAINT-FOCUSED plans.

CORE PRINCIPLE: Each step in your plan should represent achieving a CONSTRAINT or SUBGOAL, NOT atomic low-level actions.

PLANNING APPROACH:
1. Analyze the initial state
2. Identify each constraint that must be satisfied
3. For each constraint, determine what HIGH-LEVEL configuration change is needed
4. Generate a plan where each step achieves one constraint (or part of the goal)

NAMING RULES (CRITICAL):
- NEVER use abbreviations like B1, G1, P1, R1, etc.
- ALWAYS use full natural language: "black block 1", "green block number 1", "purple block", "first black block"
- Be consistent throughout the entire plan with the same naming convention

HIGH-LEVEL ACTION STYLE:
Each action should describe WHAT configuration to achieve, not HOW to achieve it.
The action implicitly includes ALL necessary low-level steps (pickup, putdown, unstack, stack).

EXAMPLES:
❌ LOW-LEVEL (What we DON'T want):
1. Unstack brown block from red block
2. Put down brown block on the table
3. Pickup orange block from the table
4. Stack orange block on red block

✅ HIGH-LEVEL (What we WANT):
1. Put orange block on red block (implicitly: remove brown block first, pickup orange, stack it)
2. Put black block on red block (implicitly: remove orange first if needed)

CONSTRAINT-FOCUSED REASONING:
For each constraint, ask:
- What configuration does this constraint require?
- What is ONE high-level action that achieves this configuration?
- Write that as a step

During your reasoning process, write:
- Initial State Analysis: What objects exist and where are they?
- Goal Analysis: What is the final configuration required?
- Constraint Analysis: List each constraint and what configuration it requires
- Subgoal Sequence: For each constraint, determine the high-level action needed

OUTPUT:
- "reasoning": Your detailed thinking process following the structure above
- "plan": List of HIGH-LEVEL constraint-satisfying steps. Each step should be a complete configuration change, not an atomic action.

CRITICAL: The plan should be COMPACT. If you have N constraints, expect roughly N steps (plus achieving the goal).

EXAMPLE FULL REASONING:
Initial State: black block on table, brown block on red block, orange block on table
Goal: black block on table (already satisfied)
Constraints: 
- Constraint 1: orange block on red block at some point
- Constraint 2: black block on red block at some point

Subgoal Sequence:
1. To satisfy Constraint 1: Put orange block on red block
2. To satisfy Constraint 2: Put black block on red block  
3. To achieve goal: Put black block on table

Final plan:
1. Put orange block on red block
2. Put black block on red block
3. Put black block on table
"""

    system_prompt_old_HIGH_LEVEL = """
You are an expert planning agent generating HIGH-LEVEL CONSTRAINT-FOCUSED plans.

You will receive in input  a domain, a problem, a set of low-level actions, a goal, and a set of constraints.
Your goal is to build a plan that must be compact and high-level.
At each step of the plan, you must describe how to achieve a specific cosntraint or subgoal, without providing low-level details.
The last step of the generated plan must be the one that achieves the goal.

OUTPUT:
- "reasoning": Your detailed thinking process following the structure above. 
- "plan": List of HIGH-LEVEL constraint-satisfying steps. Each step should be a complete configuration change, not an atomic action.

    In the reasoning part, you can write a prototype plan in which you explain why you are taking each action.
    In the plan output, you must provide a clean version of the plan without any explanations.

RULES:
    -Do not use abbreviations and describe the elements of the problem in full natural language.
    -Each action should describe WHAT configuration to achieve, not HOW to achieve it.
    -Do not concatenate multiple actions in a single step.
    -Do not provide a description of why are you taking that action in the final plan.

CONSTRAINT-FOCUSED REASONING:
For each constraint, ask:
    - What configuration does this constraint require?
    - What is ONE high-level action that achieves this configuration?
    - Write that as a step

During your reasoning process, write:
- Initial State Analysis: What objects exist and where are they?
- Goal Analysis: What is the final configuration required?
- Constraint Analysis: List each constraint and what configuration it requires
- Subgoal Sequence: For each constraint, determine the high-level action needed


EXAMPLE OF FINAL PLAN:
Example 1:
1. orange block is moved on red block
2. black block is moved on the table
3. black block is moved on red block

Example 2:
1. Move on the cell with the key
2. Pick up the key
3. Move to the door
4. Unlock the door with the key

As you can see from the examples, each step must be a high-level action that achieves a specific constraint or subgoal without further explanation or action concatenation.
Write like in these examples.
"""

    system_prompt = f"""
    You are an expert planning agent generating high-level plans.
    You have to reason about the best sequence of actions to achieve the goal while satisfying all constraints.
    During your reasoning, write the following informations and use them to generate the final plan:
    - Initial State Analysis
    - Goal Analysis
    - Constraint Analysis
    - Action Analysis

    Then, generate a HIGH-LEVEL PLAN as a sequence of steps.
    After each step, exaustively describe the state of the world and why are you doing that action.

    When the entire reasoning process is done, output the final "plan" by telling only the actions.

    OUTPUT:
    - "reasoning": Your thinking process - analyze initial state, goal, constraints, and how your plan addresses everything
    - "plan": List of HIGH-LEVEL steps describing the actions to perform. Do not add any explanations here.

        In the reasoning part, you can write a prototype plan in which you explain why you are taking each action.
        In the plan output, you must provide a clean version of the plan without any explanations.

    RULES:
        -Do not use abbreviations and describe the elements of the problem in full natural language.
        -Do not concatenate multiple actions in a single step.
        -Do not provide a description of why are you taking that action in the final plan.

    During your reasoning process, write:
    - Initial State Analysis: What objects exist and where are they?
    - Goal Analysis: What is the final configuration required?
    - Constraint Analysis: List each constraint and what configuration it requires
    - Subgoal Sequence: For each constraint, determine the needed sequence of actions to achieve it.


    IMPORTANT:
    - Keep in mind that the goal is the last thing to achieve.
    {abstraction_instructions}
    """



    '''
    HIGH-LEVEL CONSTRAINT-FOCUSED PLANNING:

    The plan should be organized around CONSTRAINTS, not atomic actions.
    Each step should achieve a constraint or move toward the goal.

    CONSTRAINT-BASED APPROACH:
    1. List all constraints
    2. For each constraint, determine what configuration it requires
    3. Create ONE high-level action per constraint
    4. Add final action(s) to achieve the goal

    BANNED PHRASES:
    "to satisfy the constraint", "to meet the requirement", "ensuring the constraint", "finally", "lastly", "in order to"

    HIGH-LEVEL vs LOW-LEVEL:
    ❌ LOW-LEVEL (atomic actions):
    1. Pickup block A
    2. Stack block A on block B
    3. Unstack block C from block D
    4. Putdown block C

    ✅ HIGH-LEVEL (constraint-focused):
    1. Put block A on block B (includes pickup and stack implicitly)
    2. Move block C to the table (includes unstack and putdown implicitly)

    Each high-level action represents achieving a specific constraint or subgoal.
    The low-level details (pickup, putdown, unstack, stack) are implicit.
    '''


    user_input = f"""
Domain: {domain}

Problem: {problem}

Available Low-Level Actions (for reference only - your plan should be high-level): {actions}

Goal: {goal}

Constraints (each constraint should typically correspond to one step in your plan):
{constraints}

INSTRUCTIONS:
1. Read each constraint carefully
2. Determine what configuration each constraint requires
3. Generate a HIGH-LEVEL plan where each step achieves one constraint (or the goal)
4. Each step should describe WHAT configuration to achieve, not HOW (no atomic actions)
5. The plan should be COMPACT - roughly one step per constraint plus achieving the goal
"""

    if feedback and previous_attempts:
        user_input += f"""
        FEEDBACK FROM PREVIOUS ATTEMPT:
        {feedback}

        You have made {len(previous_attempts)} previous attempt(s) that failed. Learn from these failures and generate a better plan.
        """

    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        seed=42,
        response_format=PlannerDescription,
    )
    description = response.choices[0].message.parsed
    
    print('PLAN GENERATION RESULT: ', description)
    reasoning = description.reasoning
    plan = description.plan
    
    stringplan = ", ".join(plan)

    final_plan = [s.strip() for s in stringplan.split(",") if s.strip()]

    # Number and join with new lines
    plan = "\n".join(f"{i+1}. {step}" for i, step in enumerate(final_plan))

    return reasoning, plan
    

