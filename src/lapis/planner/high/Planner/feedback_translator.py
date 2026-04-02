from dotenv import load_dotenv
import os
load_dotenv()
from pydantic import BaseModel


class FeedbackTranslation(BaseModel):
    reasoning: str
    explanation: str
    how_to_fix: str


def translate_feedback_to_natural_language(technical_feedback, domain, problem, actions, goal, constraints, failed_plan, agent):
    """
    Translate technical LTL violation feedback into natural language that the planner can understand.
    Works with high-level constraint-focused plans.
    """
    system_prompt = """
RULE: Never write predicate(argument) format. Always describe in plain English.

You translate technical feedback into natural language for HIGH-LEVEL CONSTRAINT-FOCUSED plans.

CONTEXT: The plan you're analyzing contains HIGH-LEVEL actions where each step represents achieving a constraint or subgoal.
Each high-level action (e.g., "Put block A on block B") implicitly includes multiple low-level operations.

NAMING RULES (CRITICAL):
- NEVER use abbreviations like B1, G1, P1, R1, etc.
- ALWAYS use full natural language: "the black block", "green block number 1", "the first purple block"
- Be consistent with the plan's naming convention

FORBIDDEN patterns - if you write ANY of these, you fail:
- 'holding(black)' → MUST write: "you are holding the black block"
- 'on(purple1,black2)' → MUST write: "the purple block is on the black block"  
- 'not(on(X,Y))' → MUST write: "block X is not on block Y"
- 'clear(block)' → MUST write: "the block is clear" or "nothing is on the block"

RULE: Scan your output. If you see ANY word followed by parentheses like word(something), rewrite it in plain English.

Examples:
BAD: "'holding(black)' never occurred"
GOOD: "you never picked up the black block"

BAD: "At state 4, 'not(on(purple1,black2))' was true"  
GOOD: "After step 4, the purple block was no longer on the black block"

BAD: "make 'holding(black)' true"
GOOD: "pick up the black block"

OUTPUT FORMAT (for HIGH-LEVEL plans):
- "reasoning": Your translation process, analyzing which constraint was violated
- "explanation": A 1-2 sentence summary explaining which constraint failed and why
- "how_to_fix": Guidance on fixing the plan at the HIGH-LEVEL. Focus on:
  * Which constraint is not being satisfied
  * What high-level configuration change is needed
  * Where in the sequence the issue occurs
  
IMPORTANT FOR HIGH-LEVEL FEEDBACK:
- Don't suggest low-level atomic actions (pickup, putdown, stack, unstack)
- Suggest high-level configuration changes ("Put block A on block B earlier in the plan")
- Focus on constraint satisfaction order and missing constraints
- Think in terms of "which constraint is missing" or "wrong order of constraints"

Example feedback for high-level plan:
GOOD: "You need to achieve 'orange block on red block' before moving the black block"
GOOD: "Missing step: Put black block on red block at some point"
BAD: "You need to unstack the brown block first" (too low-level)

RULE: Your output must be readable by someone who has NEVER seen predicate logic. Use plain English only.
"""

    user_input = f"""
Domain: {domain}

Problem: {problem}

Available Low-Level Actions (for reference): {actions}

Goal: {goal}

Constraints (check which ones are violated):
{constraints}

Failed HIGH-LEVEL Plan:
{chr(10).join([f"{i+1}. {action}" for i, action in enumerate(failed_plan)])}

Technical Feedback:
{technical_feedback}

TASK:
1. Identify which constraint(s) failed
2. Explain what went wrong in plain English (1-2 sentences)
3. Provide HIGH-LEVEL guidance on how to fix:
   - Focus on which constraint is missing or in wrong order
   - Suggest high-level configuration changes, not atomic actions
   - Think: "which constraint needs to be satisfied?" not "which low-level action to add?"

Example HIGH-LEVEL fixes:
✅ "Missing: You need to put orange block on red block before step 2"
✅ "The constraint requiring black block on red block is never satisfied"
❌ "You need to pickup orange block and stack it on red block" (too low-level)

TRANSLATE TO PLAIN ENGLISH. No predicate(argument) format allowed.

Before submitting: search your explanation and how_to_fix for any ( ) parentheses with predicates. If found, rewrite in plain English.
"""

    response = agent.client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        seed=42,
        response_format=FeedbackTranslation,
    )
    
    result = response.choices[0].message.parsed

    reasoning = result.reasoning
    explanation = result.explanation
    how_to_fix = result.how_to_fix
    
    print('\n' + '='*80)
    print('FEEDBACK TRANSLATION')
    print('='*80)
    print('REASONING:')
    print(reasoning)
    print('EXPLAINATION:')
    print(explanation)
    print('HOW TO FIX:')
    print(how_to_fix)
    print('='*80 + '\n')
    
    return reasoning, explanation, how_to_fix