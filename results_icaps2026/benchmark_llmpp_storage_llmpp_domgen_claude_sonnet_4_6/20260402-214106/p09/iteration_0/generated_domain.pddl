(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area - object_root
    storearea transitarea - area
    hoist crate surface - object_root
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - storearea ?p - place)
    (connected ?a1 - area ?a2 - area)
    (clear ?s - storearea)
    (occupies ?c - crate ?s - storearea)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s1 - storearea ?s2 - storearea ?p - place ?sur - surface)
    :precondition (and
      (available ?h)
      (at ?h ?s2)
      (on ?c ?sur)
      (in ?s1 ?p)
      (connected ?s2 ?s1)
    )
    :effect (and
      (not (on ?c ?sur))
      (clear ?s1)
      (not (available ?h))
      (lifting ?h ?c)
      (not (occupies ?c ?s1))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s1 - storearea ?s2 - storearea ?p - place ?sur - surface)
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
      (occupies ?c ?s2)
      (on ?c ?sur)
      (not (clear ?s2))
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