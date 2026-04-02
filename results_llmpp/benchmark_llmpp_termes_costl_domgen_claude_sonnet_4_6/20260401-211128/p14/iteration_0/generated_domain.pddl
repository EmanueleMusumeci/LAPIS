(define (domain blocksworld-robot)
  (:requirements :strips :typing :conditional-effects)

  (:types
    position - thing
    height   - thing
  )

  (:predicates
    (at          ?r - position)
    (neighbor    ?p1 - position ?p2 - position)
    (height-at   ?p - position ?h - height)
    (next-height ?h1 - height ?h2 - height)
    (has-block)
    (depot       ?p - position)
  )

  ;; Move horizontally to a neighboring position at the same height
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

  ;; Move up to a neighboring position that is one block higher
  (:action move-up
    :parameters (?from - position ?to - position ?h-low - height ?h-high - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h-low)
      (height-at ?to ?h-high)
      (next-height ?h-low ?h-high)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  ;; Move down to a neighboring position that is one block lower
  (:action move-down
    :parameters (?from - position ?to - position ?h-low - height ?h-high - height)
    :precondition (and
      (at ?from)
      (neighbor ?from ?to)
      (height-at ?from ?h-high)
      (height-at ?to ?h-low)
      (next-height ?h-low ?h-high)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  ;; Place a block at a neighboring position
  (:action place
    :parameters (?robot-pos - position ?block-pos - position ?h - height ?h-new - height)
    :precondition (and
      (at ?robot-pos)
      (neighbor ?robot-pos ?block-pos)
      (has-block)
      (height-at ?robot-pos ?h)
      (height-at ?block-pos ?h)
      (not (depot ?block-pos))
      (next-height ?h ?h-new)
    )
    :effect (and
      (not (has-block))
      (not (height-at ?block-pos ?h))
      (height-at ?block-pos ?h-new)
    )
  )

  ;; Remove a block from a neighboring position
  (:action remove
    :parameters (?robot-pos - position ?block-pos - position ?h - height ?h-new - height)
    :precondition (and
      (at ?robot-pos)
      (neighbor ?robot-pos ?block-pos)
      (not (has-block))
      (not (depot ?block-pos))
      (height-at ?robot-pos ?h)
      (height-at ?block-pos ?h-new)
      (next-height ?h ?h-new)
    )
    :effect (and
      (has-block)
      (not (height-at ?block-pos ?h-new))
      (height-at ?block-pos ?h)
    )
  )

  ;; Create a block at the depot
  (:action create
    :parameters (?dep - position)
    :precondition (and
      (at ?dep)
      (depot ?dep)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  ;; Destroy a block at the depot
  (:action destroy
    :parameters (?dep - position)
    :precondition (and
      (at ?dep)
      (depot ?dep)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)