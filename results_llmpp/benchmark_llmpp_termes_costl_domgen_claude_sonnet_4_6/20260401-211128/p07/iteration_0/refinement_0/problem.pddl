(define (problem blocksworld-5x4-goal)
  (:domain blocksworld-robot)

  (:objects
    pos-0-0 pos-0-1 pos-0-2 pos-0-3
    pos-1-0 pos-1-1 pos-1-2 pos-1-3
    pos-2-0 pos-2-1 pos-2-2 pos-2-3
    pos-3-0 pos-3-1 pos-3-2 pos-3-3
    pos-4-0 pos-4-1 pos-4-2 pos-4-3 - position
    h0 h1 h2 h3 - height
  )

  (:init
    ;; Robot starts at depot
    (at pos-2-0)
    (depot pos-2-0)

    ;; Height chain
    (next h0 h1)
    (next h1 h2)
    (next h2 h3)

    ;; All positions start at height 0
    (height-at pos-0-0 h0)
    (height-at pos-0-1 h0)
    (height-at pos-0-2 h0)
    (height-at pos-0-3 h0)
    (height-at pos-1-0 h0)
    (height-at pos-1-1 h0)
    (height-at pos-1-2 h0)
    (height-at pos-1-3 h0)
    (height-at pos-2-0 h0)
    (height-at pos-2-1 h0)
    (height-at pos-2-2 h0)
    (height-at pos-2-3 h0)
    (height-at pos-3-0 h0)
    (height-at pos-3-1 h0)
    (height-at pos-3-2 h0)
    (height-at pos-3-3 h0)
    (height-at pos-4-0 h0)
    (height-at pos-4-1 h0)
    (height-at pos-4-2 h0)
    (height-at pos-4-3 h0)

    ;; Neighbors (horizontal)
    (neighbor pos-0-0 pos-0-1) (neighbor pos-0-1 pos-0-0)
    (neighbor pos-0-1 pos-0-2) (neighbor pos-0-2 pos-0-1)
    (neighbor pos-0-2 pos-0-3) (neighbor pos-0-3 pos-0-2)
    (neighbor pos-1-0 pos-1-1) (neighbor pos-1-1 pos-1-0)
    (neighbor pos-1-1 pos-1-2) (neighbor pos-1-2 pos-1-1)
    (neighbor pos-1-2 pos-1-3) (neighbor pos-1-3 pos-1-2)
    (neighbor pos-2-0 pos-2-1) (neighbor pos-2-1 pos-2-0)
    (neighbor pos-2-1 pos-2-2) (neighbor pos-2-2 pos-2-1)
    (neighbor pos-2-2 pos-2-3) (neighbor pos-2-3 pos-2-2)
    (neighbor pos-3-0 pos-3-1) (neighbor pos-3-1 pos-3-0)
    (neighbor pos-3-1 pos-3-2) (neighbor pos-3-2 pos-3-1)
    (neighbor pos-3-2 pos-3-3) (neighbor pos-3-3 pos-3-2)
    (neighbor pos-4-0 pos-4-1) (neighbor pos-4-1 pos-4-0)
    (neighbor pos-4-1 pos-4-2) (neighbor pos-4-2 pos-4-1)
    (neighbor pos-4-2 pos-4-3) (neighbor pos-4-3 pos-4-2)

    ;; Neighbors (vertical)
    (neighbor pos-0-0 pos-1-0) (neighbor pos-1-0 pos-0-0)
    (neighbor pos-0-1 pos-1-1) (neighbor pos-1-1 pos-0-1)
    (neighbor pos-0-2 pos-1-2) (neighbor pos-1-2 pos-0-2)
    (neighbor pos-0-3 pos-1-3) (neighbor pos-1-3 pos-0-3)
    (neighbor pos-1-0 pos-2-0) (neighbor pos-2-0 pos-1-0)
    (neighbor pos-1-1 pos-2-1) (neighbor pos-2-1 pos-1-1)
    (neighbor pos-1-2 pos-2-2) (neighbor pos-2-2 pos-1-2)
    (neighbor pos-1-3 pos-2-3) (neighbor pos-2-3 pos-1-3)
    (neighbor pos-2-0 pos-3-0) (neighbor pos-3-0 pos-2-0)
    (neighbor pos-2-1 pos-3-1) (neighbor pos-3-1 pos-2-1)
    (neighbor pos-2-2 pos-3-2) (neighbor pos-3-2 pos-2-2)
    (neighbor pos-2-3 pos-3-3) (neighbor pos-3-3 pos-2-3)
    (neighbor pos-3-0 pos-4-0) (neighbor pos-4-0 pos-3-0)
    (neighbor pos-3-1 pos-4-1) (neighbor pos-4-1 pos-3-1)
    (neighbor pos-3-2 pos-4-2) (neighbor pos-4-2 pos-3-2)
    (neighbor pos-3-3 pos-4-3) (neighbor pos-4-3 pos-3-3)
  )

  (:goal (and
    (height-at pos-0-3 h3)
    (not (has-block))
  ))
)