(define (domain building)
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
    :parameters (?from - position ?to - position ?h - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?h)
      (height ?to ?h)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-up
    :parameters (?from - position ?to - position ?h - numb ?hnext - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?h)
      (height ?to ?hnext)
      (next ?h ?hnext)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?h - numb ?hnext - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?hnext)
      (height ?to ?h)
      (next ?h ?hnext)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?h - numb ?hnext - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (has-block)
      (height ?rpos ?h)
      (height ?bpos ?h)
      (not (depot ?bpos))
      (next ?h ?hnext)
    )
    :effect (and
      (not (has-block))
      (not (height ?bpos ?h))
      (height ?bpos ?hnext)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?h - numb ?hnext - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (not (depot ?bpos))
      (height ?rpos ?h)
      (height ?bpos ?hnext)
      (next ?h ?hnext)
    )
    :effect (and
      (has-block)
      (not (height ?bpos ?hnext))
      (height ?bpos ?h)
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