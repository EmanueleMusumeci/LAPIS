(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 - storearea
    container-0-0 - storearea
    hoist0 hoist1 hoist2 - hoist
    crate0 - crate
  )

  (:init
    ; Depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)

    ; Container storeareas are in container0
    (in container-0-0 container0)

    ; Adjacency connections among depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)

    ; depot48-1-2 and loadarea are connected
    (connected depot48-1-2 loadarea)

    ; Hoist positions
    (at hoist0 depot48-1-2)
    (at hoist1 depot48-1-3)
    (at hoist2 depot48-1-1)

    ; All hoists are available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; crate0 is on container-0-0
    (on crate0 container-0-0)

    ; Clear storeareas (those without crates on top)
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)