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
    (at ?hoist - hoist ?area - area)
    (on ?crate - crate ?surface - surface)
    (in ?storearea - storearea ?place - place)
    (clear ?storearea - storearea)
    (available ?hoist - hoist)
    (lifting ?hoist - hoist ?crate - crate)
    (connected ?area1 - area ?area2 - area)
  )

  (:action lift
    :parameters (?hoist - hoist ?crate - crate ?surface - surface ?from - storearea ?to - area ?place - place)
    :precondition (and
      (available ?hoist)
      (at ?hoist ?to)
      (on ?crate ?surface)
      (in ?from ?place)
      (connected ?to ?from)
    )
    :effect (and
      (not (on ?crate ?surface))
      (clear ?from)
      (not (available ?hoist))
      (lifting ?hoist ?crate)
      (not (in ?from ?place))
    )
  )

  (:action drop
    :parameters (?hoist - hoist ?crate - crate ?surface - surface ?to - storearea ?area - area ?place - place)
    :precondition (and
      (at ?hoist ?area)
      (lifting ?hoist ?crate)
      (clear ?to)
      (in ?to ?place)
      (connected ?area ?to)
    )
    :effect (and
      (not (lifting ?hoist ?crate))
      (available ?hoist)
      (not (clear ?to))
      (on ?crate ?surface)
      (in ?to ?place)
    )
  )

  (:action move
    :parameters (?hoist - hoist ?from - storearea ?to - storearea)
    :precondition (and
      (at ?hoist ?from)
      (clear ?to)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?hoist ?from))
      (at ?hoist ?to)
      (not (clear ?from))
      (clear ?to)
    )
  )

  (:action go-out
    :parameters (?hoist - hoist ?from - storearea ?to - transitarea)
    :precondition (and
      (at ?hoist ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?hoist ?from))
      (at ?hoist ?to)
      (clear ?from)
    )
  )

  (:action go-in
    :parameters (?hoist - hoist ?from - transitarea ?to - storearea)
    :precondition (and
      (at ?hoist ?from)
      (connected ?from ?to)
      (clear ?to)
    )
    :effect (and
      (not (at ?hoist ?from))
      (at ?hoist ?to)
      (not (clear ?to))
    )
  )
)