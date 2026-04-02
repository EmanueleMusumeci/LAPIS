(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 - crate
    container-0-0 container-0-1 depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - surface
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Adjacency among depot storeareas
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

    ; Crates on surfaces
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Crates in container storeareas
    (crate_in crate0 container-0-0)
    (crate_in crate1 container-0-1)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-1)

    ; Hoist location and availability
    (at_hoist hoist0 depot48-1-2)
    (available hoist0)
  )

  (:goal
    (and
      (crate_in crate0 depot48-1-1)
      (crate_in crate1 depot48-2-1)
    )
  )
)