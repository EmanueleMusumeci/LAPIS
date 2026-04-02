(define (domain blocksworld-robot)
  (:requirements :typing :conditional-effects)

  (:types
    position - thing
    numb - thing
  )

  (:predicates
    (at ?r - position)
    (neighboring ?p1 - position ?p2 - position)
    (height ?p - position ?n - numb)
    (succ ?n1 - numb ?n2 - numb)
    (has-block)
    (depot ?p - position)
  )

  (:action move
    :parameters (?from - position ?to - position ?h - numb)
    :precondition (and
      (at ?from)
      (neighboring ?from ?to)
      (height ?from ?h)
      (height ?to ?h)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-up
    :parameters (?from - position ?to - position ?h-low - numb ?h-high - numb)
    :precondition (and
      (at ?from)
      (neighboring ?from ?to)
      (height ?from ?h-low)
      (height ?to ?h-high)
      (succ ?h-low ?h-high)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?h-low - numb ?h-high - numb)
    :precondition (and
      (at ?from)
      (neighboring ?from ?to)
      (height ?from ?h-high)
      (height ?to ?h-low)
      (succ ?h-low ?h-high)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?h - numb ?h-new - numb)
    :precondition (and
      (at ?rpos)
      (neighboring ?rpos ?bpos)
      (has-block)
      (height ?rpos ?h)
      (height ?bpos ?h)
      (succ ?h ?h-new)
      (not (depot ?bpos))
    )
    :effect (and
      (not (has-block))
      (not (height ?bpos ?h))
      (height ?bpos ?h-new)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?h - numb ?h-new - numb)
    :precondition (and
      (at ?rpos)
      (neighboring ?rpos ?bpos)
      (not (has-block))
      (height ?rpos ?h)
      (height ?bpos ?h)
      (succ ?h-new ?h)
      (not (depot ?bpos))
    )
    :effect (and
      (has-block)
      (not (height ?bpos ?h))
      (height ?bpos ?h-new)
    )
  )

  (:action create
    :parameters (?p - position)
    :precondition (and
      (at ?p)
      (depot ?p)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  (:action destroy
    :parameters (?p - position)
    :precondition (and
      (at ?p)
      (depot ?p)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)