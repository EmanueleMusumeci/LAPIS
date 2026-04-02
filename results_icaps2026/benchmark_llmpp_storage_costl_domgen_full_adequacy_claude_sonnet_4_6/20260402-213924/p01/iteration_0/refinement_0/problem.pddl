(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 - crate
    container-0-0-surface - surface
  )

  (:init
    ; Hoist location and availability
    (at-hoist hoist0 depot48-1-1)
    (available hoist0)

    ; Crate on surface
    (on crate0 container-0-0-surface)

    ; Surface in store area
    (in container-0-0-surface container-0-0)

    ; Store areas in places
    (in-place depot48-1-1 depot48)
    (in-place container-0-0 container0)

    ; Crate in container0
    (in-crate crate0 container0)

    ; Connectivity: container storearea to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; Connectivity: depot48-1-1 and loadarea
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)

    ; Clear areas: depot48-1-1 has no crate on it; container-0-0 is occupied by crate0
    (clear depot48-1-1)
  )

  (:goal
    (and
      (in-crate crate0 depot48)
    )
  )
)