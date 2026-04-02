(define (problem block-building-problem)
  (:domain block-building)

  (:objects
    pos-0-0 pos-0-1 pos-0-2 pos-0-3
    pos-1-0 pos-1-1 pos-1-2 pos-1-3
    pos-2-0 pos-2-1 pos-2-2 pos-2-3
    pos-3-0 pos-3-1 pos-3-2 pos-3-3
    pos-4-0 pos-4-1 pos-4-2 pos-4-3 - position
    h0 h1 h2 h3 h4 - height
  )

  (:init
    ; Robot starting position
    (at pos-2-0)

    ; Depot
    (is-depot pos-2-0)

    ; Height chain
    (next-height h0 h1)
    (next-height h1 h2)
    (next-height h2 h3)
    (next-height h3 h4)

    ; All positions start at height 0
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

    ; Neighboring relationships (row adjacency)
    (neighboring pos-0-0 pos-1-0)
    (neighboring pos-1-0 pos-0-0)
    (neighboring pos-1-0 pos-2-0)
    (neighboring pos-2-0 pos-1-0)
    (neighboring pos-2-0 pos-3-0)
    (neighboring pos-3-0 pos-2-0)
    (neighboring pos-3-0 pos-4-0)
    (neighboring pos-4-0 pos-3-0)

    (neighboring pos-0-1 pos-1-1)
    (neighboring pos-1-1 pos-0-1)
    (neighboring pos-1-1 pos-2-1)
    (neighboring pos-2-1 pos-1-1)
    (neighboring pos-2-1 pos-3-1)
    (neighboring pos-3-1 pos-2-1)
    (neighboring pos-3-1 pos-4-1)
    (neighboring pos-4-1 pos-3-1)

    (neighboring pos-0-2 pos-1-2)
    (neighboring pos-1-2 pos-0-2)
    (neighboring pos-1-2 pos-2-2)
    (neighboring pos-2-2 pos-1-2)
    (neighboring pos-2-2 pos-3-2)
    (neighboring pos-3-2 pos-2-2)
    (neighboring pos-3-2 pos-4-2)
    (neighboring pos-4-2 pos-3-2)

    (neighboring pos-0-3 pos-1-3)
    (neighboring pos-1-3 pos-0-3)
    (neighboring pos-1-3 pos-2-3)
    (neighboring pos-2-3 pos-1-3)
    (neighboring pos-2-3 pos-3-3)
    (neighboring pos-3-3 pos-2-3)
    (neighboring pos-3-3 pos-4-3)
    (neighboring pos-4-3 pos-3-3)

    ; Neighboring relationships (column adjacency)
    (neighboring pos-0-0 pos-0-1)
    (neighboring pos-0-1 pos-0-0)
    (neighboring pos-0-1 pos-0-2)
    (neighboring pos-0-2 pos-0-1)
    (neighboring pos-0-2 pos-0-3)
    (neighboring pos-0-3 pos-0-2)

    (neighboring pos-1-0 pos-1-1)
    (neighboring pos-1-1 pos-1-0)
    (neighboring pos-1-1 pos-1-2)
    (neighboring pos-1-2 pos-1-1)
    (neighboring pos-1-2 pos-1-3)
    (neighboring pos-1-3 pos-1-2)

    (neighboring pos-2-0 pos-2-1)
    (neighboring pos-2-1 pos-2-0)
    (neighboring pos-2-1 pos-2-2)
    (neighboring pos-2-2 pos-2-1)
    (neighboring pos-2-2 pos-2-3)
    (neighboring pos-2-3 pos-2-2)

    (neighboring pos-3-0 pos-3-1)
    (neighboring pos-3-1 pos-3-0)
    (neighboring pos-3-1 pos-3-2)
    (neighboring pos-3-2 pos-3-1)
    (neighboring pos-3-2 pos-3-3)
    (neighboring pos-3-3 pos-3-2)

    (neighboring pos-4-0 pos-4-1)
    (neighboring pos-4-1 pos-4-0)
    (neighboring pos-4-1 pos-4-2)
    (neighboring pos-4-2 pos-4-1)
    (neighboring pos-4-2 pos-4-3)
    (neighboring pos-4-3 pos-4-2)
  )

  (:goal
    (and
      (height-at pos-2-3 h4)
      (height-at pos-3-0 h2)
      (not (has-block))
    )
  )
)