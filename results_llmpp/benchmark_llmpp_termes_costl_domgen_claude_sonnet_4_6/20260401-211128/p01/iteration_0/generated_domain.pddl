(define (domain blocksworld-robot)
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
      (not (at ?from))
      (at ?to)
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
      (not (at ?from))
      (at ?to)
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?h - numb ?hprev - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?h)
      (height ?to ?hprev)
      (next ?hprev ?h)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
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
    :parameters (?rpos - position ?bpos - position ?h - numb ?hprev - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (not (depot ?bpos))
      (height ?rpos ?h)
      (height ?bpos ?h)
      (next ?hprev ?h)
    )
    :effect (and
      (has-block)
      (not (height ?bpos ?h))
      (height ?bpos ?hprev)
    )
  )

  (:action create-block
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

  (:action destroy-block
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