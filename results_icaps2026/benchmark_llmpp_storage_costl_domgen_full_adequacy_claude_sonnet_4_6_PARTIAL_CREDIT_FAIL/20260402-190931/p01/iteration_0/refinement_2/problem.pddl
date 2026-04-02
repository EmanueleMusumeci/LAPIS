(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 - crate
    depot48-1-1-surface container-0-0-surface - surface
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in container-0-0 container0)

    ; Surfaces in places
    (in depot48-1-1-surface depot48)
    (in container-0-0-surface container0)

    ; Crate on container store area surface
    (on crate0 container-0-0-surface)
    (in-store crate0 container-0-0)

    ; Hoist location and availability
    (at-hoist hoist0 depot48-1-1)
    (available hoist0)

    ; Clear areas (container-0-0 has no hoist, so it is clear for hoist movement)
    (clear container-0-0)

    ; Connections
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
  )

  (:goal
    (and
      (in-store crate0 depot48-1-1)
    )
  )
)