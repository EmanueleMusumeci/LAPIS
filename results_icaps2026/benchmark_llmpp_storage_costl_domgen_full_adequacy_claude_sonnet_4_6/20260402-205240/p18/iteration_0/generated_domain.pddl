(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place locatable - thing
    depot distributor - place
    truck hoist surface - locatable
    pallet crate - surface
    storearea transitarea - area
    area
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (on ?c - crate ?s - surface)
    (in ?s - storearea ?p - place)
    (connected ?a1 - area ?a2 - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (clear ?s - storearea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?from - storearea ?to - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?to)
      (on ?c ?s)
      (in ?from ?p)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?from)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?from ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?to - storearea ?from - area ?p - place)
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
      (on ?c ?s)
      (in ?to ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - storearea ?to - storearea)
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
    :parameters (?h - hoist ?from - storearea ?to - transitarea)
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
    :parameters (?h - hoist ?from - transitarea ?to - storearea)
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