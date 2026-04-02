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
    (on ?c - crate ?s - storearea)
    (in ?s - storearea ?p - place)
    (connected ?s1 - area ?s2 - area)
    (clear ?s - storearea)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (atransit ?h - hoist ?t - transitarea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?a)
      (connected ?a ?s)
      (on ?c ?s)
      (in ?s ?p)
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
    :parameters (?h - hoist ?c - crate ?s - storearea ?a - area ?p - place)
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
      (not (clear ?s))
      (on ?c ?s)
    )
  )

  (:action move
    :parameters (?h - hoist ?s1 - storearea ?s2 - storearea)
    :precondition (and
      (at ?h ?s1)
      (clear ?s2)
      (connected ?s1 ?s2)
    )
    :effect (and
      (not (at ?h ?s1))
      (at ?h ?s2)
      (not (clear ?s1))
      (clear ?s2)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?s - storearea ?t - transitarea)
    :precondition (and
      (at ?h ?s)
      (connected ?s ?t)
    )
    :effect (and
      (not (at ?h ?s))
      (atransit ?h ?t)
      (clear ?s)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?t - transitarea ?s - storearea)
    :precondition (and
      (atransit ?h ?t)
      (connected ?t ?s)
      (clear ?s)
    )
    :effect (and
      (not (atransit ?h ?t))
      (at ?h ?s)
      (not (clear ?s))
    )
  )
)