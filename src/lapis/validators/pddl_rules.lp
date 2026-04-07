% Task 11 semantic verification rules for PDDL domains/problems.

% Undefined predicate usage in problem files.
error(undefined_goal_pred(P)) :- goal_pred(P), not pred(P).
error(undefined_init_pred(P)) :- init_pred(P), not pred(P).

% Goal predicates should be achievable from either init or action effects.
produced_pred(P) :- action_effect(_, P).
error(unachievable_goal(P)) :- goal_pred(P), not init_pred(P), not produced_pred(P).

% Action preconditions/effects must reference known predicates.
error(undefined_precondition_pred(A, P)) :- action_precond(A, P), not pred(P).
error(undefined_effect_pred(A, P)) :- action_effect(A, P), not pred(P).

% Type checks: every parameter type must have at least one object in the problem.
has_object_type(T) :- obj_type(_, T).
error(no_object_for_type(A, Param, T)) :- param_type(A, Param, T), not has_object_type(T).

% STRIPS compliance issues passed from parser-side detection.
error(non_strips_issue(R)) :- non_strips(R).

% Optional quality warnings.
used_pred(P) :- goal_pred(P).
used_pred(P) :- init_pred(P).
used_pred(P) :- action_precond(_, P).
used_pred(P) :- action_effect(_, P).
warning(unused_predicate(P)) :- pred(P), not used_pred(P).

#show error/1.
#show warning/1.
