(define (domain depots)
  (:requirements :strips :typing)

  (:types
    place locatable - thing
    depot distributor - place
    truck hoist surface - locatable
    pallet crate - surface
  )

  (:predicates
    (at ?x - locatable ?p - place)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?p - place)
    (clear ?s - surface)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (connected ?p1 - place ?p2 - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?from - place ?to - place)
    :precondition (and
      (available ?h)
      (at ?h ?to)
      (on ?c ?s)
      (in ?s ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?s)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?c ?from))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?to - place ?from - place)
    :precondition (and
      (at ?h ?from)
      (lifting ?h ?c)
      (clear ?s)
      (in ?s ?to)
      (connected ?to ?from)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (on ?c ?s)
      (not (clear ?s))
      (in ?c ?to)
    )
  )

  (:action move
    :parameters (?h - hoist ?from - place ?to - place)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?from - place ?to - place)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?from - place ?to - place)
    :precondition (and
      (at ?h ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?h ?from))
      (at ?h ?to)
    )
  )
)