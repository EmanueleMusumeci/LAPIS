(define (domain depot)
  (:requirements :strips :typing)

  (:types
    place area hoist crate surface - physical-object
    store transit - area
  )

  (:predicates
    (at ?h - hoist ?a - area)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?s - surface ?st - store)
    (connected ?a1 - area ?a2 - area)
    (clear ?st - store)
    (at-place ?c - crate ?p - place)
    (in-place ?st - store ?p - place)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?src - store ?dst - area ?p - place)
    :precondition (and
      (available ?h)
      (at ?h ?dst)
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
      (not (at-place ?c ?p))
    )
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?dst - store ?area - area ?p - place)
    :precondition (and
      (at ?h ?area)
      (lifting ?h ?c)
      (clear ?dst)
      (in-place ?dst ?p)
      (in ?s ?dst)
      (connected ?area ?dst)
    )
    :effect (and
      (not (lifting ?h ?c))
      (available ?h)
      (not (clear ?dst))
      (on ?c ?s)
      (at-place ?c ?p)
    )
  )

  (:action move
    :parameters (?h - hoist ?src - store ?dst - store)
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
    :parameters (?h - hoist ?src - store ?dst - transit)
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
    :parameters (?h - hoist ?src - transit ?dst - store)
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