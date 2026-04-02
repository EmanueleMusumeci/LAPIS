(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    hoist0 - hoist
    crate0 crate1 crate2 - crate
  )

  (:init
    ; Hoist location and availability
    (hoist-at hoist0 depot48-1-2)
    (hoist-available hoist0)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ; Crate locations (store_area)
    (crate-at crate0 container-0-0)
    (crate-at crate1 container-0-1)
    (crate-at crate2 container-0-2)

    ; All crates and container storeareas are in container0
    (crate-in crate0 container0)
    (crate-in crate1 container0)
    (crate-in crate2 container0)
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; All depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-1-3)
    (clear depot48-2-1)
    (clear depot48-1-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)

    ; depot48-2-2 connected to loadarea
    (connected depot48-2-2 loadarea)

    ; Adjacent depot storeareas connected (based on map)
    ; Row 1: depot48-1-1 depot48-1-2 depot48-1-3
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Row 2: depot48-2-1 depot48-2-2 depot48-2-3
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Column connections
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
  )

  (:goal
    (and
      (crate-in crate0 depot48)
      (crate-in crate1 depot48)
      (crate-in crate2 depot48)
    )
  )
)