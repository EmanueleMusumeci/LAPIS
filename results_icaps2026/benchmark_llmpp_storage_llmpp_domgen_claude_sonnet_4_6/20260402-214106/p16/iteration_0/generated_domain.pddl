(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (hoist-at ?h - hoist ?a - area)
    (hoist-available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (crate-on ?c - crate ?s - store_area)
    (clear ?s - store_area)
    (connected ?s - store_area ?a - area)
    (in ?s - store_area ?p - place)
    (crate-in ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - store_area ?a - area ?p - place)
    :precondition (and
      (hoist-available ?h)
      (hoist-at ?h ?a)
      (crate-on ?c ?s)
      (in ?s ?p)
      (connected ?s ?a)
    )
    :effect (and
      (not (crate-on ?c ?s))
      (clear ?s)
      (not (hoist-available ?h))
      (lifting ?h ?c)
      (not (crate-in ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - store_area ?a - area ?p - place)
    :precondition (and
      (hoist-at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?s ?a)
    )
    :effect (and
      (not (lifting ?h ?c))
      (hoist-available ?h)
      (not (clear ?s))
      (crate-on ?c ?s)
      (crate-in ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - store_area ?to - store_area)
    :precondition (and
      (hoist-at ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (hoist-at ?h ?from))
      (hoist-at ?h ?to)
      (not (clear ?to))
      (clear ?from)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store_area ?to - transit_area)
    :precondition (and
      (hoist-at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (hoist-at ?h ?from))
      (hoist-at ?h ?to)
      (clear ?from)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - transit_area ?to - store_area)
    :precondition (and
      (hoist-at ?h ?from)
      (connected ?to ?from)
      (clear ?to)
    )
    :effect (and
      (not (hoist-at ?h ?from))
      (hoist-at ?h ?to)
      (not (clear ?to))
    )
  )
)