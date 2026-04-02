(define (domain build)
  (:requirements :typing :conditional-effects)

  (:types
    position - thing
    numb - thing
  )

  (:predicates
    (at ?r - position)
    (neighbor ?p1 - position ?p2 - position)
    (height ?p - position ?n - numb)
    (next ?n1 - numb ?n2 - numb)
    (has-block)
    (depot ?p - position)
  )

  (:action move
    :parameters (?from - position ?to - position ?n - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?n)
      (height ?to ?n)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-up
    :parameters (?from - position ?to - position ?n1 - numb ?n2 - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?n1)
      (height ?to ?n2)
      (next ?n1 ?n2)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?n1 - numb ?n2 - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?n1)
      (height ?to ?n2)
      (next ?n2 ?n1)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?n1 - numb ?n2 - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (has-block)
      (height ?rpos ?n1)
      (height ?bpos ?n1)
      (not (depot ?bpos))
      (next ?n1 ?n2)
    )
    :effect (and
      (not (has-block))
      (not (height ?bpos ?n1))
      (height ?bpos ?n2)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?n1 - numb ?n2 - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (not (depot ?bpos))
      (height ?rpos ?n1)
      (height ?bpos ?n1)
      (next ?n2 ?n1)
    )
    :effect (and
      (has-block)
      (not (height ?bpos ?n1))
      (height ?bpos ?n2)
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