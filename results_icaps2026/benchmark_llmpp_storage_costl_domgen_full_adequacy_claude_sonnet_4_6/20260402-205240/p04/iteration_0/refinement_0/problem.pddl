(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; Hoist location and availability
    (at_hoist hoist0 depot48-1-1)
    (available hoist0)

    ; Depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; Container storeareas are in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Crate in place facts
    (crate_in_place crate0 container0)
    (crate_in_place crate1 container0)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-2)

    ; Adjacency connections among depot storeareas (horizontal and vertical)
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

    ; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)
  )

  (:goal
    (and
      (crate_in_place crate0 depot48)
      (crate_in_place crate1 depot48)
    )
  )
)