(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at_hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in_place ?s - surface ?p - place)
    (connected ?a1 - area ?a2 - area)
    (clear ?s - surface)
    (occupying ?c - crate ?s - surface)
    (hoist_in_store ?h - hoist ?s - store_area)
    (hoist_in_transit ?h - hoist ?t - transit_area)
    (in_store ?c - crate ?s - store_area)
    (store_in_place ?s - store_area ?p - place)
    (store_clear ?s - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at_hoist ?h ?dst)
      (on ?c ?src)
      (store_in_place ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?src))
      (store_clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (store_in_place ?src ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - store_area ?src - area ?p - place)
    :precondition (and
      (at_hoist ?h ?src)
      (lifting ?h ?c)
      (store_clear ?dst)
      (store_in_place ?dst ?p)
      (connected ?src ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (store_clear ?dst))
      (on ?c ?dst)
      (in_store ?c ?dst)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store_area ?dst - store_area)
    :precondition (and
      (hoist_in_store ?h ?src)
      (store_clear ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (hoist_in_store ?h ?src))
      (hoist_in_store ?h ?dst)
      (at_hoist ?h ?dst)
      (not (at_hoist ?h ?src))
      (not (store_clear ?src))
      (store_clear ?dst)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?src - store_area ?dst - transit_area)
    :precondition (and
      (hoist_in_store ?h ?src)
      (at_hoist ?h ?src)
      (connected ?src ?dst)
    )
    :effect (and
      (not (hoist_in_store ?h ?src))
      (not (at_hoist ?h ?src))
      (hoist_in_transit ?h ?dst)
      (at_hoist ?h ?dst)
      (store_clear ?src)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?src - transit_area ?dst - store_area)
    :precondition (and
      (hoist_in_transit ?h ?src)
      (at_hoist ?h ?src)
      (connected ?src ?dst)
      (store_clear ?dst)
    )
    :effect (and
      (not (hoist_in_transit ?h ?src))
      (not (at_hoist ?h ?src))
      (hoist_in_store ?h ?dst)
      (at_hoist ?h ?dst)
      (not (store_clear ?dst))
    )
  )
)