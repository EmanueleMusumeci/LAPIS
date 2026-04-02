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
    (connected ?a1 - area ?a2 - area)
    (clear ?sa - store_area)
    (in_place ?sa - store_area ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - store_area ?da - area ?p - place)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?da)
      (on ?c ?s)
      (in ?s ?sa)
      (in_place ?sa ?p)
      (connected ?da ?sa)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?sa)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in_place ?sa ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - store_area ?da - area ?p - place)
    :precondition (and
      (at_hoist ?h ?da)
      (lifting ?h ?c)
      (clear ?sa)
      (in_place ?sa ?p)
      (in ?s ?sa)
      (connected ?da ?sa)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?sa))
      (on ?c ?s)
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
      (not (clear ?to))
      (clear ?from)
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
      (connected ?from ?to)
      (clear ?to)
    )
    :effect (and
      (not (at_hoist ?h ?from))
      (at_hoist ?h ?to)
      (not (clear ?to))
    )
  )
)