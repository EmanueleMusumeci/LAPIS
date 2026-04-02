(define (domain block-building)
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
    (is-depot ?p - position)
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
    :parameters (?from - position ?to - position ?h-low - numb ?h-high - numb)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height ?from ?h-low)
      (height ?to ?h-high)
      (next ?h-low ?h-high)
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
      (neighbor ?from ?to)
      (height ?from ?h-high)
      (height ?to ?h-low)
      (next ?h-low ?h-high)
    )
    :effect (and
      (at ?to)
      (not (at ?from))
    )
  )

  (:action place
    :parameters (?rob - position ?block - position ?h - numb ?h-new - numb)
    :precondition (and
      (at ?rob)
      (neighbor ?rob ?block)
      (has-block)
      (height ?rob ?h)
      (height ?block ?h)
      (not (is-depot ?block))
      (next ?h ?h-new)
    )
    :effect (and
      (not (has-block))
      (not (height ?block ?h))
      (height ?block ?h-new)
    )
  )

  (:action remove
    :parameters (?rob - position ?block - position ?h - numb ?h-new - numb)
    :precondition (and
      (at ?rob)
      (neighbor ?rob ?block)
      (not (has-block))
      (height ?rob ?h)
      (height ?block ?h)
      (not (is-depot ?block))
      (next ?h-new ?h)
    )
    :effect (and
      (has-block)
      (not (height ?block ?h))
      (height ?block ?h-new)
    )
  )

  (:action create
    :parameters (?depot - position)
    :precondition (and
      (at ?depot)
      (is-depot ?depot)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  (:action destroy
    :parameters (?depot - position)
    :precondition (and
      (at ?depot)
      (is-depot ?depot)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)