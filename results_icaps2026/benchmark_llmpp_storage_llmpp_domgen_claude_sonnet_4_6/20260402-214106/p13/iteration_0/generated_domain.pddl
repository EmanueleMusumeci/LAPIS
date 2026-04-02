(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    hoist crate surface - item
    storearea transitarea - area
    place
  )

  (:predicates
    (available ?h - hoist)
    (at ?h - hoist ?a - area)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - storearea ?p - place)
    (clear ?s - storearea)
    (connected ?s - storearea ?a - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - storearea ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?s)
      (in ?src ?p)
      (connected ?src ?dst)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - storearea ?src - area ?p - place)
    :precondition (and
      (at ?h ?src)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?s)
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
      (connected ?dst ?src)
      (clear ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (not (clear ?dst))
    )
  )
)