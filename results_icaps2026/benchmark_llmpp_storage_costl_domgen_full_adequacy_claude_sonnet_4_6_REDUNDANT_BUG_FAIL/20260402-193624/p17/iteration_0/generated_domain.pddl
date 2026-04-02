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
    (connected ?s1 - storearea ?s2 - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (crate-at ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s1 - storearea ?a2 - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?a2)
      (on ?c ?s1)
      (in ?s1 ?p)
      (connected ?s1 ?a2)
    )
    :effect (and
      (not (on ?c ?s1))
      (clear ?s1)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate-at ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s2 - storearea ?a1 - area ?p - place)
    :precondition (and
      (at ?h ?a1)
      (lifting ?h ?c)
      (clear ?s2)
      (in ?s2 ?p)
      (connected ?s2 ?a1)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?s2))
      (on ?c ?s2)
      (crate-at ?c ?p)
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
    :parameters (?h - hoist ?s1 - storearea ?t2 - transitarea)
    :precondition (and
      (at ?h ?s1)
      (connected ?s1 ?t2)
    )
    :effect (and
      (not (at ?h ?s1))
      (at ?h ?t2)
      (clear ?s1)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?t1 - transitarea ?s2 - storearea)
    :precondition (and
      (at ?h ?t1)
      (connected ?s2 ?t1)
      (clear ?s2)
    )
    :effect (and
      (not (at ?h ?t1))
      (at ?h ?s2)
      (not (clear ?s2))
    )
  )
)