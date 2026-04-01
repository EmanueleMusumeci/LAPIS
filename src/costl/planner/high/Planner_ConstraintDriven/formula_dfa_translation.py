"""
Self-contained example script to translate an LTL formula using SPOT.

What it does:
- Calls `ltl2tgba` to translate an LTL formula into an automaton (HOA format).
- Optionally asks SPOT for a deterministic automaton.
- Prints a compact summary (states/AP/start/acceptance/transitions).
- Optionally saves HOA and DOT outputs.

Notes:
- For standard LTL over infinite traces, SPOT returns omega-automata (e.g., TGBA/Buchi),
  not a classic DFA in general.
- Deterministic output is requested via SPOT when possible.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class SpotToolError(RuntimeError):
	"""Raised when a SPOT binary is missing or a SPOT command fails."""

	pass


def _to_safe_ap_name(name: str) -> str:
	"""Convert an arbitrary proposition token into a SPOT-safe AP identifier."""

	cleaned = re.sub(r"[^A-Za-z0-9_]", "_", name)
	cleaned = re.sub(r"_+", "_", cleaned).strip("_")
	return cleaned or "ap"


def normalize_formula_for_spot(formula: str) -> tuple[str, dict[str, str]]:
	"""
	Normalize common planner/LTL syntax into SPOT-compatible syntax.

	Conversions:
	- AND/OR/NOT -> &/|/!
	- predicate(arg1, arg2, ...) -> predicate__arg1__arg2

	Returns:
		(normalized_formula, ap_display_map)
	where ap_display_map maps internal SPOT AP names to readable predicate syntax.
	"""

	normalized = formula
	ap_display_map: dict[str, str] = {}

	# Normalize boolean keywords often produced by LLM/planner outputs.
	normalized = re.sub(r"\bAND\b", "&", normalized, flags=re.IGNORECASE)
	normalized = re.sub(r"\bOR\b", "|", normalized, flags=re.IGNORECASE)
	normalized = re.sub(r"\bNOT\b", "!", normalized, flags=re.IGNORECASE)

	# Replace predicate-style atoms with plain atomic propositions.
	# Example: onTop(purple, black) -> onTop__purple__black
	pred_call_pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*([A-Za-z0-9_\s,]+)\s*\)")

	def _replace_pred_call(match: re.Match[str]) -> str:
		name = match.group(1)
		args_text = match.group(2)
		args = [arg.strip() for arg in args_text.split(",") if arg.strip()]
		if not args:
			return name
		atom = "__".join([name, *args])
		safe_atom = _to_safe_ap_name(atom)
		ap_display_map[safe_atom] = f"{name}({', '.join(args)})"
		return safe_atom

	normalized = pred_call_pattern.sub(_replace_pred_call, normalized)
	return normalized, ap_display_map


def _require_tool(tool_name: str) -> None:
	"""Ensure a required SPOT executable is available in PATH."""

	if shutil.which(tool_name) is None:
		raise SpotToolError(
			f"Required SPOT tool not found: '{tool_name}'. "
			"Install SPOT and ensure the binaries are in PATH."
		)


def _run_command(cmd: list[str], stdin_text: Optional[str] = None) -> str:
	"""Run a subprocess and return stdout; raise SpotToolError on non-zero exit."""

	# `text=True` means stdin/stdout are plain Python strings.
	result = subprocess.run(
		cmd,
		input=stdin_text,
		text=True,
		capture_output=True,
		check=False,
	)
	if result.returncode != 0:
		raise SpotToolError(
			"SPOT command failed:\n"
			f"  Command: {' '.join(cmd)}\n"
			f"  Exit code: {result.returncode}\n"
			f"  STDERR:\n{result.stderr.strip()}"
		)
	return result.stdout


def ltl_to_hoa(formula: str, deterministic: bool = False) -> str:
	"""Translate an LTL formula to HOA using SPOT's `ltl2tgba`."""

	_require_tool("ltl2tgba")

	# `--hoa`: machine-readable automaton format.
	# `-f`: formula passed directly as CLI argument.
	cmd = ["ltl2tgba", "--hoa", "-f", formula]
	if deterministic:
		# Determinization is requested when feasible for the input formula/class.
		cmd.append("--deterministic")

	return _run_command(cmd)


def hoa_to_state_based_acceptance(hoa_text: str) -> str:
	"""Convert HOA to state-based acceptance (sbacc) for clearer visualization."""

	_require_tool("autfilt")
	return _run_command(["autfilt", "--sbacc"], stdin_text=hoa_text)


def hoa_to_dot(hoa_text: str) -> str:
	"""Convert HOA text into DOT graph format using SPOT's `autfilt`."""

	_require_tool("autfilt")
	return _run_command(["autfilt", "--dot"], stdin_text=hoa_text)


def dot_to_image(dot_text: str, output_path: Path, image_format: str) -> None:
	"""Render DOT text to an image file using Graphviz `dot`."""

	_require_tool("dot")
	cmd = ["dot", f"-T{image_format}", "-o", str(output_path)]
	_ = _run_command(cmd, stdin_text=dot_text)


def parse_hoa_summary(hoa_text: str) -> dict[str, str | int | list[str]]:
	"""
	Extract a lightweight summary from HOA output.

	Returned fields are intentionally simple so they can be printed/logged directly.
	"""

	# Defaults are placeholders when some header fields are absent.
	summary: dict[str, str | int | list[str]] = {
		"states": "?",
		"start": "?",
		"ap_count": "?",
		"ap_names": [],
		"acceptance": "?",
		"transitions": 0,
	}

	states_match = re.search(r"^States:\s+(\d+)", hoa_text, flags=re.MULTILINE)
	start_match = re.search(r"^Start:\s+(.+)$", hoa_text, flags=re.MULTILINE)
	ap_match = re.search(r'^AP:\s+(\d+)\s+(.*)$', hoa_text, flags=re.MULTILINE)
	acc_match = re.search(r"^Acceptance:\s+(.+)$", hoa_text, flags=re.MULTILINE)

	if states_match:
		summary["states"] = int(states_match.group(1))
	if start_match:
		summary["start"] = start_match.group(1).strip()
	if ap_match:
		summary["ap_count"] = int(ap_match.group(1))
		ap_names = re.findall(r'"([^"]+)"', ap_match.group(2))
		summary["ap_names"] = ap_names
	if acc_match:
		summary["acceptance"] = acc_match.group(1).strip()

	transitions = 0
	in_body = False
	for line in hoa_text.splitlines():
		# In HOA, transitions are listed in the BODY section.
		if line.strip() == "--BODY--":
			in_body = True
			continue
		if line.strip() == "--END--":
			break
		if in_body and "[" in line:
			# Transition lines usually contain a guard in brackets, e.g. [0&!1] 2.
			transitions += 1
	summary["transitions"] = transitions
	return summary


def parse_hoa_graph(hoa_text: str) -> tuple[list[int], set[int], dict[int, list[int]]]:
	"""
	Parse HOA text into a lightweight directed graph.

	Returns:
		(start_states, accepting_states, adjacency)
	"""
	start_states: list[int] = []
	accepting_states: set[int] = set()
	adjacency: dict[int, list[int]] = {}

	start_match = re.search(r"^Start:\s+(.+)$", hoa_text, flags=re.MULTILINE)
	if start_match:
		# Handles simple start states and universal syntax by extracting all integers.
		start_states = [int(value) for value in re.findall(r"\d+", start_match.group(1))]

	in_body = False
	current_state: Optional[int] = None
	for raw_line in hoa_text.splitlines():
		line = raw_line.strip()
		if line == "--BODY--":
			in_body = True
			continue
		if line == "--END--":
			break
		if not in_body:
			continue

		if line.startswith("State:"):
			state_match = re.match(r"State:\s+(\d+)", line)
			if state_match is None:
				current_state = None
				continue
			current_state = int(state_match.group(1))
			adjacency.setdefault(current_state, [])
			# In sbacc mode, accepting states are typically annotated as {0} on State lines.
			if "{" in line and "}" in line:
				accepting_states.add(current_state)
			continue

		if current_state is None:
			continue

		transition_match = re.match(r"\[.*\]\s+(.+)$", line)
		if transition_match is None:
			continue
		# Handles standard destination and universal destinations by collecting all integers.
		dest_states = [int(value) for value in re.findall(r"\d+", transition_match.group(1))]
		if dest_states:
			adjacency.setdefault(current_state, []).extend(dest_states)

	# Remove duplicate outgoing destinations while preserving order.
	for state, targets in adjacency.items():
		seen: set[int] = set()
		unique_targets: list[int] = []
		for target in targets:
			if target in seen:
				continue
			seen.add(target)
			unique_targets.append(target)
		adjacency[state] = unique_targets

	return start_states, accepting_states, adjacency


def parse_hoa_transitions(hoa_text: str) -> tuple[list[int], dict[int, list[tuple[str, list[int]]]]]:
	"""Parse HOA transitions with guards: state -> [(guard, destinations), ...]."""

	start_states: list[int] = []
	transitions: dict[int, list[tuple[str, list[int]]]] = {}

	start_match = re.search(r"^Start:\s+(.+)$", hoa_text, flags=re.MULTILINE)
	if start_match:
		start_states = [int(value) for value in re.findall(r"\d+", start_match.group(1))]

	in_body = False
	current_state: Optional[int] = None
	for raw_line in hoa_text.splitlines():
		line = raw_line.strip()
		if line == "--BODY--":
			in_body = True
			continue
		if line == "--END--":
			break
		if not in_body:
			continue

		if line.startswith("State:"):
			state_match = re.match(r"State:\s+(\d+)", line)
			if state_match is None:
				current_state = None
				continue
			current_state = int(state_match.group(1))
			transitions.setdefault(current_state, [])
			continue

		if current_state is None:
			continue

		transition_match = re.match(r"\[(.*)\]\s+(.+)$", line)
		if transition_match is None:
			continue

		guard = transition_match.group(1).strip()
		dest_states = [int(value) for value in re.findall(r"\d+", transition_match.group(2))]
		if dest_states:
			transitions.setdefault(current_state, []).append((guard, dest_states))

	return start_states, transitions


def parse_true_atoms(state_true_args: Optional[list[str]]) -> set[str]:
	"""Parse --state-true arguments (repeatable and comma-separated)."""

	atoms: set[str] = set()
	if not state_true_args:
		return atoms

	for chunk in state_true_args:
		for raw_item in chunk.split(","):
			item = raw_item.strip()
			if item:
				atoms.add(item)
	return atoms


def parse_trace_true_atoms(trace_state_true_args: Optional[list[str]]) -> list[set[str]]:
	"""
	Parse --trace-state-true arguments.

	Each flag occurrence corresponds to one trace state.
	Within each occurrence, atoms can be comma-separated.
	"""

	trace: list[set[str]] = []
	if not trace_state_true_args:
		return trace

	for chunk in trace_state_true_args:
		state_atoms: set[str] = set()
		for raw_item in chunk.split(","):
			item = raw_item.strip()
			if item:
				state_atoms.add(item)
		trace.append(state_atoms)
	return trace


def split_top_level(text: str, sep: str = ",") -> list[str]:
	"""Split text by separator only at top level (outside nested brackets)."""

	parts: list[str] = []
	current: list[str] = []
	depth = 0
	openers = "([{"
	closers = ")] }".replace(" ", "")
	matching = {")": "(", "]": "[", "}": "{"}
	stack: list[str] = []

	for char in text:
		if char in openers:
			stack.append(char)
			depth += 1
			current.append(char)
			continue
		if char in closers:
			if stack and stack[-1] == matching[char]:
				stack.pop()
				depth -= 1
			current.append(char)
			continue
		if char == sep and depth == 0:
			parts.append("".join(current).strip())
			current = []
			continue
		current.append(char)

	last = "".join(current).strip()
	if last:
		parts.append(last)
	return parts


def parse_trace_argument(trace_arg: str) -> list[set[str]]:
	"""
	Parse single --trace argument in list-style format.

	Supported examples:
	- [(holding(green_block_1)), (holding(black_block_1))]
	- [(!onTable(purple_block_1),holding(green_block_1)), (holding(black_block_1))]
	"""

	text = trace_arg.strip()
	if not (text.startswith("[") and text.endswith("]")):
		raise ValueError("Trace must start with '[' and end with ']'.")

	inner = text[1:-1].strip()
	if not inner:
		return []

	state_chunks = split_top_level(inner, sep=",")
	trace: list[set[str]] = []

	for state_chunk in state_chunks:
		chunk = state_chunk.strip()
		if (chunk.startswith("(") and chunk.endswith(")")) or (chunk.startswith("{") and chunk.endswith("}")):
			chunk = chunk[1:-1].strip()

		state_atoms: set[str] = set()
		if chunk:
			for atom in split_top_level(chunk, sep=","):
				clean = atom.strip().strip("'\"")
				if clean:
					state_atoms.add(clean)
		trace.append(state_atoms)

	return trace


def eval_hoa_guard(guard: str, valuation_by_index: dict[int, bool]) -> bool:
	"""Evaluate an HOA boolean guard (using AP indices) against a valuation."""

	def _replace_index(match: re.Match[str]) -> str:
		index = int(match.group(0))
		return "True" if valuation_by_index.get(index, False) else "False"

	expr = guard
	expr = re.sub(r"\bt\b", "True", expr)
	expr = re.sub(r"\bf\b", "False", expr)
	expr = re.sub(r"(?<![A-Za-z_])\d+(?![A-Za-z_])", _replace_index, expr)
	expr = expr.replace("!", " not ").replace("&", " and ").replace("|", " or ")

	if re.search(r"[^A-Za-z()_\s]", expr):
		return False

	try:
		return bool(eval(expr, {"__builtins__": {}}, {}))
	except Exception:
		return False


def build_ap_valuation(
	ap_names: list[str],
	ap_display_map: dict[str, str],
	true_atoms: set[str],
) -> dict[int, bool]:
	"""Build AP-index valuation from a set of true atoms."""

	valuation_by_index: dict[int, bool] = {}
	for idx, internal_name in enumerate(ap_names):
		display_name = ap_display_map.get(internal_name, internal_name)
		valuation_by_index[idx] = (internal_name in true_atoms) or (display_name in true_atoms)
	return valuation_by_index


def compute_current_automaton_states(
	hoa_text: str,
	ap_names: list[str],
	ap_display_map: dict[str, str],
	true_atoms: set[str],
) -> tuple[list[int], list[int], dict[int, bool]]:
	"""Compute reachable automaton states after reading one PDDL state's AP valuation."""

	valuation_by_index = build_ap_valuation(ap_names, ap_display_map, true_atoms)

	start_states, transitions = parse_hoa_transitions(hoa_text)
	reached: set[int] = set()

	for start_state in start_states:
		for guard, destinations in transitions.get(start_state, []):
			if eval_hoa_guard(guard, valuation_by_index):
				reached.update(destinations)

	return start_states, sorted(reached), valuation_by_index


def compute_current_automaton_states_for_trace(
	hoa_text: str,
	ap_names: list[str],
	ap_display_map: dict[str, str],
	trace_true_atoms: list[set[str]],
) -> tuple[list[int], list[int], list[dict[int, bool]], bool]:
	"""
	Compute current automaton states after consuming a sequence of state valuations.

	Returns:
		(start_states, final_states, valuations_per_step, hit_implicit_sink)
	"""

	start_states, transitions = parse_hoa_transitions(hoa_text)
	current_states: set[int] = set(start_states)
	valuations_per_step: list[dict[int, bool]] = []
	hit_implicit_sink = False

	for true_atoms in trace_true_atoms:
		valuation_by_index = build_ap_valuation(ap_names, ap_display_map, true_atoms)
		valuations_per_step.append(valuation_by_index)

		next_states: set[int] = set()
		for state in current_states:
			for guard, destinations in transitions.get(state, []):
				if eval_hoa_guard(guard, valuation_by_index):
					next_states.update(destinations)

		if not next_states:
			hit_implicit_sink = True
			current_states = set()
			break

		current_states = next_states

	return start_states, sorted(current_states), valuations_per_step, hit_implicit_sink


def enumerate_simple_paths_with_guards(
	start_states: list[int],
	accepting_states: set[int],
	transitions: dict[int, list[tuple[str, list[int]]]],
	max_depth: int,
	max_paths: int,
) -> tuple[list[tuple[list[int], list[str]]], bool]:
	"""
	Enumerate simple paths from any start state to any accepting state.
	
	Returns:
		(paths_with_guards, truncated)
	where paths_with_guards is a list of (state_path, guard_path) tuples.
	Each guard_path[i] is the guard for the transition from state_path[i] to state_path[i+1].
	"""

	paths: list[tuple[list[int], list[str]]] = []
	truncated = False

	def _dfs(node: int, current_path: list[int], current_guards: list[str], visited: set[int]) -> None:
		nonlocal truncated
		if truncated:
			return
		if len(current_path) > max_depth:
			return
		if node in accepting_states:
			paths.append((current_path.copy(), current_guards.copy()))
			if len(paths) >= max_paths:
				truncated = True
			return
		for guard, destinations in transitions.get(node, []):
			for nxt in destinations:
				if nxt in visited:
					continue
				visited.add(nxt)
				current_path.append(nxt)
				current_guards.append(guard)
				_dfs(nxt, current_path, current_guards, visited)
				current_path.pop()
				current_guards.pop()
				visited.remove(nxt)

	for start in start_states:
		_dfs(start, [start], [], {start})
		if truncated:
			break

	return paths, truncated


def enumerate_simple_paths(
	start_states: list[int],
	accepting_states: set[int],
	adjacency: dict[int, list[int]],
	max_depth: int,
	max_paths: int,
) -> tuple[list[list[int]], bool]:
	"""Enumerate simple paths from any start state to any accepting state."""

	paths: list[list[int]] = []
	truncated = False

	def _dfs(node: int, current_path: list[int], visited: set[int]) -> None:
		nonlocal truncated
		if truncated:
			return
		if len(current_path) > max_depth:
			return
		if node in accepting_states:
			paths.append(current_path.copy())
			if len(paths) >= max_paths:
				truncated = True
			return
		for nxt in adjacency.get(node, []):
			if nxt in visited:
				continue
			visited.add(nxt)
			current_path.append(nxt)
			_dfs(nxt, current_path, visited)
			current_path.pop()
			visited.remove(nxt)

	for start in start_states:
		_dfs(start, [start], {start})
		if truncated:
			break

	return paths, truncated


def hoa_guard_to_display_formula(
	guard: str,
	ap_names: list[str],
	ap_display_map: dict[str, str],
) -> str:
	"""Convert HOA guard (using AP indices and operators) to extended display formula."""

	if not guard or guard in ["t", "f"]:
		return guard

	def _replace_index(match: re.Match[str]) -> str:
		index = int(match.group(0))
		if index < len(ap_names):
			internal_name = ap_names[index]
			return ap_display_map.get(internal_name, internal_name)
		return match.group(0)

	expr = guard
	expr = re.sub(r"(?<![A-Za-z_])\d+(?![A-Za-z_])", _replace_index, expr)
	expr = expr.replace("!", "¬").replace("&", " ∧ ").replace("|", " ∨ ")
	return expr


def save_paths_report(
	output_path: Path,
	start_states: list[int],
	accepting_states: set[int],
	paths: list[list[int]] | list[tuple[list[int], list[str]]],
	max_depth: int,
	max_paths: int,
	truncated: bool,
	current_states: Optional[list[int]] = None,
	ap_names: Optional[list[str]] = None,
	ap_display_map: Optional[dict[str, str]] = None,
) -> None:
	"""
	Save a human-readable path report to a text file.
	
	If current_states is provided, shows paths from current state to accepting states.
	Otherwise, shows paths from start states to accepting states.
	
	If ap_names and ap_display_map are provided, shows guards in extended form.
	"""

	output_path.parent.mkdir(parents=True, exist_ok=True)
	
	origin_states = current_states if current_states is not None else start_states
	origin_label = "Current state(s)" if current_states is not None else "Start state(s)"
	
	lines: list[str] = [
		"Automaton Paths Report",
		"=" * 72,
		f"{origin_label}: {origin_states if origin_states else '[]'}",
		f"Accepting states: {sorted(accepting_states) if accepting_states else '[]'}",
		f"Max depth      : {max_depth}",
		f"Max paths      : {max_paths}",
		"",
		"Note: paths are simple (no repeated states).",
	]
	if truncated:
		lines.append("Note: output truncated due to max-paths limit.")
	lines.append("")

	if not paths:
		origin_desc = "current state" if current_states is not None else "start state"
		lines.append(f"No simple path from any {origin_desc} to any accepting state.")
	else:
		lines.append(f"Found {len(paths)} path(s):")
		
		# Check if paths include guards (tuple format)
		has_guards = paths and isinstance(paths[0], tuple)
		
		for idx, path_data in enumerate(paths, start=1):
			if has_guards:
				state_path, guard_path = path_data
				path_str_parts = [str(state_path[0])]
				for i, next_state in enumerate(state_path[1:]):
					if i < len(guard_path):
						guard_raw = guard_path[i]
						if ap_names and ap_display_map:
							guard_display = hoa_guard_to_display_formula(guard_raw, ap_names, ap_display_map)
						else:
							guard_display = guard_raw
						path_str_parts.append(f"[{guard_display}]")
					path_str_parts.append(str(next_state))
				lines.append(f"{idx}. {' -> '.join(path_str_parts)}")
			else:
				path = path_data
				lines.append(f"{idx}. {' -> '.join(str(state) for state in path)}")

	output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compact_dot_labels(
	dot_text: str,
	ap_names: list[str],
	ap_display_map: Optional[dict[str, str]] = None,
	rankdir: str = "TB",
) -> tuple[str, dict[str, str]]:
	"""
	Shorten long AP names in DOT labels (p0, p1, ...) and add compact layout attrs.

	Returns:
		(modified_dot_text, legend_map)
	where legend_map maps short labels to original AP names.
	"""
	legend_map: dict[str, str] = {}
	modified = dot_text

	for idx, ap_name in enumerate(ap_names):
		short = f"p{idx}"
		readable_name = ap_display_map.get(ap_name, ap_name) if ap_display_map is not None else ap_name
		legend_map[short] = readable_name
		pattern = rf"(?<![A-Za-z0-9_]){re.escape(ap_name)}(?![A-Za-z0-9_])"
		modified = re.sub(pattern, short, modified)

	lines = modified.splitlines()
	if lines:
		lines.insert(
			1,
			(
				f'  graph [rankdir={rankdir}, splines=true, overlap=false, nodesep=0.35, ranksep=0.45];\n'
				'  node [fontsize=12];\n'
				'  edge [fontsize=10];'
			),
		)
		modified = "\n".join(lines)

	# Embed AP legend directly in the graph so the image is self-explanatory.
	if legend_map:
		def _esc(text: str) -> str:
			return text.replace("\\", "\\\\").replace('"', '\\"')

		legend_label = "AP Legend:\\l" + "".join(
			f"{_esc(short)} = {_esc(full)}\\l" for short, full in legend_map.items()
		)
		legend_block = "\n".join(
			[
				"  subgraph cluster_legend {",
				'    label="Legend";',
				'    fontsize=11;',
				'    color="#777777";',
				'    style="rounded,dashed";',
				f'    legend_node [shape=note, fontsize=10, label="{legend_label}"];',
				"  }",
			]
		)

		closing_idx = modified.rfind("}")
		if closing_idx != -1:
			modified = modified[:closing_idx] + "\n" + legend_block + "\n" + modified[closing_idx:]

	return modified, legend_map


def main() -> int:
	"""CLI entry point: translate formula, print summary, and optionally export files."""

	parser = argparse.ArgumentParser(
		description="Translate an LTL formula with SPOT and summarize the generated automaton."
	)
	parser.add_argument(
		"formula",
		nargs="?",
		default="(F(!onTable(purple_block_1) & holding(green_block_1))) AND (F(!onTop(purple_block_1, black_block_2))) AND (G(!onTop(purple_block_1, black_block_2) -> F(holding(black_block_1))))",
		help="LTL formula (default: 'G(a -> F b)')",
	)
	parser.add_argument(
		"--formula",
		dest="formula_flag",
		default=None,
		help="LTL formula (named option, equivalent to positional `formula`).",
	)
	parser.add_argument(
		"--deterministic",
		action="store_true",
		help="Request deterministic output from SPOT when possible.",
	)
	parser.add_argument(
		"--save-hoa",
		type=Path,
		default=None,
		help="Optional path to save HOA output.",
	)
	parser.add_argument(
		"--save-dot",
		type=Path,
		default=None,
		help="Optional path to save DOT graph output.",
	)
	parser.add_argument(
		"--render-image",
		type=Path,
		nargs="?",
		const=Path("automaton"),
		default=None,
		help=(
			"Optional output image path (e.g., automaton.svg, automaton.png). "
			"If provided without a value, defaults to './automaton.<image-format>'."
		),
	)
	parser.add_argument(
		"--image-format",
		choices=["svg", "png", "pdf"],
		default="svg",
		help="Graphviz output format used with --render-image (default: svg).",
	)
	parser.add_argument(
		"--rankdir",
		choices=["TB", "LR"],
		default="TB",
		help="Graph direction for visualization: TB (top-bottom) or LR (left-right).",
	)
	parser.add_argument(
		"--no-compact-labels",
		action="store_true",
		help="Disable short AP aliases (p0, p1, ...) in visualization.",
	)
	parser.add_argument(
		"--save-legend",
		type=Path,
		default=None,
		help="Optional path for AP legend text file (short label -> full proposition).",
	)
	parser.add_argument(
		"--save-paths",
		type=Path,
		default=None,
		help="Optional path to save all simple paths from start to accepting states (.txt).",
	)
	parser.add_argument(
		"--max-path-depth",
		type=int,
		default=30,
		help="Maximum depth used to enumerate simple paths (default: 30).",
	)
	parser.add_argument(
		"--max-paths",
		type=int,
		default=2000,
		help="Maximum number of paths to save before truncating output (default: 2000).",
	)
	parser.add_argument(
		"--check-state",
		action="store_true",
		help="Given an input state valuation, compute current automaton state(s).",
	)
	parser.add_argument(
		"--state-true",
		action="append",
		default=None,
		help=(
			"True atomic propositions for the input state. "
			"Repeat flag or pass comma-separated values, e.g. "
			"--state-true 'onTable(black_block_2),holding(green_block_1)'."
		),
	)
	parser.add_argument(
		"--trace-state-true",
		action="append",
		default=None,
		help=(
			"One trace state per flag occurrence. "
			"Use comma-separated true atoms for each state, e.g. "
			"--trace-state-true 'onTable(black_block_2)' "
			"--trace-state-true 'onTable(black_block_2),holding(green_block_1)'."
		),
	)
	parser.add_argument(
		"--trace",
		default=None,
		help=(
			"Trace as a single argument, e.g. "
			"--trace '[(holding(green_block_1)),(holding(black_block_1))]'."
		),
	)
	parser.add_argument(
		"--trace-verbose",
		action="store_true",
		help="Print AP valuation details for each trace step during state-check.",
	)
	parser.add_argument(
		"--print-hoa",
		action="store_true",
		help="Print full HOA content to stdout.",
	)

	args = parser.parse_args()
	formula_input = args.formula_flag if args.formula_flag is not None else args.formula
	formula, ap_display_map = normalize_formula_for_spot(formula_input)

	resolved_image_path: Optional[Path] = None
	if args.render_image is not None:
		resolved_image_path = args.render_image
		if resolved_image_path.suffix == "":
			resolved_image_path = resolved_image_path.with_suffix(f".{args.image_format}")

	resolved_paths_path: Optional[Path] = args.save_paths
	if resolved_paths_path is None and resolved_image_path is not None:
		resolved_paths_path = resolved_image_path.parent / f"{resolved_image_path.stem}_paths.txt"

	try:
		# Main translation step (LTL -> HOA automaton).
		hoa = ltl_to_hoa(formula, deterministic=args.deterministic)
	except SpotToolError as exc:
		print(f"[ERROR] {exc}", file=sys.stderr)
		return 2

	summary = parse_hoa_summary(hoa)
	display_ap_names = [ap_display_map.get(name, name) for name in summary["ap_names"]] if isinstance(summary["ap_names"], list) else []
	print("=" * 72)
	print("SPOT LTL -> Automaton translation")
	print("=" * 72)
	print(f"Formula in   : {formula_input}")
	print(f"Formula SPOT : {formula}")
	print(f"Deterministic: {args.deterministic}")
	print(f"States       : {summary['states']}")
	print(f"Start state  : {summary['start']}")
	print(f"AP count     : {summary['ap_count']}")
	print(f"AP names     : {', '.join(display_ap_names) if display_ap_names else '-'}")
	print(f"Acceptance   : {summary['acceptance']}")
	print(f"Transitions  : {summary['transitions']}")
	print("-" * 72)
	print("Note: for general LTL over infinite traces this is not a classic DFA.")

	single_state_true_atoms = parse_true_atoms(args.state_true)
	trace_true_atoms = parse_trace_true_atoms(args.trace_state_true)
	if args.trace is not None:
		try:
			trace_true_atoms = parse_trace_argument(args.trace)
		except ValueError as exc:
			print(f"[ERROR] Invalid --trace format: {exc}", file=sys.stderr)
			return 2
	if not trace_true_atoms and single_state_true_atoms:
		trace_true_atoms = [single_state_true_atoms]

	# Initialize current_states to None; will be set if trace is provided.
	current_states: Optional[list[int]] = None
	
	if args.check_state or trace_true_atoms:
		if not trace_true_atoms:
			print(
				"[ERROR] --check-state requires --trace-state-true (preferred) or --state-true.",
				file=sys.stderr,
			)
			return 2

		ap_names_internal = summary["ap_names"] if isinstance(summary["ap_names"], list) else []
		start_states, current_states, valuations_per_step, hit_implicit_sink = compute_current_automaton_states_for_trace(
			hoa_text=hoa,
			ap_names=ap_names_internal,
			ap_display_map=ap_display_map,
			trace_true_atoms=trace_true_atoms,
		)

		print("\nState-check (trace)")
		print("-" * 72)
		print(f"Trace length     : {len(trace_true_atoms)}")
		print(f"Start state(s)   : {start_states if start_states else '[]'}")
		for idx, state_atoms in enumerate(trace_true_atoms, start=1):
			print(f"State[{idx}] true : {', '.join(sorted(state_atoms)) if state_atoms else '(none)'}")
			if args.trace_verbose and idx <= len(valuations_per_step):
				valuation_by_index = valuations_per_step[idx - 1]
				valuation_chunks = []
				for ap_idx, internal_name in enumerate(ap_names_internal):
					display_name = ap_display_map.get(internal_name, internal_name)
					truth = valuation_by_index.get(ap_idx, False)
					valuation_chunks.append(f"p{ap_idx}={str(truth)} ({display_name})")
				print(f"  AP valuation   : {', '.join(valuation_chunks) if valuation_chunks else '-'}")

		if current_states:
			print(f"Current state(s) : {current_states}")
		else:
			print("Current state(s) : []")
			if hit_implicit_sink:
				print("Note: trace reached an implicit rejecting sink (no matching explicit transition).")

	if args.print_hoa:
		# Useful for debugging or for piping to external automata tooling.
		print("\nHOA output:")
		print(hoa)

	if args.save_hoa is not None:
		args.save_hoa.parent.mkdir(parents=True, exist_ok=True)
		args.save_hoa.write_text(hoa, encoding="utf-8")
		print(f"Saved HOA to: {args.save_hoa}")

	# Build visualization-oriented HOA when needed by DOT/image/paths analysis.
	if args.save_dot is not None or resolved_image_path is not None or resolved_paths_path is not None:
		try:
			# For visualization we convert to state-based acceptance first,
			# so accepting states are explicit and easier to read in the graph.
			hoa_for_viz = hoa_to_state_based_acceptance(hoa)

			if resolved_paths_path is not None:
				start_states, accepting_states, adjacency = parse_hoa_graph(hoa_for_viz)
				
				# Determine which states to use as starting points for path enumeration.
				# If a trace was provided and computed current states, use those; otherwise use start states.
				path_start_states = current_states if (args.check_state or trace_true_atoms) and current_states else start_states
				
				# Get transitions with guards for detailed path display
				_, transitions_with_guards = parse_hoa_transitions(hoa_for_viz)
				
				paths, truncated = enumerate_simple_paths_with_guards(
					start_states=path_start_states,
					accepting_states=accepting_states,
					transitions=transitions_with_guards,
					max_depth=max(1, args.max_path_depth),
					max_paths=max(1, args.max_paths),
				)
				
				ap_names_internal = summary["ap_names"] if isinstance(summary["ap_names"], list) else []
				save_paths_report(
					output_path=resolved_paths_path,
					start_states=start_states,
					accepting_states=accepting_states,
					paths=paths,
					max_depth=max(1, args.max_path_depth),
					max_paths=max(1, args.max_paths),
					truncated=truncated,
					current_states=path_start_states if (args.check_state or trace_true_atoms) else None,
					ap_names=ap_names_internal,
					ap_display_map=ap_display_map,
				)
				print(f"Saved paths report to: {resolved_paths_path}")

			dot_text = hoa_to_dot(hoa_for_viz)

			legend_map: dict[str, str] = {}
			if not args.no_compact_labels:
				dot_text, legend_map = compact_dot_labels(
					dot_text,
					summary["ap_names"] if isinstance(summary["ap_names"], list) else [],
					ap_display_map=ap_display_map,
					rankdir=args.rankdir,
				)

			if args.save_dot is not None:
				args.save_dot.parent.mkdir(parents=True, exist_ok=True)
				args.save_dot.write_text(dot_text, encoding="utf-8")
				print(f"Saved DOT to: {args.save_dot}")

			if resolved_image_path is not None:
				image_path = resolved_image_path
				image_path.parent.mkdir(parents=True, exist_ok=True)
				dot_to_image(dot_text, image_path, args.image_format)
				print(f"Saved image to: {image_path} ({args.image_format})")
				print("Visualization note: rendered using state-based acceptance (sbacc).")

				legend_path = args.save_legend
				if legend_path is None and legend_map:
					legend_path = image_path.parent / f"{image_path.stem}_legend.txt"
				if legend_path is not None and legend_map:
					legend_path.parent.mkdir(parents=True, exist_ok=True)
					legend_lines = [f"{k} = {v}" for k, v in legend_map.items()]
					legend_path.write_text("\n".join(legend_lines) + "\n", encoding="utf-8")
					print(f"Saved AP legend to: {legend_path}")
		except SpotToolError as exc:
			print(f"[WARN] DOT/image export skipped: {exc}", file=sys.stderr)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())

