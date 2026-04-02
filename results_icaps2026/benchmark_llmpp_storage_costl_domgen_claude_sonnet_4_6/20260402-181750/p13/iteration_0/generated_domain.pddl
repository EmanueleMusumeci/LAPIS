(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - physical-object
    storearea transitarea - area
  )

  (:predicates
    (connected ?a1 - area ?a2 - area)
    (in ?a - storearea ?p - place)
    (on ?c - crate ?s - storearea)
    (clear ?s - storearea)
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (crate-at ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (connected ?a ?s)
      (on ?c ?s)
      (in ?s ?p)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate-at ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (connected ?a ?s)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s))
      (on ?c ?s)
      (crate-at ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - storearea ?to - storearea)
    :precondition (and
      (at ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (not (clear ?to))
      (clear ?from)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - storearea ?to - transitarea)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (clear ?from)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - transitarea ?to - storearea)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
      (clear ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (not (clear ?to))
    )
  )
)