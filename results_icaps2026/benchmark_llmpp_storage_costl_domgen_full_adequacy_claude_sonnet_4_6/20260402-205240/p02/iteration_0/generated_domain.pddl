(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area crate hoist surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at_hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?sa - store_area)
    (clear ?sa - store_area)
    (connected ?a1 - area ?a2 - area)
    (in_place ?sa - store_area ?p - place)
    (crate_in_place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - store_area ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?dst)
      (on ?c ?s)
      (in ?s ?src)
      (in_place ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate_in_place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - store_area ?src - area ?p - place)
    :precondition (and
      (at_hoist ?h ?src)
      (lifting ?h ?c)
      (clear ?dst)
      (in_place ?dst ?p)
      (in ?s ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?s)
      (crate_in_place ?c ?p)
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