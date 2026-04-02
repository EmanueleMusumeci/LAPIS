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
    (clear ?s - store_area)
    (connected ?a1 - area ?a2 - area)
    (in-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - store_area ?a - area ?p - place ?surf - surface)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (on ?c ?surf)
      (in ?s ?p)
      (connected ?a ?s)
    )
    :effect (and
      (not (on ?c ?surf))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - store_area ?a - area ?p - place ?surf - surface)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?a ?s)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s))
      (on ?c ?surf)
      (in-place ?c ?p)
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