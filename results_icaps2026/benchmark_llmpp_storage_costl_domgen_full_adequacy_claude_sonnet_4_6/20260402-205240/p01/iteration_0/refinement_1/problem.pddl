(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 - crate
    pallet0 pallet1 - surface
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in container-0-0 container0)

    ; Surfaces at store areas
    (surface-at pallet0 container-0-0)
    (surface-at pallet1 depot48-1-1)

    ; Crate on surface in container area
    (crate-on crate0 pallet0)

    ; depot48-1-1 is clear (no crate on its surface, hoist is there but area-clear refers to crate occupancy)
    (area-clear depot48-1-1)

    ; Hoist location and availability
    (hoist-at hoist0 depot48-1-1)
    (hoist-available hoist0)

    ; Connections
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
  )

  (:goal
    (and
      (crate-on crate0 pallet1)
    )
  )
)