(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place area crate hoist surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at-hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?p - place)
    (connected ?a1 - area ?a2 - area)
    (clear ?a - store_area)
    (in-store ?c - crate ?s - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?p - place ?s - surface)
    :precondition (and
      (available ?h)
      (at-hoist ?h ?dst)
      (on ?c ?s)
      (in ?s ?p)
      (in-store ?c ?src)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (in-store ?c ?src))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (on ?c ?s))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - store_area ?p - place ?s - surface ?a - area)
    :precondition (and
      (at-hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (in ?s ?p)
      (connected ?a ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (in-store ?c ?dst)
      (on ?c ?s)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store_area ?dst - store_area)
    :precondition (and
      (at-hoist ?h ?src)
      (clear ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at-hoist ?h ?src))
      (at-hoist ?h ?dst)
      (not (clear ?dst))
      (clear ?src)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?src - store_area ?dst - transit_area)
    :precondition (and
      (at-hoist ?h ?src)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at-hoist ?h ?src))
      (at-hoist ?h ?dst)
      (clear ?src)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?src - transit_area ?dst - store_area)
    :precondition (and
      (at-hoist ?h ?src)
      (connected ?src ?dst)
      (clear ?dst)
    )
    :effect (and
      (not (at-hoist ?h ?src))
      (at-hoist ?h ?dst)
      (not (clear ?dst))
    )
  )
)