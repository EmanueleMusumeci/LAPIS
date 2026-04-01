"""
Deterministic trace generator based on PDDL-like rules.
This replaces the LLM-based trace generation with a rule-based approach
that guarantees consistency between actions and states.
"""

import re
from typing import List, Set, Tuple, Dict


class BlocksworldState:
    """Represents a state in the blocksworld domain."""
    
    def __init__(self):
        self.on_table: Set[str] = set()  # blocks on the table
        self.on: Dict[str, str] = {}  # on[X] = Y means X is on Y
        self.clear: Set[str] = set()  # blocks with nothing on top
        self.holding: str = None  # block being held (None if arm is empty)
    
    def copy(self):
        """Create a deep copy of this state."""
        new_state = BlocksworldState()
        new_state.on_table = self.on_table.copy()
        new_state.on = self.on.copy()
        new_state.clear = self.clear.copy()
        new_state.holding = self.holding
        return new_state
    
    def to_fluent_list(self) -> List[str]:
        """Convert state to list of fluent strings."""
        fluents = []
        
        # on_table fluents
        for block in sorted(self.on_table):
            fluents.append(f"on_table({block})")
        
        # on fluents
        for block, base in sorted(self.on.items()):
            fluents.append(f"on({block}, {base})")
        
        # clear fluents
        for block in sorted(self.clear):
            fluents.append(f"clear({block})")
        
        # holding fluent
        if self.holding:
            fluents.append(f"holding({self.holding})")
        else:
            fluents.append("arm_empty")
        
        return fluents
    
    def __str__(self):
        return "\n".join(self.to_fluent_list())


class BlocksworldTraceGenerator:
    """Generates traces from plans using deterministic PDDL-like rules."""
    
    def __init__(self):
        self.block_aliases = {}  # maps various names to canonical names
    
    def parse_initial_state(self, nl_description: str) -> BlocksworldState:
        """
        Parse the natural language description to extract initial state.
        This uses simple pattern matching.
        """
        state = BlocksworldState()
        
        # Extract blocks mentioned in the description
        # Common patterns: "block X", "X block", "first X", "second X", etc.
        blocks = set()
        
        # Pattern to find block descriptions
        block_patterns = [
            r'(\w+)\s+block(?:\s+number)?\s+(\d+)',  # "green block number 1", "green block 1"
            r'(\w+)\s+block',  # "green block", "purple block"
            r'the\s+(\w+)',  # "the purple", "the first green"
        ]
        
        lines = nl_description.lower().split('.')
        
        # Try to infer from common patterns in problem descriptions
        # "X is on the table" -> on_table(X)
        # "X is on top of Y" / "Y has X on top" -> on(X, Y)
        # "X is clear" / "nothing is on X" -> clear(X)
        
        for line in lines:
            line = line.strip()
            
            # Pattern: "X is/are on the table"
            if 'on the table' in line:
                # Extract what's on the table
                words = line.split()
                for i, word in enumerate(words):
                    if word in ['is', 'are'] and i > 0:
                        block_desc = ' '.join(words[:i])
                        block_name = self._extract_block_name(block_desc)
                        if block_name:
                            state.on_table.add(block_name)
                            state.clear.add(block_name)
            
            # Pattern: "X on top of Y" or "Y with X on top"
            if 'on top of' in line:
                parts = line.split('on top of')
                if len(parts) == 2:
                    upper = self._extract_block_name(parts[0])
                    lower = self._extract_block_name(parts[1])
                    if upper and lower:
                        state.on[upper] = lower
                        state.clear.add(upper)
                        if lower in state.clear:
                            state.clear.remove(lower)
        
        # Arm starts empty
        state.holding = None
        
        return state
    
    def _extract_block_name(self, text: str) -> str:
        """Extract canonical block name from text description."""
        text = text.strip().lower()
        
        # Remove common prefixes
        text = re.sub(r'the\s+', '', text)
        text = re.sub(r'a\s+', '', text)
        
        # Pattern: "color block number N" or "color block N"
        match = re.search(r'(\w+)\s+block(?:\s+number)?\s+(\d+)', text)
        if match:
            color = match.group(1)
            num = match.group(2)
            return f"{color}_{num}"
        
        # Pattern: "Nth color" (e.g., "first green", "second black")
        ordinals = {'first': '1', 'second': '2', 'third': '3', 'fourth': '4'}
        for ord_word, num in ordinals.items():
            if ord_word in text:
                color = text.replace(ord_word, '').strip()
                if color:
                    return f"{color}_{num}"
        
        # Pattern: "color block" (assume it's number 1)
        match = re.search(r'(\w+)\s+block', text)
        if match:
            color = match.group(1)
            return f"{color}_1"
        
        # Just a color name
        if text in ['red', 'green', 'blue', 'yellow', 'purple', 'black', 'white', 'orange', 'brown', 'grey', 'gray']:
            return f"{text}_1"
        
        return None
    
    def parse_action(self, action_str: str) -> Tuple[str, List[str]]:
        """
        Parse an action string into action name and parameters.
        
        Returns: (action_name, [param1, param2, ...])
        """
        action_str = action_str.strip().lower()
        
        # Remove numbering if present (e.g., "1. Pickup X" -> "Pickup X")
        action_str = re.sub(r'^\d+\.\s*', '', action_str)
        
        # Patterns for different action types
        # pickup(X) / pick up X / pickup X from the table
        if 'pickup' in action_str or 'pick up' in action_str:
            block = self._extract_block_from_action(action_str, 'pickup')
            return ('pickup', [block] if block else [])
        
        # putdown(X) / put down X / place X on the table
        if 'putdown' in action_str or 'put down' in action_str or 'place' in action_str:
            block = self._extract_block_from_action(action_str, 'putdown')
            return ('putdown', [block] if block else [])
        
        # stack(X, Y) / stack X on Y / place X on Y
        if 'stack' in action_str or 'place' in action_str:
            # Extract two blocks
            blocks = self._extract_two_blocks_from_action(action_str)
            if len(blocks) == 2:
                return ('stack', blocks)
        
        # unstack(X, Y) / unstack X from Y / remove X from Y
        if 'unstack' in action_str or 'remove' in action_str:
            blocks = self._extract_two_blocks_from_action(action_str)
            if len(blocks) == 2:
                return ('unstack', blocks)
        
        # If we can't parse, return unknown
        return ('unknown', [])
    
    def _extract_block_from_action(self, action_str: str, action_type: str) -> str:
        """Extract a single block name from an action string."""
        # Remove action keyword
        for keyword in [action_type, 'pickup', 'pick up', 'putdown', 'put down', 'place', 'from the table', 'on the table']:
            action_str = action_str.replace(keyword, ' ')
        
        return self._extract_block_name(action_str)
    
    def _extract_two_blocks_from_action(self, action_str: str) -> List[str]:
        """Extract two block names from an action string (for stack/unstack)."""
        # Split by common separators
        separators = [' on top of ', ' on ', ' from ', ' to ']
        
        for sep in separators:
            if sep in action_str:
                parts = action_str.split(sep, 1)
                if len(parts) == 2:
                    block1 = self._extract_block_name(parts[0])
                    block2 = self._extract_block_name(parts[1])
                    if block1 and block2:
                        return [block1, block2]
        
        return []
    
    def apply_action(self, state: BlocksworldState, action_name: str, params: List[str]) -> BlocksworldState:
        """
        Apply an action to a state and return the new state.
        Uses PDDL-like preconditions and effects.
        """
        new_state = state.copy()
        
        if action_name == 'pickup' and len(params) == 1:
            block = params[0]
            # Preconditions: on_table(block), clear(block), arm_empty
            if block in state.on_table and block in state.clear and state.holding is None:
                # Effects: holding(block), !on_table(block), !arm_empty
                new_state.on_table.remove(block)
                new_state.clear.remove(block)
                new_state.holding = block
        
        elif action_name == 'putdown' and len(params) == 1:
            block = params[0]
            # Preconditions: holding(block)
            if state.holding == block:
                # Effects: on_table(block), clear(block), arm_empty, !holding(block)
                new_state.on_table.add(block)
                new_state.clear.add(block)
                new_state.holding = None
        
        elif action_name == 'stack' and len(params) == 2:
            upper, lower = params
            # Preconditions: holding(upper), clear(lower)
            if state.holding == upper and lower in state.clear:
                # Effects: on(upper, lower), arm_empty, !holding(upper), !clear(lower), clear(upper)
                new_state.on[upper] = lower
                new_state.clear.remove(lower)
                new_state.clear.add(upper)
                new_state.holding = None
        
        elif action_name == 'unstack' and len(params) == 2:
            upper, lower = params
            # Preconditions: on(upper, lower), clear(upper), arm_empty
            if state.on.get(upper) == lower and upper in state.clear and state.holding is None:
                # Effects: holding(upper), clear(lower), !on(upper, lower), !arm_empty, !clear(upper)
                del new_state.on[upper]
                new_state.clear.add(lower)
                new_state.clear.remove(upper)
                new_state.holding = upper
        
        return new_state
    
    def generate_trace(self, plan: str, nl_description: str = None) -> Tuple[List[List[str]], str]:
        """
        Generate a deterministic trace from a plan.
        
        Args:
            plan: String with numbered actions (one per line)
            nl_description: Natural language description of initial state (optional)
        
        Returns:
            (trace, reasoning) where trace is a list of states (each state is a list of fluent strings)
        """
        # Parse plan into list of actions
        action_lines = [line.strip() for line in plan.strip().split('\n') if line.strip()]
        
        # Initialize state (TODO: parse from nl_description if provided)
        state = BlocksworldState()
        if nl_description:
            state = self.parse_initial_state(nl_description)
        
        # Generate initial state
        trace = [state.to_fluent_list()]
        reasoning_parts = [f"Initial State:\n{state}"]
        
        # Apply each action
        for i, action_line in enumerate(action_lines, 1):
            action_name, params = self.parse_action(action_line)
            
            if action_name == 'unknown':
                reasoning_parts.append(f"\nAction {i}: {action_line}\nWARNING: Could not parse action, state unchanged")
                trace.append(state.to_fluent_list())
                continue
            
            # Apply action
            new_state = self.apply_action(state, action_name, params)
            
            # Record reasoning
            reasoning_parts.append(
                f"\nAction {i}: {action_line}\n"
                f"Parsed as: {action_name}({', '.join(params)})\n"
                f"New State:\n{new_state}"
            )
            
            # Add to trace
            trace.append(new_state.to_fluent_list())
            state = new_state
        
        reasoning = "\n".join(reasoning_parts)
        return trace, reasoning


def deterministic_trace_generation(plan: str, nl_description: str = None) -> Tuple[str, List[List[str]]]:
    """
    Wrapper function that matches the signature of the original trace_generation.
    
    Args:
        plan: The plan as a string with numbered actions
        nl_description: Natural language description of the problem (optional)
    
    Returns:
        (reasoning, trace) tuple
    """
    generator = BlocksworldTraceGenerator()
    trace, reasoning = generator.generate_trace(plan, nl_description)
    return reasoning, trace
