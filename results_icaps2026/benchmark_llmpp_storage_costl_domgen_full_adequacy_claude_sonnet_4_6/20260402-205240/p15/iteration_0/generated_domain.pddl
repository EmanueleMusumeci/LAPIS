(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area - object_root
    store_area transit_area - area
    hoist crate surface - object_root
  )

  (:predicates
    (available ?h - hoist)
    (at ?h - hoist ?a - area)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - store_area ?p - place)
    (clear ?s - store_area)
    (connected ?a1 - area ?a2 - area)
    (occupied ?s - store_area ?c - crate)
    (is-surface ?s - store_area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - store_area ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?s)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (in ?src ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - store_area ?a - area ?p - place)
    :precondition (and
      (at ?h ?a)
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
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store_area ?dst - store_area)
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
    :parameters (?h - hoist ?src - store_area ?dst - transit_area)
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
    :parameters (?h - hoist ?src - transit_area ?dst - store_area)
    :precondition (and
      (at ?h ?src)
      (connected ?src ?dst)
      (clear ?dst)
    )
    :effect (and
      (not (at ?h ?src))
      (at ?h ?dst)
      (not (clear ?dst))
    )
  )
)