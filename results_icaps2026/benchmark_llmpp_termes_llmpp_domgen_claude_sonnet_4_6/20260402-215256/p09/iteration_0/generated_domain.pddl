(define (domain building)
  (:requirements :typing :conditional-effects)

  (:types
    position
    height
  )

  (:predicates
    (at ?r - position)
    (neighbor ?p1 - position ?p2 - position)
    (height-at ?p - position ?h - height)
    (next ?h1 - height ?h2 - height)
    (has-block)
    (depot ?p - position)
  )

  (:action move
    :parameters (?from - position ?to - position ?h - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h)
      (height-at ?to ?h)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action move-up
    :parameters (?from - position ?to - position ?h1 - height ?h2 - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h1)
      (height-at ?to ?h2)
      (next ?h1 ?h2)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?h1 - height ?h2 - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h1)
      (height-at ?to ?h2)
      (next ?h2 ?h1)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?h1 - height ?h2 - height)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (has-block)
      (height-at ?rpos ?h1)
      (height-at ?bpos ?h1)
      (not (depot ?bpos))
      (next ?h1 ?h2)
    )
    :effect (and
      (not (has-block))
      (not (height-at ?bpos ?h1))
      (height-at ?bpos ?h2)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?h1 - height ?h2 - height)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (not (depot ?bpos))
      (height-at ?rpos ?h1)
      (height-at ?bpos ?h1)
      (next ?h2 ?h1)
    )
    :effect (and
      (has-block)
      (not (height-at ?bpos ?h1))
      (height-at ?bpos ?h2)
    )
  )

  (:action create
    :parameters (?rpos - position)
    :precondition (and
      (at ?rpos)
      (depot ?rpos)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  (:action destroy
    :parameters (?rpos - position)
    :precondition (and
      (at ?rpos)
      (depot ?rpos)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)