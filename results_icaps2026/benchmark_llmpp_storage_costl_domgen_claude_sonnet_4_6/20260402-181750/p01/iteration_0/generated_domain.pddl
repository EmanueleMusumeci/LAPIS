(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place area - object_root
    store transit - area
    hoist crate surface - object_root
  )

  (:predicates
    (at-hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - store ?p - place)
    (clear ?s - store)
    (connected ?a1 - area ?a2 - area)
    (in-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - store ?to - area ?p - place ?s - surface)
    :precondition (and
      (available ?h)
      (at-hoist ?h ?to)
      (on ?c ?s)
      (in ?from ?p)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - store ?a - area ?p - place ?s - surface)
    :precondition (and
      (at-hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?to)
      (in ?to ?p)
      (connected ?a ?to)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?to))
      (on ?c ?s)
      (in-place ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - store ?to - store)
    :precondition (and
      (at-hoist ?h ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (at-hoist ?h ?from))
      (at-hoist ?h ?to)
      (not (clear ?from))
      (clear ?to)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - store ?to - transit)
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
    :parameters (?h - hoist ?from - transit ?to - store)
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