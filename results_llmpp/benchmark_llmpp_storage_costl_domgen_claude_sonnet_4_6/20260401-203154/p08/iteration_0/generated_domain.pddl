(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - physical-object
    storearea transitarea - area
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - storearea ?p - place)
    (connected ?a1 - area ?a2 - area)
    (clear ?s - storearea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - storearea ?p - place ?sur - surface)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (on ?c ?sur)
      (in ?s ?p)
      (connected ?a ?s)
    )
    :effect (and
      (not (on ?c ?sur))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?s ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place ?sur - surface)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?a ?s)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (on ?c ?sur)
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
      (not (clear ?to))
      (clear ?from)
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