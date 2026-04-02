(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (in ?a - area ?p - place)
    (connected ?a1 - area ?a2 - area)
    (hoist-at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - store_area)
    (clear ?s - store_area)
    (in-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store_area ?to - area ?p - place)
    :precondition (and
      (available ?h)
      (hoist-at ?h ?to)
      (on ?c ?from)
      (in ?from ?p)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?c ?from))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - store_area ?from - area ?p - place)
    :precondition (and
      (hoist-at ?h ?from)
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
      (in-place ?c ?p)
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
      (connected ?from ?to)
      (clear ?to)
    )
    :effect (and
      (not (hoist-at ?h ?from))
      (hoist-at ?h ?to)
      (not (clear ?to))
    )
  )
)