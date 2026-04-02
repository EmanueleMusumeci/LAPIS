(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at-hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?sa - store_area)
    (clear ?sa - store_area)
    (connected ?a1 - area ?a2 - area)
    (in-place ?sa - store_area ?p - place)
    (in-crate ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?from - store_area ?to - area ?p - place)
    :precondition (and
      (available ?h)
      (at-hoist ?h ?to)
      (on ?c ?s)
      (in ?s ?from)
      (in-place ?from ?p)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in-place ?from ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?to - store_area ?a - area ?p - place)
    :precondition (and
      (at-hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?to)
      (in ?s ?to)
      (in-place ?to ?p)
      (connected ?a ?to)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?to))
      (on ?c ?s)
      (in-crate ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - store_area ?to - store_area)
    :precondition (and
      (at-hoist ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (at-hoist ?h ?from))
      (at-hoist ?h ?to)
      (not (clear ?from))
      (not (clear ?to))
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store_area ?to - transit_area)
    :precondition (and
      (at-hoist ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at-hoist ?h ?from))
      (at-hoist ?h ?to)
      (clear ?from)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - transit_area ?to - store_area)
    :precondition (and
      (at-hoist ?h ?from)
      (connected ?from ?to)
      (clear ?to)
    )
    :effect (and
      (not (at-hoist ?h ?from))
      (at-hoist ?h ?to)
      (not (clear ?to))
    )
  )

)