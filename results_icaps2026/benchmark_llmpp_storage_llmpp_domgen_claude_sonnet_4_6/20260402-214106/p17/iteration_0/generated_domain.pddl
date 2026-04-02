(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place locatable - thing
    area hoist crate - locatable
    storearea transitarea - area
  )

  (:predicates
    (connected ?x - storearea ?y - area)
    (in ?x - storearea ?y - place)
    (at ?x - hoist ?y - area)
    (available ?x - hoist)
    (lifting ?x - hoist ?y - crate)
    (on ?x - crate ?y - storearea)
    (clear ?x - storearea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - storearea ?d - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?d)
      (on ?c ?s)
      (in ?s ?p)
      (connected ?s ?d)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?s ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - storearea ?d - area ?p - place)
    :precondition (and
      (at ?h ?d)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?s ?d)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (on ?c ?s)
      (not (clear ?s))
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