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
    (clear ?s - storearea)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (connected ?s1 - storearea ?s2 - area)
    (connected ?t - transitarea ?s - storearea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s1 - storearea ?s2 - storearea ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?s2)
      (on ?c ?s1)
      (in ?s1 ?p)
      (connected ?s2 ?s1)
    )
    :effect (and
      (not (on ?c ?s1))
      (clear ?s1)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?s1 ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s1 - storearea ?s2 - storearea ?p - place)
    :precondition (and
      (at ?h ?s1)
      (lifting ?h ?c)
      (clear ?s2)
      (in ?s2 ?p)
      (connected ?s1 ?s2)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s2))
      (on ?c ?s2)
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
      (at ?h ?t)
      (clear ?s)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?t - transitarea ?s - storearea)
    :precondition (and
      (at ?h ?t)
      (connected ?t ?s)
      (clear ?s)
    )
    :effect (and
      (not (at ?h ?t))
      (at ?h ?s)
      (not (clear ?s))
    )
  )
)