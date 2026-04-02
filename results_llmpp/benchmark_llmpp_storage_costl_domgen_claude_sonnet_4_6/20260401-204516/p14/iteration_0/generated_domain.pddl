(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at_hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?sa - store_area)
    (clear ?sa - store_area)
    (connected ?sa - store_area ?a - area)
    (in_place ?sa - store_area ?p - place)
    (crate_in_place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - store_area ?a - area ?p - place)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?a)
      (on ?c ?s)
      (in ?s ?sa)
      (in_place ?sa ?p)
      (connected ?sa ?a)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?sa)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate_in_place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - store_area ?a - area ?p - place)
    :precondition (and
      (at_hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?sa)
      (in_place ?sa ?p)
      (in ?s ?sa)
      (connected ?sa ?a)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?sa))
      (on ?c ?s)
      (crate_in_place ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - store_area ?to - store_area)
    :precondition (and
      (at_hoist ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (at_hoist ?h ?from))
      (at_hoist ?h ?to)
      (not (clear ?from))
      (clear ?to)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store_area ?to - transit_area)
    :precondition (and
      (at_hoist ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at_hoist ?h ?from))
      (at_hoist ?h ?to)
      (clear ?from)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - transit_area ?to - store_area)
    :precondition (and
      (at_hoist ?h ?from)
      (connected ?to ?from)
      (clear ?to)
    )
    :effect (and
      (not (at_hoist ?h ?from))
      (at_hoist ?h ?to)
      (not (clear ?to))
    )
  )
)