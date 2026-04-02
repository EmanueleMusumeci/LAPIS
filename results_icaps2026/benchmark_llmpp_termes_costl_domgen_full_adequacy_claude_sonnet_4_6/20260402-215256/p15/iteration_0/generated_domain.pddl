(define (domain blocksworld-robot)
  (:requirements :strips :typing :conditional-effects)

  (:types
    position height
  )

  (:predicates
    (at ?r - position)
    (neighbor ?p1 - position ?p2 - position)
    (height-at ?p - position ?h - height)
    (next ?h1 - height ?h2 - height)
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
    :parameters (?robot-pos - position ?block-pos - position ?h - height ?h-new - height)
    :precondition (and
      (at ?robot-pos)
      (neighbor ?robot-pos ?block-pos)
      (has-block)
      (height-at ?robot-pos ?h)
      (height-at ?block-pos ?h)
      (not (depot ?block-pos))
      (next ?h ?h-new)
    )
    :effect (and
      (not (has-block))
      (not (height-at ?block-pos ?h))
      (height-at ?block-pos ?h-new)
    )
  )

  (:action remove
    :parameters (?robot-pos - position ?block-pos - position ?h - height ?h-new - height)
    :precondition (and
      (at ?robot-pos)
      (neighbor ?robot-pos ?block-pos)
      (not (has-block))
      (not (depot ?block-pos))
      (height-at ?robot-pos ?h)
      (height-at ?block-pos ?h)
      (next ?h-new ?h)
    )
    :effect (and
      (has-block)
      (not (height-at ?block-pos ?h))
      (height-at ?block-pos ?h-new)
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