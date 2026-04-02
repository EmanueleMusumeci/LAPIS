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
    (in-place ?sa - storearea ?p - place)
    (crate-in-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - storearea ?a - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (on ?c ?s)
      (in ?s ?sa)
      (in-place ?sa ?p)
      (connected ?sa ?a)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?sa)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate-in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?sa - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?sa)
      (in ?s ?sa)
      (in-place ?sa ?p)
      (connected ?sa ?a)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (on ?c ?s)
      (not (clear ?sa))
      (crate-in-place ?c ?p)
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