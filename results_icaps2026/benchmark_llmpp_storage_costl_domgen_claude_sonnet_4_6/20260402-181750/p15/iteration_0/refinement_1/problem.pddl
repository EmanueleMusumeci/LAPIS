(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - storearea
    container-0-0 container-0-1 - storearea
    loadarea - transitarea
    hoist0 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Crates in container0
    (in-place crate0 container0)
    (in-place crate1 container0)

    ; Clear depot storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-1)

    ; Hoist0 location and availability
    (at hoist0 depot48-1-2)
    (available hoist0)

    ; Adjacency connections among depot storeareas (row-by-row and column-by-column)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)
  )

  (:goal
    (and
      (in-place crate0 depot48)
      (in-place crate1 depot48)
    )
  )
)