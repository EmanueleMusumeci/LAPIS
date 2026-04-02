(define (domain blocks)
  (:requirements :strips)
  (:predicates
    (on ?x ?y)
    (clear ?x)
    (holding ?x)
    (empty)
    (num-blocks ?n) ; Added predicate to represent the number of blocks
    (goal-on ?x ?y) ; Added predicate to represent the goal state
  )

  (:action pickup
    :parameters (?x)
    :precondition (and (clear ?x) (empty))
    :effect (and (holding ?x) (not (clear ?x))))

  (:action putdown
    :parameters (?x)
    :precondition (holding ?x)
    :effect (and (clear ?x) (empty) (not (holding ?x))))

  (:action stack
    :parameters (?x ?y)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (on ?x ?y) (clear ?x) (empty) (not (holding ?x))))

  (:action unstack
    :parameters (?x ?y)
    :precondition (and (on ?x ?y) (clear ?x) (empty))
    :effect (and (holding ?x) (clear ?y) (not (on ?x ?y))))
)