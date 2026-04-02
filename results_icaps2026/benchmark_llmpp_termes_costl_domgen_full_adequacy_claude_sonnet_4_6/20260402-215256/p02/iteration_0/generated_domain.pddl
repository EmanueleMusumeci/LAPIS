(define (domain block-building)
  (:requirements :typing :conditional-effects)

  (:types
    position - thing
    height   - thing
  )

  (:predicates
    (at           ?r - position)
    (neighbor     ?p1 - position ?p2 - position)
    (height-at    ?p - position ?h - height)
    (next-height  ?h1 - height ?h2 - height)
    (has-block)
    (depot        ?p - position)
  )

  ;; Move horizontally: old and new positions must be at the same height
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

  ;; Move up: new position is one block higher than old position
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

  ;; Move down: new position is one block lower than old position
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
      (next-height ?h ?h-new)
      (not (depot ?block-pos))
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
      (height-at ?robot-pos ?h)
      (height-at ?block-pos ?h)
      (next-height ?h-new ?h)
      (not (depot ?block-pos))
    )
    :effect (and
      (has-block)
      (not (height-at ?block-pos ?h))
      (height-at ?block-pos ?h-new)
    )
  )

  ;; Create a block at the depot
  (:action create
    :parameters (?robot-pos - position)
    :precondition (and
      (at ?robot-pos)
      (depot ?robot-pos)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  ;; Destroy a block at the depot
  (:action destroy
    :parameters (?robot-pos - position)
    :precondition (and
      (at ?robot-pos)
      (depot ?robot-pos)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )
)