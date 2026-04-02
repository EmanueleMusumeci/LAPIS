(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; Hoists locations
    (at_hoist hoist0 depot48-1-1)
    (at_hoist hoist1 depot48-1-2)
    (at_hoist hoist2 depot48-2-2)

    ; All hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; Clear storeareas (depot48-2-1 is clear, hoists occupy others)
    (clear depot48-2-1)

    ; Adjacency connections among depot storeareas (bidirectional)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)

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
      (in depot48-1-1 depot48)
      (on crate0 depot48-1-1)
      (on crate1 depot48-2-1)
    )
  )

)