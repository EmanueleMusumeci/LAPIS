(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - store_area
    container-0-0 container-0-1 container-0-2 container-0-3 - store_area
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 crate2 crate3 - crate
  )

  (:init
    ; All depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-1-4 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)
    (in depot48-2-4 depot48)

    ; All container storeareas are in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)
    (in container-0-3 container0)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)
    (on crate3 container-0-3)

    ; Adjacency connections among depot storeareas (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)

    ; Adjacency connections among depot storeareas (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ; Adjacency connections between row 1 and row 2
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)

    ; All container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected container-0-3 loadarea)

    ; depot48-2-1 and loadarea are connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; Clear storeareas (depot48-2-1 is NOT clear: hoist0 is there)
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-2-4)
    (clear depot48-1-1)
    (clear depot48-1-4)

    ; Hoists positions
    (at_hoist hoist0 depot48-2-1)
    (at_hoist hoist1 depot48-1-2)
    (at_hoist hoist2 depot48-1-3)

    ; All hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)
  )

  (:goal
    (and
      (in depot48-1-1 depot48)
      (on crate0 depot48-1-1)
      (on crate1 depot48-2-3)
      (on crate2 depot48-2-4)
      (on crate3 depot48-2-2)
    )
  )

)