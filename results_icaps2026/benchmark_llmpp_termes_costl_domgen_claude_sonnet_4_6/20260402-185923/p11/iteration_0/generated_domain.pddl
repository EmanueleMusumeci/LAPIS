(define (domain building)
  (:requirements :typing :conditional-effects)

  (:types
    position - thing
    height - thing
  )

  (:predicates
    (at ?r - position)
    (neighbor ?p1 - position ?p2 - position)
    (height-at ?p - position ?h - height)
    (next ?h1 - height ?h2 - height)
    (has-block)
    (is-depot ?p - position)
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
    :parameters (?rob - position ?block - position ?h - height ?h-new - height)
    :precondition (and
      (at ?rob)
      (neighbor ?rob ?block)
      (has-block)
      (height-at ?rob ?h)
      (height-at ?block ?h)
      (not (is-depot ?block))
      (next ?h ?h-new)
    )
    :effect (and
      (not (has-block))
      (not (height-at ?block ?h))
      (height-at ?block ?h-new)
    )
  )

  (:action remove
    :parameters (?rob - position ?block - position ?h - height ?h-new - height)
    :precondition (and
      (at ?rob)
      (neighbor ?rob ?block)
      (not (has-block))
      (not (is-depot ?block))
      (height-at ?rob ?h)
      (height-at ?block ?h)
      (next ?h-new ?h)
    )
    :effect (and
      (has-block)
      (not (height-at ?block ?h))
      (height-at ?block ?h-new)
    )
  )

  (:action create
    :parameters (?dep - position)
    :precondition (and
      (at ?dep)
      (is-depot ?dep)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  (:action destroy
    :parameters (?dep - position)
    :precondition (and
      (at ?dep)
      (is-depot ?dep)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)