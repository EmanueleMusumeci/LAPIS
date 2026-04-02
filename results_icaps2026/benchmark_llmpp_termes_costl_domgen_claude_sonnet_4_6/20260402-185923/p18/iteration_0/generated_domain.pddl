(define (domain build-structures)
  (:requirements :typing :conditional-effects)

  (:types
    position - thing
    numb - thing
  )

  (:predicates
    (at ?r - position)
    (height ?p - position ?h - numb)
    (next ?h1 - numb ?h2 - numb)
    (neighbor ?p1 - position ?p2 - position)
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
    :parameters (?from - position ?to - position ?h1 - numb ?h2 - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?h1)
      (height ?to ?h2)
      (next ?h1 ?h2)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action move-down
    :parameters (?from - position ?to - position ?h1 - numb ?h2 - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?h1)
      (height ?to ?h2)
      (next ?h2 ?h1)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action place
    :parameters (?rpos - position ?bpos - position ?h1 - numb ?h2 - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (has-block)
      (height ?rpos ?h1)
      (height ?bpos ?h1)
      (next ?h1 ?h2)
      (not (depot ?bpos))
    )
    :effect (and
      (not (has-block))
      (not (height ?bpos ?h1))
      (height ?bpos ?h2)
    )
  )

  (:action remove
    :parameters (?rpos - position ?bpos - position ?h1 - numb ?h2 - numb)
    :precondition (and
      (at ?rpos)
      (neighbor ?rpos ?bpos)
      (not (has-block))
      (height ?rpos ?h1)
      (height ?bpos ?h1)
      (next ?h2 ?h1)
      (not (depot ?bpos))
    )
    :effect (and
      (has-block)
      (not (height ?bpos ?h1))
      (height ?bpos ?h2)
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