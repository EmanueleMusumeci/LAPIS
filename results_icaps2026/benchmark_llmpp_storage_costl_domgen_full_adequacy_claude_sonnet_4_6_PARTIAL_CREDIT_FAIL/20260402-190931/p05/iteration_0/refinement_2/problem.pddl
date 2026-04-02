(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 - crate
    container-0-0-surf container-0-1-surf - surface
    depot48-1-1-surf depot48-1-2-surf depot48-2-1-surf depot48-2-2-surf - surface
  )

  (:init
    ; Hoist locations
    (at_hoist hoist0 depot48-1-1)
    (at_hoist hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Crates on surfaces
    (on crate0 container-0-0-surf)
    (on crate1 container-0-1-surf)

    ; Surfaces in store areas
    (in container-0-0-surf container-0-0)
    (in container-0-1-surf container-0-1)

    ; Surfaces in depot store areas
    (in depot48-1-1-surf depot48-1-1)
    (in depot48-1-2-surf depot48-1-2)
    (in depot48-2-1-surf depot48-2-1)
    (in depot48-2-2-surf depot48-2-2)

    ; Crates in container0
    (crate_in crate0 container0)
    (crate_in crate1 container0)

    ; Container storeareas in container0
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)

    ; Depot storeareas in depot48
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-2-1 depot48)
    (in_place depot48-2-2 depot48)

    ; Clear storeareas
    (clear depot48-2-1)
    (clear depot48-2-2)

    ; Adjacency connections among depot storeareas (bidirectional via connected)
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

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected depot48-2-2 loadarea)
  )

  (:goal
    (and
      (crate_in crate0 depot48)
      (crate_in crate1 depot48)
    )
  )
)