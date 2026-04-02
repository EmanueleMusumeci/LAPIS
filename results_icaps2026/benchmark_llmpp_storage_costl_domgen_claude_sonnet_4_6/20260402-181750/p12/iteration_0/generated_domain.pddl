(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (in ?a - area ?p - place)
    (connected ?a1 - area ?a2 - area)
    (hoist_at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - store_area)
    (clear ?s - store_area)
    (in_place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - store_area ?a - store_area ?p - place)
    :precondition (and
      (available ?h)
      (hoist_at ?h ?a)
      (on ?c ?s)
      (in ?s ?p)
      (connected ?a ?s)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in_place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - store_area ?a - store_area ?p - place)
    :precondition (and
      (hoist_at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?a ?s)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s))
      (on ?c ?s)
      (in_place ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - store_area ?to - store_area)
    :precondition (and
      (hoist_at ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (hoist_at ?h ?from))
      (hoist_at ?h ?to)
      (not (clear ?from))
      (clear ?to)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store_area ?to - transit_area)
    :precondition (and
      (hoist_at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (hoist_at ?h ?from))
      (hoist_at ?h ?to)
      (clear ?from)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - transit_area ?to - store_area)
    :precondition (and
      (hoist_at ?h ?from)
      (connected ?from ?to)
      (clear ?to)
    )
    :effect (and
      (not (hoist_at ?h ?from))
      (hoist_at ?h ?to)
      (not (clear ?to))
    )
  )
)