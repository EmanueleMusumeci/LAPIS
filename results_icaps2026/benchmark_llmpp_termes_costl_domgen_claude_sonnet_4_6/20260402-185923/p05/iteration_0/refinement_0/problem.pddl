(define (problem block-building-problem)
  (:domain block-building)

  (:objects
    pos-0-0 pos-0-1 pos-0-2
    pos-1-0 pos-1-1 pos-1-2
    pos-2-0 pos-2-1 pos-2-2
    pos-3-0 pos-3-1 pos-3-2 - position
    n0 n1 n2 n3 n4 n5 - numb
  )

  (:init
    ; Robot starting position
    (at pos-2-0)

    ; Depot
    (depot pos-2-0)

    ; Number succession
    (next n0 n1)
    (next n1 n2)
    (next n2 n3)
    (next n3 n4)
    (next n4 n5)

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

    ; Neighboring relationships (horizontal)
    (neighboring pos-0-0 pos-0-1)
    (neighboring pos-0-1 pos-0-0)
    (neighboring pos-0-1 pos-0-2)
    (neighboring pos-0-2 pos-0-1)

    (neighboring pos-1-0 pos-1-1)
    (neighboring pos-1-1 pos-1-0)
    (neighboring pos-1-1 pos-1-2)
    (neighboring pos-1-2 pos-1-1)

    (neighboring pos-2-0 pos-2-1)
    (neighboring pos-2-1 pos-2-0)
    (neighboring pos-2-1 pos-2-2)
    (neighboring pos-2-2 pos-2-1)

    (neighboring pos-3-0 pos-3-1)
    (neighboring pos-3-1 pos-3-0)
    (neighboring pos-3-1 pos-3-2)
    (neighboring pos-3-2 pos-3-1)

    ; Neighboring relationships (vertical)
    (neighboring pos-0-0 pos-1-0)
    (neighboring pos-1-0 pos-0-0)
    (neighboring pos-0-1 pos-1-1)
    (neighboring pos-1-1 pos-0-1)
    (neighboring pos-0-2 pos-1-2)
    (neighboring pos-1-2 pos-0-2)

    (neighboring pos-1-0 pos-2-0)
    (neighboring pos-2-0 pos-1-0)
    (neighboring pos-1-1 pos-2-1)
    (neighboring pos-2-1 pos-1-1)
    (neighboring pos-1-2 pos-2-2)
    (neighboring pos-2-2 pos-1-2)

    (neighboring pos-2-0 pos-3-0)
    (neighboring pos-3-0 pos-2-0)
    (neighboring pos-2-1 pos-3-1)
    (neighboring pos-3-1 pos-2-1)
    (neighboring pos-2-2 pos-3-2)
    (neighboring pos-3-2 pos-2-2)
  )

  (:goal
    (and
      (height pos-2-1 n5)
      (not (has-block))
    )
  )
)