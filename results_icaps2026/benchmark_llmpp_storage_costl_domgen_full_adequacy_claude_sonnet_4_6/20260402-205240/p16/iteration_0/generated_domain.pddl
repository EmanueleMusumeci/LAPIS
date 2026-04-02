(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - store_area ?p - place)
    (clear ?s - store_area)
    (connected ?s - store_area ?a - area)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?s - surface ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?s)
      (in ?src ?p)
      (connected ?src ?dst)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - store_area ?s - surface ?a - area ?p - place)
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