(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (available ?h - hoist)
    (at ?h - hoist ?a - area)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - store_area ?p - place)
    (connected ?a1 - area ?a2 - area)
    (clear ?s - store_area)
    (occupying ?c - crate ?s - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store_area ?to - area ?p - place ?s - surface)
    :precondition (and
      (available ?h)
      (at ?h ?to)
      (on ?c ?s)
      (in ?from ?p)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
      (not (occupying ?c ?from))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - store_area ?p - place ?s - surface)
    :precondition (and
      (at ?h ?to)
      (lifting ?h ?c)
      (clear ?to)
      (in ?to ?p)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (occupying ?c ?to)
      (on ?c ?s)
      (not (clear ?to))
    )
  )

  (:action move
    :parameters (?h - hoist ?from - store_area ?to - store_area)
    :precondition (and
      (at ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (not (clear ?from))
      (clear ?to)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store_area ?to - transit_area)
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
    :parameters (?h - hoist ?from - transit_area ?to - store_area)
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