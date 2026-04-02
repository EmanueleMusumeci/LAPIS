(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (on ?c - crate ?s - store_area)
    (in ?s - store_area ?p - place)
    (clear ?s - store_area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (connected ?s1 - area ?s2 - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store_area ?to - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?to)
      (on ?c ?from)
      (in ?from ?p)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?c ?from))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - store_area ?from - area ?p - place)
    :precondition (and
      (at ?h ?from)
      (lifting ?h ?c)
      (clear ?to)
      (in ?to ?p)
      (connected ?from ?to)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?to))
      (on ?c ?to)
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
      (not (clear ?to))
      (clear ?from)
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