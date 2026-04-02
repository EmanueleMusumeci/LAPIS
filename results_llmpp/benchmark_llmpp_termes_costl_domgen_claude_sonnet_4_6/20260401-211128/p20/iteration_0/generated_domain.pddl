(define (domain blocksworld-robot)
  (:requirements :strips :typing :conditional-effects)

  (:types
    position - thing
    height   - thing
  )

  (:predicates
    (at        ?r - position)
    (neighbor  ?p1 - position ?p2 - position)
    (height-at ?p - position ?h - height)
    (next      ?h1 - height ?h2 - height)
    (has-block)
    (depot     ?p - position)
  )

  ;; Move horizontally (same height)
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

  ;; Move up (destination is one block higher)
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

  ;; Move down (destination is one block lower)
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

  ;; Place a block at a neighboring position
  (:action place
    :parameters (?pos - position ?target - position ?h - height ?h-new - height)
    :precondition (and
      (at ?pos)
      (neighbor ?pos ?target)
      (has-block)
      (height-at ?pos ?h)
      (height-at ?target ?h)
      (not (depot ?target))
      (next ?h ?h-new)
    )
    :effect (and
      (not (has-block))
      (not (height-at ?target ?h))
      (height-at ?target ?h-new)
    )
  )

  ;; Remove a block from a neighboring position
  (:action remove
    :parameters (?pos - position ?target - position ?h - height ?h-new - height)
    :precondition (and
      (at ?pos)
      (neighbor ?pos ?target)
      (not (has-block))
      (not (depot ?target))
      (height-at ?pos ?h)
      (height-at ?target ?h-new)
      (next ?h ?h-new)
    )
    :effect (and
      (has-block)
      (not (height-at ?target ?h-new))
      (height-at ?target ?h)
    )
  )

  ;; Create a block at the depot
  (:action create
    :parameters (?pos - position)
    :precondition (and
      (at ?pos)
      (depot ?pos)
      (not (has-block))
    )
    :effect (and
      (has-block)
    )
  )

  ;; Destroy a block at the depot
  (:action destroy
    :parameters (?pos - position)
    :precondition (and
      (at ?pos)
      (depot ?pos)
      (has-block)
    )
    :effect (and
      (not (has-block))
    )
  )

)