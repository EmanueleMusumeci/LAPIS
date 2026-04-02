(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area - object_root
    store_area transit_area - area
    hoist crate surface - object_root
  )

  (:predicates
    (hoist-at ?h - hoist ?a - area)
    (hoist-available ?h - hoist)
    (hoist-lifting ?h - hoist ?c - crate)
    (crate-on ?c - crate ?s - surface)
    (area-clear ?a - area)
    (in ?a - store_area ?p - place)
    (connected ?a1 - area ?a2 - area)
    (surface-at ?s - surface ?a - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - store_area ?dst - area ?p - place)
    :precondition (and
      (hoist-available ?h)
      (hoist-at ?h ?dst)
      (crate-on ?c ?s)
      (surface-at ?s ?src)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (crate-on ?c ?s))
      (area-clear ?src)
      (not (hoist-available ?h))
      (hoist-lifting ?h ?c)
      (not (in ?src ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - store_area ?a - area ?p - place)
    :precondition (and
      (hoist-at ?h ?a)
      (hoist-lifting ?h ?c)
      (area-clear ?dst)
      (in ?dst ?p)
      (connected ?a ?dst)
      (surface-at ?s ?dst)
    )
    :effect (and
      (not (hoist-lifting ?h ?c))
      (hoist-available ?h)
      (not (area-clear ?dst))
      (crate-on ?c ?s)
      (in ?dst ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store_area ?dst - store_area)
    :precondition (and
      (hoist-at ?h ?src)
      (area-clear ?dst)
      (connected ?src ?dst)
    )
    :effect (and
      (not (hoist-at ?h ?src))
      (hoist-at ?h ?dst)
      (not (area-clear ?dst))
      (area-clear ?src)
    )
  )

  (:action go-out
    :parameters (?h - hoist ?src - store_area ?dst - transit_area)
    :precondition (and
      (hoist-at ?h ?src)
      (connected ?src ?dst)
    )
    :effect (and
      (not (hoist-at ?h ?src))
      (hoist-at ?h ?dst)
      (area-clear ?src)
    )
  )

  (:action go-in
    :parameters (?h - hoist ?src - transit_area ?dst - store_area)
    :precondition (and
      (hoist-at ?h ?src)
      (connected ?src ?dst)
      (area-clear ?dst)
    )
    :effect (and
      (not (hoist-at ?h ?src))
      (hoist-at ?h ?dst)
      (not (area-clear ?dst))
    )
  )
)