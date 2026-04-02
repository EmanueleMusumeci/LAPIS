(define (domain build-structures)
  (:requirements :typing :conditional-effects)

  (:types
    position - thing
    height   - thing
  )

  (:predicates
    (at         ?r - position)
    (neighbor   ?p1 - position ?p2 - position)
    (height-at  ?p - position ?h - height)
    (next       ?h1 - height ?h2 - height)
    (has-block)
    (is-depot   ?p - position)
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
      (next ?h-low ?h-high)
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
      (next ?h-low ?h-high)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?h-cur - height ?h-new - height)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (has-block)
      (height-at ?rpos ?h-cur)
      (height-at ?bpos ?h-cur)
      (not (is-depot ?bpos))
      (next ?h-cur ?h-new)
    )
    :effect (and
      (not (has-block))
      (not (height-at ?bpos ?h-cur))
      (height-at ?bpos ?h-new)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?h-cur - height ?h-new - height)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (not (is-depot ?bpos))
      (height-at ?rpos ?h-cur)
      (height-at ?bpos ?h-cur)
      (next ?h-new ?h-cur)
    )
    :effect (and
      (has-block)
      (not (height-at ?bpos ?h-cur))
      (height-at ?bpos ?h-new)
    )
  )

  (:action create-block
    :parameters (?dpos - position)
    :precondition (and
      (at ?dpos)
      (is-depot ?dpos)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  (:action destroy-block
    :parameters (?dpos - position)
    :precondition (and
      (at ?dpos)
      (is-depot ?dpos)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)