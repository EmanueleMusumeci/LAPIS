(define (problem depot_problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; All depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; All container storeareas are in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Adjacency connections among depot storeareas (from map)
    ; Row 1: depot48-1-1 <-> depot48-1-2
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    ; Row 2: depot48-2-1 <-> depot48-2-2
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    ; Column 1: depot48-1-1 <-> depot48-2-1
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    ; Column 2: depot48-1-2 <-> depot48-2-2
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)

    ; All container storeareas are connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)

    ; depot48-2-1 and loadarea are connected
    (connected depot48-2-1 loadarea)

    ; Clear storeareas
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-2-2)

    ; Hoist locations
    (at_hoist hoist1 depot48-2-1)
    (at_hoist hoist2 depot48-1-2)
    (at_hoist hoist0 depot48-2-2)

    ; All hoists are available
    (available hoist0)
    (available hoist1)
    (available hoist2)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
      (on crate1 depot48-1-2)
    )
  )
)