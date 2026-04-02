(define (domain depot)
  (:requirements :strips :typing)

  (:types
    hoist crate surface place - entity
    storearea transitarea - surface
  )

  (:predicates
    (available ?h - hoist)
    (at ?h - hoist ?a - surface)
    (on ?c - crate ?a - storearea)
    (in ?a - storearea ?p - place)
    (clear ?a - storearea)
    (lifting ?h - hoist ?c - crate)
    (connected ?a1 - surface ?a2 - surface)
    (crat-in-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - storearea ?dst - surface ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?src)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?src))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crat-in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - storearea ?src - surface ?p - place)
    :precondition (and
      (at ?h ?src)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (connected ?src ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?dst)
      (crat-in-place ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - storearea ?dst - storearea)
    :precondition (and
      (at ?h ?src)
      (clear ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (not (clear ?src))
      (clear ?dst)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?src - storearea ?dst - transitarea)
    :precondition (and
      (at ?h ?src)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (clear ?src)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?src - transitarea ?dst - storearea)
    :precondition (and
      (at ?h ?src)
      (connected ?src ?dst)
      (clear ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (not (clear ?dst))
    )
  )
)