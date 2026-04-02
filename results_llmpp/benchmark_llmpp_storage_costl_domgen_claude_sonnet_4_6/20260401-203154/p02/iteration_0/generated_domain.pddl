(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - object_root
    store transit - area
  )

  (:predicates
    (at-hoist ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?a - store)
    (clear ?a - store)
    (connected ?a1 - area ?a2 - area)
    (in-place ?a - store ?p - place)
    (crate-in-place ?c - crate ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - store ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at-hoist ?h ?dst)
      (on ?c ?s)
      (in ?s ?src)
      (in-place ?src ?p)
      (connected ?dst ?src)
    )
    :effect (and
      (not (on ?c ?s))
      (clear ?src)
      (not (available ?h))
      (lifting ?h ?c)
      (not (crate-in-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - store ?a - area ?p - place)
    :precondition (and
      (at-hoist ?h ?a)
      (lifting ?h ?c)
      (clear ?dst)
      (in-place ?dst ?p)
      (in ?s ?dst)
      (connected ?a ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?s)
      (crate-in-place ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store ?dst - store)
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
    :parameters (?h - hoist ?src - store ?dst - transit)
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
    :parameters (?h - hoist ?src - transit ?dst - store)
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