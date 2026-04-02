(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - physical-object
    store transit - area
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (clear ?s - surface)
    (in ?s - surface ?p - place)
    (connected ?a1 - area ?a2 - area)
    (crate-at ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store ?dest - area ?s - surface ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dest)
      (on ?c ?s)
      (in ?s ?p)
      (connected ?dest ?from)
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
    :parameters (?h - hoist ?c - crate ?dest - store ?s - surface ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?a ?dest)
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
    :parameters (?h - hoist ?from - store ?to - store ?sfrom - surface ?sto - surface)
    :precondition (and
      (at ?h ?from)
      (clear ?sto)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (not (clear ?sfrom))
      (clear ?sto)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store ?to - transit ?s - surface)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (clear ?s)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - transit ?to - store ?s - surface)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
      (clear ?s)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (not (clear ?s))
    )
  )
)