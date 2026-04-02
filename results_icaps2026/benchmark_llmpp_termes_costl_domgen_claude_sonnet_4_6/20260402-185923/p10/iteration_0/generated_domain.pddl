(define (domain blocks)
  (:requirements :strips :typing :conditional-effects)

  (:types
    position
    height
  )

  (:predicates
    (at ?r - position)
    (height-at ?p - position ?h - height)
    (next-height ?h1 - height ?h2 - height)
    (neighbor ?p1 - position ?p2 - position)
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
    :parameters (?from - position ?to - position ?h-low - height ?h-high - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h-low)
      (height-at ?to ?h-high)
      (next-height ?h-low ?h-high)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?h-low - height ?h-high - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h-high)
      (height-at ?to ?h-low)
      (next-height ?h-low ?h-high)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?h - height ?h-new - height)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (has-block)
      (height-at ?rpos ?h)
      (height-at ?bpos ?h)
      (next-height ?h ?h-new)
      (not (depot ?bpos))
    )
    :effect (and
      (not (has-block))
      (not (height-at ?bpos ?h))
      (height-at ?bpos ?h-new)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?h - height ?h-new - height)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (height-at ?rpos ?h)
      (height-at ?bpos ?h)
      (next-height ?h-new ?h)
      (not (depot ?bpos))
    )
    :effect (and
      (has-block)
      (not (height-at ?bpos ?h))
      (height-at ?bpos ?h-new)
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