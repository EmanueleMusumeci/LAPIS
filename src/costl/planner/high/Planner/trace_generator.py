from dotenv import load_dotenv
import os
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel
from fluent_extractor import extract_fluents_from_ltl, get_fluent_pattern_examples


class TracerDescription(BaseModel):
    reasoning: str
    trace: list[list[str]]

class InitStateDescription(BaseModel):
    reasoning: str
    init_state: str

def init_trace(domain,problem,ltl_formula, fluent_syntax, agent):
    """
    Generate the first state of a trace.
    """
    
    
    system_prompt = """
You are an expert in planning and state representation. Your task is to generate the complete initial state of the given domain and problem.

A state represents ALL fluents (facts) that are either true or false at a given point in the plan. You must be EXHAUSTIVE and track every possible fluent.

You will receive:
- **Domain**: A description of the domain that you will work with
- **Problem**: The natural language description of the problem
- **LTL Formula**: Contains fluents that must be tracked

Your task:
1. Identify ALL fluents mentioned in the LTL formula
2. Identify ALL objects (blocks, locations, etc.) in the problem
3. For EACH possible fluent involving these objects, determine if it's true or false in the initial state
4. Express each fluent using the EXACT SAME SYNTAX as used in the LTL formula

OUTPUT:
- "reasoning": Explain your step-by-step thinking. List ALL objects, then for EACH possible fluent, state whether it's true or false and why.

- "init_state": A COMPLETE set of fluent strings representing the initial state. Include:
  * ALL fluents that are TRUE (e.g., "onTable(red)", "clear(blue)")
  * This must be exhaustive - every relevant fluent about every object must be considered

CRITICAL RULES:
1. Be EXHAUSTIVE - include fluents for EVERY object and EVERY relationship
2. Fluent syntax must EXACTLY match the LTL formula syntax
3. For each object, consider: position (on table/on another object), whether you're holding it, whether it's clear, etc.
4. If the formula uses "onTop(a,b)", use that exact syntax, not "on(a,b)" or "a is on b"
5. Track the arm state: if not holding anything, include empty fluents; if holding something, include holding(X)

NAMING CONTRACT — NON-NEGOTIABLE SYNTAX RULE:
Every fluent string MUST be character-for-character identical to the predicate templates in the LTL formula. Do NOT invent aliases, abbreviations, or alternative spellings.

Syntax pattern (PREDICATE_N and OBJECT_N are fully generic placeholders):

  CORRECT  →  PREDICATE_1(OBJECT_1),  PREDICATE_2(OBJECT_1, OBJECT_2)
  WRONG    →  PREDICATE_1(OBJ_1),     PREDICATE_2(obj1, obj2),  PREDICATE_1(object 1)
"""

    user_input = f"""

Domain: {domain}

Problem: {problem}

LTL Formula: {ltl_formula}

Fluent Syntax Meaning: {fluent_syntax}

Generate the the the first state of this problem using the exact fluent syntax from the formula.
"""
    
    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        seed=42,
        response_format=InitStateDescription,
    )
    output = response.choices[0].message.parsed
    
    reasoning = output.reasoning
    init_state = output.init_state
    
    return reasoning,init_state



def trace_generation(plan, ltl_formula, fluent_syntax, agent, problem=None, domain=None):
    """
    Generate a trace (sequence of states) from a high-level constraint-focused plan.
    The trace has exactly N+1 states (initial state + one state per plan step).
    Each state is represented as a list of fluents that are true in that state.
    """
    
    system_prompt = """
You are an expert in planning and state representation. Your task is to generate a trace from a HIGH-LEVEL plan.

CRITICAL RULE: The trace must have EXACTLY (N+1) states, where N is the number of steps in the plan:
- State 0: Initial state (MUST BE COMPLETE AND NON-EMPTY)
- State 1: After executing plan step 1
- State 2: After executing plan step 2
- ...
- State N: After executing plan step N

NO INTERMEDIATE STATES! One plan step = One state transition.

A trace is a sequence of states, where each state represents the fluents (facts) that are CERTAINLY TRUE at that point.

You will receive:
- **Domain**: Description of the domain and its physics
- **Problem**: Description of the specific problem instance with INITIAL STATE
- **Plan**: A sequence of HIGH-LEVEL actions (may be abstract like "Hold X" or specific like "Put X on Y")
- **LTL Formula**: The temporal logic formula that contains all fluents that must be tracked
- **Fluent Syntax**: Explanation of what each fluent means

⚠️ CRITICAL: STATE 0 (INITIAL STATE) MUST NEVER BE EMPTY ⚠️

The problem description contains the INITIAL STATE configuration. You MUST:
1. Read the problem description carefully to find what blocks/objects exist and their initial positions
2. For EVERY object mentioned, determine its initial state
3. Express these using the fluent syntax from the LTL formula
4. State 0 should typically have 5-15 fluents depending on the number of objects

Example initial state for blocksworld:
- If "block A is on the table" → include: on_table(A), clear(A) [if nothing on top]
- If "block B is on top of block C" → include: on(B, C), !clear(C), clear(B) [if nothing on B]
- If "arm is empty" → include this fact if tracked in formula
- For EVERY block: determine if it's on table, on another block, clear, being held

DO NOT leave state 0 empty! The initial state is the foundation for all subsequent states.

NAMING RULES (CRITICAL):
- NEVER use abbreviations like B1, G1, P1, R1, etc.
- ALWAYS use full natural language matching the plan: "black block 1", "green block number 1", "purple block"
- Be consistent with naming from the plan - if plan says "black block 1", use "black block 1" in fluents
- Match the exact names used in the LTL formula fluents

HANDLING HIGH-LEVEL ACTIONS - KEY PRINCIPLE:
For each plan step, determine what fluents are CERTAINLY TRUE after that step completes.
- If you can infer a fluent with certainty, include it
- If a fluent's value is uncertain or depends on implementation details you don't know, only include what you're certain about

Examples:
- "Put orange block on red block" → CERTAINLY: on(orange, red), !on_table(orange), !holding(orange)
- "Hold green block" → CERTAINLY: holding(green), !on_table(green)
- You may not know the exact state of OTHER blocks unless it's logically required

Your task:
1. ⚠️ FIRST PRIORITY: Parse the problem description to determine the COMPLETE INITIAL STATE (state 0)
   - Identify ALL objects (blocks, locations, etc.)
   - For EACH object, determine its position, status (clear/not clear), etc.
   - Express ALL of these facts using the fluent syntax from the formula
2. Identify ALL fluents from the LTL formula that need tracking
3. For EACH plan step:
   a. Determine what fluents are CERTAINLY TRUE after this step
   b. Update the state to reflect only what you're certain about
   c. Include derived predicates that can be computed from certain base fluents
4. Express each fluent using EXACT SAME SYNTAX as in the LTL formula

OUTPUT:
- "reasoning": 
  * START with analysis of the initial state from problem description
  * Then for EACH plan step, explain:
    - What the action is trying to achieve
    - What fluents become certainly true after this step
    - What fluents become certainly false after this step
    - The resulting state after this step

- "trace": A list of EXACTLY (N+1) states, where N is the number of plan steps. 
  * State 0 MUST be comprehensive based on problem description (NEVER empty!)
  * Each subsequent state contains fluents that are CERTAINLY TRUE after that action
  * Each fluent must use the exact syntax from the LTL formula

CRITICAL RULES:
1. Include only fluents you're certain about based on the plan step
2. Each state should reflect the configuration after that plan step completes
3. Derived predicates must be computed from base fluents
4. Fluent syntax must EXACTLY match the LTL formula
5. The trace length must be: number of plan steps + 1 (for initial state)

NAMING CONTRACT — NON-NEGOTIABLE SYNTAX RULE:
Every fluent string in the trace MUST be character-for-character identical to the predicate templates listed in "Fluent Syntax Meaning". Do NOT invent aliases, abbreviations, or alternative spellings.

Syntax pattern (PREDICATE_N and OBJECT_N are fully generic placeholders):

  CORRECT  →  PREDICATE_1(OBJECT_1),  PREDICATE_2(OBJECT_1, OBJECT_2)
  WRONG    →  PREDICATE_1(OBJ_1),     PREDICATE_2(obj1, obj2),  PREDICATE_1(object 1)

The "Fluent Syntax Meaning" field you receive IS the naming contract — copy predicate names and object identifiers exactly as written there.

MAINTAIN CONSISTENCY: Each state should reflect what is certainly true after that plan step, without inventing intermediate sub-actions.
"""

    # Extract fluents from formula to ensure completeness
    required_fluents = extract_fluents_from_ltl(ltl_formula)
    fluent_examples = get_fluent_pattern_examples(ltl_formula)
    
    fluent_list = "\n".join([f"  - {f}: {', '.join(fluent_examples.get(f, ['(pattern not shown)']))}" 
                              for f in sorted(required_fluents)])
    
    user_input = f"""
⚠️⚠️⚠️ CRITICAL: STATE 0 (INITIAL STATE) MUST NOT BE EMPTY ⚠️⚠️⚠️

Read the problem description below VERY CAREFULLY to extract the initial configuration of ALL objects.

Domain: {domain if domain else "Not provided - infer from actions"}

Problem Description (READ THIS to build State 0): 
{problem if problem else "Not provided - assume minimal initial state"}

Plan ({len(plan.split(chr(10)))} steps - your trace must have {len(plan.split(chr(10))) + 1} states):
{chr(10).join([f"{i+1}. {action}" for i, action in enumerate(plan.split(chr(10)))])}

LTL Formula: {ltl_formula}

Fluent Syntax Meaning: {fluent_syntax}

REQUIRED FLUENTS (track these when you're certain about their values):
{fluent_list}

CRITICAL INSTRUCTIONS FOR STATE 0 (INITIAL STATE):
1. ⚠️ Read the "Problem Description" above and identify ALL objects mentioned
2. ⚠️ For EACH object, determine its initial position/state from the description
3. ⚠️ Express ALL these facts using the fluent syntax from the LTL formula
4. ⚠️ State 0 should have multiple fluents (typically 5-15) - NEVER leave it empty!
5. ⚠️ If problem says "block A is on table", include fluents about A (on_table, clear, etc.)

CRITICAL INSTRUCTIONS FOR SUBSEQUENT STATES:
1. Generate EXACTLY {len(plan.split(chr(10))) + 1} states (initial + one per plan step)
2. NO INTERMEDIATE STATES - each plan step produces exactly one state
3. For each plan step, include only fluents you're CERTAIN about after that step
4. If the plan says "Put X on Y", then after that step: on(X,Y) is certainly true
5. If the plan says "Hold X", then after that step: holding(X) is certainly true
6. Don't invent sub-actions or intermediate states
7. Use EXACT fluent syntax from the formula
8. Compute derived predicates based on the fluents you know

Example: If plan has 4 steps, generate exactly 5 states (state 0, 1, 2, 3, 4).
"""
    
    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        seed=42,  # Fixed seed for deterministic results
        response_format=TracerDescription,
    )
    output = response.choices[0].message.parsed
    
    reasoning = output.reasoning
    trace = output.trace
    
    return reasoning,trace

    
