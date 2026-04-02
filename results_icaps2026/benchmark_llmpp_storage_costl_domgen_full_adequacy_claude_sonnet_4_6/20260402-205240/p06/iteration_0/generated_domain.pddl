(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (hoist-at ?h - hoist ?a - area)
    (hoist-available ?h - hoist)
    (hoist-lifting ?h - hoist ?c - crate)
    (crate-on ?c - crate ?s - surface)
    (area-clear ?a - store_area)
    (area-in ?a - store_area ?p - place)
    (connected ?a1 - area ?a2 - area)
    (crate-in ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?p - place ?s - surface)
    :precondition (and
      (hoist-available ?h)
      (hoist-at ?h ?dst)
      (crate-on ?c ?s)
      (area-in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (crate-on ?c ?s))
      (area-clear ?src)
      (not (hoist-available ?h))
      (hoist-lifting ?h ?c)
      (not (crate-in ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - store_area ?p - place ?s - surface ?a - area)
    :precondition (and
      (hoist-at ?h ?a)
      (hoist-lifting ?h ?c)
      (area-clear ?dst)
      (area-in ?dst ?p)
      (connected ?a ?dst)
    )
    :effect (and
      (not (hoist-lifting ?h ?c))
      (hoist-available ?h)
      (not (area-clear ?dst))
      (crate-on ?c ?s)
      (crate-in ?c ?p)
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