(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - storearea
    container-0-0 container-0-1 container-0-2 - storearea
    loadarea - transitarea
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 crate2 - crate
    container0 depot48 - place
  )

  (:init
    ; Hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; Hoist locations
    (at hoist0 depot48-2-3)
    (at hoist1 depot48-2-1)
    (at hoist2 depot48-2-2)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ; Clear depot storeareas
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)

    ; Adjacency connections among depot storeareas (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Adjacency connections among depot storeareas (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Adjacency connections between rows
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)

    ; depot48-2-1, depot48-2-2, depot48-2-3 connected to loadarea
    (connected depot48-2-1 loadarea)
    (connected depot48-2-2 loadarea)
    (connected depot48-2-3 loadarea)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
      (on crate1 depot48-1-2)
      (on crate2 depot48-1-3)
    )
  )
)