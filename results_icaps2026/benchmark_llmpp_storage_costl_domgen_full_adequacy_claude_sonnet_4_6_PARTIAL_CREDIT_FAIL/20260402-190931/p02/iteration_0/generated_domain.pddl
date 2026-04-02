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
    (on ?c - crate ?s - store_area)
    (in ?s - store_area ?p - place)
    (clear ?s - store_area)
    (connected ?s - store_area ?a - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store_area ?to - area ?p - place)
    :precondition (and
      (hoist-available ?h)
      (hoist-at ?h ?to)
      (on ?c ?from)
      (in ?from ?p)
      (connected ?from ?to)
    )
    :effect (and
      (not (on ?c ?from))
      (clear ?from)
      (not (hoist-available ?h))
      (lifting ?h ?c)
      (not (in ?from ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - store_area ?a - area ?p - place)
    :precondition (and
      (hoist-at ?h ?a)
      (lifting ?h ?c)
      (clear ?to)
      (in ?to ?p)
      (connected ?to ?a)
    )
    :effect (and
      (not (lifting ?h ?c))
      (hoist-available ?h)
      (not (clear ?to))
      (on ?c ?to)
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