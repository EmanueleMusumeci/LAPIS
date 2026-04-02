(define (domain depot)
  (:requirements :typing :conditional-effects)

  (:types
    place area - object_root
    store_area transit_area - area
    hoist crate surface - object_root
  )

  (:predicates
    (at_hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - store_area ?p - place)
    (connected ?a1 - area ?a2 - area)
    (clear ?s - store_area)
    (crate_in ?c - crate ?s - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?p - place ?s - surface)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?dst)
      (on ?c ?s)
      (crate_in ?c ?src)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (crate_in ?c ?src))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (on ?c ?s))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - store_area ?a - area ?p - place ?s - surface)
    :precondition (and
      (at_hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?dst)
      (in ?dst ?p)
      (connected ?a ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (crate_in ?c ?dst)
      (on ?c ?s)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store_area ?dst - store_area)
    :precondition (and
      (at_hoist ?h ?src)
      (clear ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at_hoist ?h ?src))
      (at_hoist ?h ?dst)
      (not (clear ?src))
      (clear ?dst)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?src - store_area ?dst - transit_area)
    :precondition (and
      (at_hoist ?h ?src)
      (connected ?src ?dst)
    )
    :effect (and
      (not (at_hoist ?h ?src))
      (at_hoist ?h ?dst)
      (clear ?src)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?src - transit_area ?dst - store_area)
    :precondition (and
      (at_hoist ?h ?src)
      (connected ?src ?dst)
      (clear ?dst)
    )
    :effect (and
      (not (at_hoist ?h ?src))
      (at_hoist ?h ?dst)
      (not (clear ?dst))
    )
  )

)