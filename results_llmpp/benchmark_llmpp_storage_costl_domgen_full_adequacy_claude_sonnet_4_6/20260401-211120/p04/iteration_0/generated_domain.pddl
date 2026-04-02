(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - physical-object
    storearea transitarea - area
  )

  (:predicates
    (connected ?a1 - area ?a2 - area)
    (in ?a - storearea ?p - place)
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in-store ?c - crate ?a - storearea)
    (clear ?a - storearea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - storearea ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?s)
      (in-store ?c ?src)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (in-store ?c ?src))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (on ?c ?s))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (connected ?a ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (on ?c ?s)
      (in-store ?c ?dst)
      (not (clear ?dst))
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
      (not (clear ?dst))
      (clear ?src)
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