(define (problem build-structures-problem)
  (:domain build-structures)

  (:objects
    pos-0-0 pos-0-1 pos-0-2
    pos-1-0 pos-1-1 pos-1-2
    pos-2-0 pos-2-1 pos-2-2
    pos-3-0 pos-3-1 pos-3-2 - position
    n0 n1 n2 n3 - numb
  )

  (:init
    ; Robot starting position
    (at pos-2-0)

    ; Depot
    (depot pos-2-0)

    ; Height chain
    (next n0 n1)
    (next n1 n2)
    (next n2 n3)

    ; All positions start at height 0
    (height pos-0-0 n0)
    (height pos-0-1 n0)
    (height pos-0-2 n0)
    (height pos-1-0 n0)
    (height pos-1-1 n0)
    (height pos-1-2 n0)
    (height pos-2-0 n0)
    (height pos-2-1 n0)
    (height pos-2-2 n0)
    (height pos-3-0 n0)
    (height pos-3-1 n0)
    (height pos-3-2 n0)

    ; Neighbors (row adjacency)
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

    ; Neighbors (column adjacency)
    (neighbor pos-0-0 pos-1-0)
    (neighbor pos-1-0 pos-0-0)
    (neighbor pos-1-0 pos-2-0)
    (neighbor pos-2-0 pos-1-0)
    (neighbor pos-2-0 pos-3-0)
    (neighbor pos-3-0 pos-2-0)

    (neighbor pos-0-1 pos-1-1)
    (neighbor pos-1-1 pos-0-1)
    (neighbor pos-1-1 pos-2-1)
    (neighbor pos-2-1 pos-1-1)
    (neighbor pos-2-1 pos-3-1)
    (neighbor pos-3-1 pos-2-1)

    (neighbor pos-0-2 pos-1-2)
    (neighbor pos-1-2 pos-0-2)
    (neighbor pos-1-2 pos-2-2)
    (neighbor pos-2-2 pos-1-2)
    (neighbor pos-2-2 pos-3-2)
    (neighbor pos-3-2 pos-2-2)
  )

  (:goal
    (and
      (height pos-0-0 n2)
      (height pos-0-2 n2)
      (height pos-1-0 n3)
      (height pos-1-2 n3)
      (height pos-2-2 n2)
      (height pos-3-1 n2)
      (not (has-block))
    )
  )
)