(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at_hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - store_area)
    (in ?s - store_area ?p - place)
    (clear ?s - store_area)
    (connected ?s - store_area ?a - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store_area ?to - area ?p - place)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?to)
      (on ?c ?from)
      (in ?from ?p)
      (connected ?from ?to)
    )
    :effect (and
      (not (on ?c ?from))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?from ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - store_area ?a - area ?p - place)
    :precondition (and
      (at_hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?to)
      (in ?to ?p)
      (connected ?to ?a)
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