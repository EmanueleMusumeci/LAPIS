(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place locatable - thing
    area hoist crate - locatable
    storearea transitarea - area
  )

  (:predicates
    (connected ?x - storearea ?y - area)
    (connected-to ?x - area ?y - storearea)
    (in ?x - storearea ?y - place)
    (on ?c - crate ?s - storearea)
    (clear ?s - storearea)
    (available ?h - hoist)
    (at ?h - hoist ?a - area)
    (lifting ?h - hoist ?c - crate)
    (crate-at ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (connected ?s ?a)
      (on ?c ?s)
      (in ?s ?p)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate-at ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (connected ?s ?a)
      (in ?s ?p)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s))
      (on ?c ?s)
      (crate-at ?c ?p)
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
      (connected ?to ?from)
      (clear ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
      (not (clear ?to))
    )
  )
)