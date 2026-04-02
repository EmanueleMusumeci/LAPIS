from dotenv import load_dotenv
import os
load_dotenv()  # loads variables from .env into environment
from pydantic import BaseModel


class FormulaDescription(BaseModel):
    reasoning: str
    formula: str
    fluent_syntax: str


def ltl_formula_generation(domain, goal, constraints, agent):
    system_prompt = """
You are an expert in Linear Temporal Logic (LTL) who can translate planning goals and constraints into formal LTL formulas.

You will receive:
- **Domain**: A description of the planning domain (what actions are possible, how the world works)
- **Goal**: What needs to be achieved
- **Constraints**: Additional conditions that must be satisfied during plan execution

Your task is to generate an LTL formula that captures both the goal and the constraints.

LTL OPERATORS:
- **F** (Finally): F(p) means "p will be true at some point in the future"
- **G** (Globally): G(p) means "p is always true"
- **X** (Next): X(p) means "p is true in the next state"
- **U** (Until): p U q means "p is true until q becomes true"
- **&** (And): p & q means "both p and q are true"
- **|** (Or): p | q means "either p or q (or both) are true"
- **!** (Not): !p means "p is not true"
- **->** (Implies): p -> q means "if p is true, then q must be true"

CRITICAL: TEMPORAL PRECEDENCE vs CONSEQUENCE
This is the most common source of errors in LTL formula translation!

**PRECEDENCE CONSTRAINTS** (B must happen BEFORE A):
- Natural language: "If A holds in some state, then there must be an EARLIER state where B is true"
- Natural language: "Before A happens, B must hold"
- **WRONG formula**: G(A -> F(B))  ← This says B happens AFTER A!
- **CORRECT formula**: B U A  ← This says B holds UNTIL A becomes true
- **Alternative correct**: !A U (A & B) or (B | !A) U A depending on whether B must still hold when A becomes true

Examples:
- "Before the block is on the table, it must be held" → holding U on_table
- "If x is clear, there was an earlier state where y was picked" → picked_y U clear_x

**CONSEQUENCE CONSTRAINTS** (B must happen AFTER or AT A):
- Natural language: "If A holds in state s, then B must hold at s or AFTER s"
- Natural language: "Whenever A happens, B must follow"
- **CORRECT formula**: G(A -> F(B))
- **Alternative**: G(!A | F(B))

Examples:
- "If block is on table, it will eventually be moved" → G(on_table -> F(!on_table))
- "Whenever x is picked, y will be clear later" → G(holding_x -> F(clear_y))

**KEY DISTINCTION**:
- "earlier/before/prior" → Use UNTIL (U) operator
- "after/later/eventually following" → Use IMPLIES with F: G(A -> F(B))

GOAL vs CONSTRAINTS:
- **Goal**: Must be true in the FINAL state. Use F(goal) to ensure it's eventually reached.
- **Simple Constraints**: "X must happen at least once" → F(X)
- **Precedence Constraints**: "Y must happen before X" → Y U X
- **Consequence Constraints**: "After X, Y must happen" → G(X -> F(Y))
- **Always true**: "X must always hold" → G(X)

OBJECT NAMING — CRITICAL SYNTAX RULE:
You MUST copy object identifiers VERBATIM from the Domain and Goal description. Do NOT shorten, abbreviate, or rephrase them.

Syntax pattern (PREDICATE_N and OBJECT_N are fully generic placeholders — substitute with actual names from the input):

  CORRECT  →  PREDICATE_1(OBJECT_1),  PREDICATE_2(OBJECT_1, OBJECT_2)
  WRONG    →  PREDICATE_1(OBJ_1),     PREDICATE_2(obj1, obj2),  PREDICATE_1(object 1)

The rule: if the Domain names an object "OBJECT_1", every predicate in your formula referencing it must spell it exactly "OBJECT_1" — no shorter aliases, no space/underscore/capitalisation variants.

In the "fluent_syntax" field, enumerate the exact predicate templates you used, substituting PREDICATE_N and OBJECT_N with the real names from this problem (e.g. PREDICATE_1(OBJECT_1, OBJECT_2)). This list is the canonical naming contract that the trace generator must follow.

OUTPUT:
- "reasoning": Explain your step-by-step thought process. For each constraint, explicitly identify whether it's a PRECEDENCE or CONSEQUENCE constraint and why you chose specific operators.

- "formula": The complete LTL formula. Use standard LTL syntax with the operators described above.

- "fluent_syntax": List the exact predicate templates used in the formula (with the real predicate and object names from this problem). This will be used by the trace generator to enforce identical naming.
"""

    user_input = f"""
Domain: {domain}

Goal: {goal}

Constraints: {constraints}
"""

    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        seed=42,
        response_format=FormulaDescription,
    )
    description = response.choices[0].message.parsed
    
    print('FORMULA GENERATION RESULT: ', description)
    reasoning = description.reasoning
    formula = description.formula
    fluent_syntax = description.fluent_syntax
    
    return reasoning, formula, fluent_syntax