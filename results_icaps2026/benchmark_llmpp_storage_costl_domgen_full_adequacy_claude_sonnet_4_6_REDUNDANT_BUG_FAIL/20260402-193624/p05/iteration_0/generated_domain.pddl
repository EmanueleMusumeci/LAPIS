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
    (occupied ?s - store_area ?c - crate)
    (crate_in ?c - crate ?p - place)
    (hoist_in_store ?s - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?p - place ?s - surface)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?dst)
      (on ?c ?s)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate_in ?c ?p))
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
      (occupied ?dst ?c)
      (on ?c ?s)
      (crate_in ?c ?p)
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
      (not (hoist_in_store ?src))
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
      (hoist_in_store ?dst)
    )
  )

)