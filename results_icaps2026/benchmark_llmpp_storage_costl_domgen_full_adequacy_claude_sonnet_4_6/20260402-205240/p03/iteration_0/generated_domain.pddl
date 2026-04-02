(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    depot distributor - place
    storearea transitarea - area
    container - surface
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - storearea ?p - place)
    (clear ?s - storearea)
    (connected ?s - storearea ?a - area)
    (in-container ?c - crate ?cn - container)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place ?sur - surface)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (on ?c ?sur)
      (in ?s ?p)
      (connected ?s ?a)
    )
    :effect (and
      (not (on ?c ?sur))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place ?sur - surface)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?p)
      (connected ?s ?a)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s))
      (on ?c ?sur)
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