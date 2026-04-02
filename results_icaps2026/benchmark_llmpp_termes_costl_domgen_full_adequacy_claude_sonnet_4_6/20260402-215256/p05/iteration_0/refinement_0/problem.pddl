(define (problem build-structures-problem)
  (:domain build-structures)

  (:objects
    pos-0-0 pos-0-1 pos-0-2
    pos-1-0 pos-1-1 pos-1-2
    pos-2-0 pos-2-1 pos-2-2
    pos-3-0 pos-3-1 pos-3-2 - position
    h0 h1 h2 h3 h4 h5 - height
  )

  (:init
    ; Robot starting position
    (at pos-2-0)

    ; Depot
    (depot pos-2-0)

    ; Adjacency (bidirectional)
    (adjacent pos-0-0 pos-0-1)
    (adjacent pos-0-1 pos-0-0)
    (adjacent pos-0-1 pos-0-2)
    (adjacent pos-0-2 pos-0-1)

    (adjacent pos-1-0 pos-1-1)
    (adjacent pos-1-1 pos-1-0)
    (adjacent pos-1-1 pos-1-2)
    (adjacent pos-1-2 pos-1-1)

    (adjacent pos-2-0 pos-2-1)
    (adjacent pos-2-1 pos-2-0)
    (adjacent pos-2-1 pos-2-2)
    (adjacent pos-2-2 pos-2-1)

    (adjacent pos-3-0 pos-3-1)
    (adjacent pos-3-1 pos-3-0)
    (adjacent pos-3-1 pos-3-2)
    (adjacent pos-3-2 pos-3-1)

    (adjacent pos-0-0 pos-1-0)
    (adjacent pos-1-0 pos-0-0)
    (adjacent pos-1-0 pos-2-0)
    (adjacent pos-2-0 pos-1-0)
    (adjacent pos-2-0 pos-3-0)
    (adjacent pos-3-0 pos-2-0)

    (adjacent pos-0-1 pos-1-1)
    (adjacent pos-1-1 pos-0-1)
    (adjacent pos-1-1 pos-2-1)
    (adjacent pos-2-1 pos-1-1)
    (adjacent pos-2-1 pos-3-1)
    (adjacent pos-3-1 pos-2-1)

    (adjacent pos-0-2 pos-1-2)
    (adjacent pos-1-2 pos-0-2)
    (adjacent pos-1-2 pos-2-2)
    (adjacent pos-2-2 pos-1-2)
    (adjacent pos-2-2 pos-3-2)
    (adjacent pos-3-2 pos-2-2)

    ; All positions start at height h0
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

    ; Height ordering
    (next-height h0 h1)
    (next-height h1 h2)
    (next-height h2 h3)
    (next-height h3 h4)
    (next-height h4 h5)
  )

  (:goal
    (and
      (height-at pos-2-1 h5)
      (not (has-block))
    )
  )
)