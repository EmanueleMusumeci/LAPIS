(define (problem blocksworld-robot-problem)
  (:domain blocksworld-robot)

  (:objects
    pos-0-0 pos-0-1 pos-0-2
    pos-1-0 pos-1-1 pos-1-2
    pos-2-0 pos-2-1 pos-2-2
    pos-3-0 pos-3-1 pos-3-2 - position
    h0 h1 h2 h3 h4 - height
  )

  (:init
    ;; Robot starting position
    (at pos-2-0)

    ;; Depot
    (depot pos-2-0)

    ;; Height chain
    (next h0 h1)
    (next h1 h2)
    (next h2 h3)
    (next h3 h4)

    ;; All positions start at height 0
    (height-at pos-0-0 h0)
    (height-at pos-0-1 h0)
    (height-at pos-0-2 h0)
    (height-at pos-1-0 h0)
    (height-at pos-1-1 h0)
    (height-at pos-1-2 h0)
    (height-at pos-2-0 h0)
    (height-at pos-2-1 h0)
    (height-at pos-2-2 h0)
    (height-at pos-3-0 h0)
    (height-at pos-3-1 h0)
    (height-at pos-3-2 h0)

    ;; Neighbor relationships (horizontal)
    (neighbor pos-0-0 pos-0-1)
    (neighbor pos-0-1 pos-0-0)
    (neighbor pos-0-1 pos-0-2)
    (neighbor pos-0-2 pos-0-1)

    (neighbor pos-1-0 pos-1-1)
    (neighbor pos-1-1 pos-1-0)
    (neighbor pos-1-1 pos-1-2)
    (neighbor pos-1-2 pos-1-1)

    (neighbor pos-2-0 pos-2-1)
    (neighbor pos-2-1 pos-2-0)
    (neighbor pos-2-1 pos-2-2)
    (neighbor pos-2-2 pos-2-1)

    (neighbor pos-3-0 pos-3-1)
    (neighbor pos-3-1 pos-3-0)
    (neighbor pos-3-1 pos-3-2)
    (neighbor pos-3-2 pos-3-1)

    ;; Neighbor relationships (vertical)
    (neighbor pos-0-0 pos-1-0)
    (neighbor pos-1-0 pos-0-0)
    (neighbor pos-0-1 pos-1-1)
    (neighbor pos-1-1 pos-0-1)
    (neighbor pos-0-2 pos-1-2)
    (neighbor pos-1-2 pos-0-2)

    (neighbor pos-1-0 pos-2-0)
    (neighbor pos-2-0 pos-1-0)
    (neighbor pos-1-1 pos-2-1)
    (neighbor pos-2-1 pos-1-1)
    (neighbor pos-1-2 pos-2-2)
    (neighbor pos-2-2 pos-1-2)

    (neighbor pos-2-0 pos-3-0)
    (neighbor pos-3-0 pos-2-0)
    (neighbor pos-2-1 pos-3-1)
    (neighbor pos-3-1 pos-2-1)
    (neighbor pos-2-2 pos-3-2)
    (neighbor pos-3-2 pos-2-2)
  )

  (:goal
    (and
      (height-at pos-0-0 h4)
      (height-at pos-0-2 h2)
      (height-at pos-1-0 h4)
      (height-at pos-1-1 h2)
      (height-at pos-3-0 h2)
      (height-at pos-3-2 h2)
      (not (has-block))
    )
  )
)