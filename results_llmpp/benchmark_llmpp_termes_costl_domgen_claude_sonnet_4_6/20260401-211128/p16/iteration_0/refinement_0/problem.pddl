(define (problem building-problem)
  (:domain building)

  (:objects
    pos-0-0 pos-0-1 pos-0-2
    pos-1-0 pos-1-1 pos-1-2
    pos-2-0 pos-2-1 pos-2-2
    pos-3-0 pos-3-1 pos-3-2 - position
    n0 n1 n2 n3 n4 n5 - numb
  )

  (:init
    ; Robot starting position
    (at pos-1-0)

    ; Depot
    (depot pos-1-0)

    ; Neighbor relationships (horizontal)
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

    ; Neighbor relationships (vertical)
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

    ; Number sequence
    (next n0 n1)
    (next n1 n2)
    (next n2 n3)
    (next n3 n4)
    (next n4 n5)

    ; Initial heights (all positions start at 0)
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
  )

  (:goal
    (and
      (height pos-1-2 n5)
      (height pos-2-0 n2)
      (height pos-3-1 n5)
      (height pos-3-2 n4)
      (not (has-block))
    )
  )
)