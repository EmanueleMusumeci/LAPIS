(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place locatable - object_root
    area hoist crate - locatable
    storearea transitarea - area
  )

  (:predicates
    (connected ?x - storearea ?y - area)
    (in ?x - storearea ?y - place)
    (at ?h - hoist ?x - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?x - storearea)
    (clear ?x - storearea)
    (in-place ?c - crate ?p - place)
    (in-crate ?c - crate ?p - place)
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
      (not (in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - storearea ?src - area ?p - place)
    :precondition (and
      (at ?h ?src)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?dst)
      (in-place ?c ?p)
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