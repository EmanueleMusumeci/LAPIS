(define (domain construction)
  (:requirements :typing :conditional-effects)

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
    (is-depot  ?p - position)
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

  ;; Move up (to position one block higher)
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

  ;; Move down (to position one block lower)
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
    :parameters (?pos - position ?h - height ?h-new - height)
    :precondition (and
      (has-block)
      (next ?h ?h-new)
      (forall (?cur - position)
        (when (at ?cur)
          (and
            (neighbor ?cur ?pos)
            (height-at ?cur ?h)
          )
        )
      )
      (height-at ?pos ?h)
      (not (is-depot ?pos))
    )
    :effect (and
      (not (has-block))
      (not (height-at ?pos ?h))
      (height-at ?pos ?h-new)
    )
  )

  ;; Remove a block from a neighboring position
  (:action remove
    :parameters (?pos - position ?h - height ?h-new - height)
    :precondition (and
      (not (has-block))
      (next ?h-new ?h)
      (forall (?cur - position)
        (when (at ?cur)
          (and
            (neighbor ?cur ?pos)
            (height-at ?cur ?h-new)
          )
        )
      )
      (height-at ?pos ?h)
      (not (is-depot ?pos))
    )
    :effect (and
      (has-block)
      (not (height-at ?pos ?h))
      (height-at ?pos ?h-new)
    )
  )

  ;; Create a block at the depot
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

  ;; Destroy a block at the depot
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