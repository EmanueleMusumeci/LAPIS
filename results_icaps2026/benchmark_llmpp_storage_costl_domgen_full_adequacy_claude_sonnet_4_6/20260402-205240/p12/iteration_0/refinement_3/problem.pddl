(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    depot48-1-1 - storearea
    container-0-0-area - storearea
    container-0-0 - pallet
    pallet0 - pallet
    loadarea - transitarea
    hoist0 - hoist
    crate0 - crate
  )

  (:init
    ; Hoists locations
    (at hoist0 depot48-1-1)

    ; Hoists availability
    (available hoist0)

    ; Storearea membership
    (in depot48-1-1 depot48)
    (in container-0-0-area container0)

    ; Crate on surface
    (on crate0 container-0-0)

    ; Clear areas and surfaces
    (clear depot48-1-1)
    (clear pallet0)

    ; Connections
    (connected container-0-0-area loadarea)
    (connected loadarea container-0-0-area)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
  )

  (:goal
    (and
      (on crate0 pallet0)
    )
  )
)