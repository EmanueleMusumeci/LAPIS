(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - store
    loadarea - transit
    hoist0 - hoist
    crate0 - crate
  )

  (:init
    ; Places and surfaces
    (in depot48-1-1 depot48)
    (in container-0-0 container0)

    ; Crate positions
    (on crate0 container-0-0)
    (crate-at crate0 container0)

    ; Hoist position and availability
    (at hoist0 depot48-1-1)
    (available hoist0)

    ; Connectivity
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)

    ; Clear surfaces
    (clear depot48-1-1)
  )

  (:goal
    (and
      (crate-at crate0 depot48)
    )
  )
)