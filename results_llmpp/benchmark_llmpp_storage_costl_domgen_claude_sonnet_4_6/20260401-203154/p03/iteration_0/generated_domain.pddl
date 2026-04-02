(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place locatable - thing
    depot distributor - place
    truck hoist surface - locatable
    storearea transitarea - area
    crate - locatable
    area - thing
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (on ?c - crate ?s - storearea)
    (in ?s - storearea ?p - place)
    (clear ?s - storearea)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (connected ?s - storearea ?a - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - storearea ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?src)
      (in ?src ?p)
      (connected ?src ?dst)
    )
    :effect (and
      (not (on ?c ?src))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?src ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - storearea ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (connected ?dst ?a)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?dst)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - storearea ?dst - storearea)
    :precondition (and
      (at ?h ?src)
      (clear ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (not (clear ?src))
      (clear ?dst)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?src - storearea ?dst - transitarea)
    :precondition (and
      (at ?h ?src)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (clear ?src)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?src - transitarea ?dst - storearea)
    :precondition (and
      (at ?h ?src)
      (connected ?dst ?src)
      (clear ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (not (clear ?dst))
    )
  )

)