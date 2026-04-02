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
    (in ?s - surface ?sa - storearea)
    (clear ?sa - storearea)
    (connected ?sa - storearea ?a - area)
    (crat-in ?c - crate ?p - place)
    (areain ?sa - storearea ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - storearea ?a - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (connected ?sa ?a)
      (on ?c ?s)
      (in ?s ?sa)
      (areain ?sa ?p)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?sa)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crat-in ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (connected ?sa ?a)
      (lifting ?h ?c)
      (clear ?sa)
      (in ?s ?sa)
      (areain ?sa ?p)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?sa))
      (on ?c ?s)
      (crat-in ?c ?p)
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