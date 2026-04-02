(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place locatable - thing
    depot distributor - place
    truck hoist surface - locatable
    storearea transitarea - area
    crate - locatable
    area - thing
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (on ?c - crate ?s - storearea)
    (in ?s - storearea ?p - place)
    (clear ?s - storearea)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (connected ?s1 - area ?s2 - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?from - storearea ?to - area ?p - place)
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
      (not (in ?from ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?to - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?to)
      (in ?to ?p)
      (connected ?a ?to)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (on ?c ?to)
      (not (clear ?to))
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