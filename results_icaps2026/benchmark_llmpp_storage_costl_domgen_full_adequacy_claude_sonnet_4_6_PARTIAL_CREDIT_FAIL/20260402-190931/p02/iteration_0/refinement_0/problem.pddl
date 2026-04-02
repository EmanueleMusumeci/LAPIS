(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 - store_area
    container-0-0 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; Hoists locations
    (hoist-at hoist0 depot48-1-1)
    (hoist-at hoist1 depot48-1-2)

    ; Hoists available
    (hoist-available hoist0)
    (hoist-available hoist1)

    ; Crate on container store area
    (on crate0 container-0-0)

    ; Store areas in their places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in container-0-0 container0)

    ; Clear store areas (no crates on depot areas)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Connections among depot storeareas (adjacent)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storearea connected to loadarea
    (connected container-0-0 loadarea)

    ; depot48-1-1 connected to loadarea
    (connected depot48-1-1 loadarea)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)