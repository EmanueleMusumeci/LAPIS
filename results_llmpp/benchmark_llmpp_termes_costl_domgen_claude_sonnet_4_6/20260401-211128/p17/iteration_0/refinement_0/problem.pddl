(define (problem block-building-problem)
  (:domain block-building)

  (:objects
    pos-0-0 pos-0-1 pos-0-2
    pos-1-0 pos-1-1 pos-1-2
    pos-2-0 pos-2-1 pos-2-2
    pos-3-0 pos-3-1 pos-3-2 - position
    n0 n1 n2 n3 - numb
  )

  (:init
    ; Robot starting position
    (at pos-3-0)

    ; Depot
    (depot pos-3-0)

    ; Successor relationships
    (succ n0 n1)
    (succ n1 n2)
    (succ n2 n3)

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

    ; Adjacency (horizontal)
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

    ; Adjacency (vertical)
    (adjacent pos-0-0 pos-1-0)
    (adjacent pos-1-0 pos-0-0)
    (adjacent pos-0-1 pos-1-1)
    (adjacent pos-1-1 pos-0-1)
    (adjacent pos-0-2 pos-1-2)
    (adjacent pos-1-2 pos-0-2)

    (adjacent pos-1-0 pos-2-0)
    (adjacent pos-2-0 pos-1-0)
    (adjacent pos-1-1 pos-2-1)
    (adjacent pos-2-1 pos-1-1)
    (adjacent pos-1-2 pos-2-2)
    (adjacent pos-2-2 pos-1-2)

    (adjacent pos-2-0 pos-3-0)
    (adjacent pos-3-0 pos-2-0)
    (adjacent pos-2-1 pos-3-1)
    (adjacent pos-3-1 pos-2-1)
    (adjacent pos-2-2 pos-3-2)
    (adjacent pos-3-2 pos-2-2)
  )

  (:goal
    (and
      (height pos-0-1 n3)
      (height pos-1-0 n3)
      (height pos-1-2 n3)
      (height pos-2-0 n3)
      (height pos-3-2 n3)
      (not (has-block))
    )
  )
)