(define (domain blocksworld-robot)
  (:requirements :strips :typing :conditional-effects)

  (:types
    position - thing
    numb - thing
  )

  (:predicates
    (at ?r - position)
    (neighboring ?p1 - position ?p2 - position)
    (height ?p - position ?n - numb)
    (next ?n1 - numb ?n2 - numb)
    (has-block)
    (depot ?p - position)
  )

  (:action move
    :parameters (?from - position ?to - position ?n - numb)
    :precondition (and
      (at ?from)
      (neighboring ?from ?to)
      (height ?from ?n)
      (height ?to ?n)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-up
    :parameters (?from - position ?to - position ?n - numb ?m - numb)
    :precondition (and
      (at ?from)
      (neighboring ?from ?to)
      (height ?from ?n)
      (height ?to ?m)
      (next ?n ?m)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?n - numb ?m - numb)
    :precondition (and
      (at ?from)
      (neighboring ?from ?to)
      (height ?from ?m)
      (height ?to ?n)
      (next ?n ?m)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?n - numb ?m - numb)
    :precondition (and
      (at ?rpos)
      (neighboring ?rpos ?bpos)
      (has-block)
      (height ?rpos ?n)
      (height ?bpos ?n)
      (not (depot ?bpos))
      (next ?n ?m)
    )
    :effect (and
      (not (has-block))
      (not (height ?bpos ?n))
      (height ?bpos ?m)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?n - numb ?m - numb)
    :precondition (and
      (at ?rpos)
      (neighboring ?rpos ?bpos)
      (not (has-block))
      (not (depot ?bpos))
      (height ?rpos ?n)
      (height ?bpos ?n)
      (next ?m ?n)
    )
    :effect (and
      (has-block)
      (not (height ?bpos ?n))
      (height ?bpos ?m)
    )
  )

  (:action create
    :parameters (?rpos - position ?n - numb)
    :precondition (and
      (at ?rpos)
      (depot ?rpos)
      (not (has-block))
      (height ?rpos ?n)
    )
    :effect (and
      (has-block)
    )
  )

  (:action destroy
    :parameters (?rpos - position ?n - numb)
    :precondition (and
      (at ?rpos)
      (depot ?rpos)
      (has-block)
      (height ?rpos ?n)
    )
    :effect (and
      (not (has-block))
    )
  )

)