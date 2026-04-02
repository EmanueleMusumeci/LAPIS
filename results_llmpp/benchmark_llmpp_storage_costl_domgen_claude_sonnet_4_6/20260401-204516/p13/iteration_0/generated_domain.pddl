(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store_area transit_area - area
  )

  (:predicates
    (available ?h - hoist)
    (at ?h - hoist ?a - area)
    (on ?c - crate ?s - store_area)
    (in ?s - store_area ?p - place)
    (clear ?s - store_area)
    (lifting ?h - hoist ?c - crate)
    (connected ?s1 - area ?s2 - area)
    (crate-at-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?src - store_area ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
      (on ?c ?src)
      (in ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?src))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate-at-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?dst - store_area ?a - area ?p - place)
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
      (not (clear ?dst))
      (on ?c ?dst)
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