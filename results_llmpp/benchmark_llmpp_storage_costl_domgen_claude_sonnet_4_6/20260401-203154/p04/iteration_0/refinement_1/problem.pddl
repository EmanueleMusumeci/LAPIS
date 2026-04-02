(define (problem depotprob)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 - crate
    container-0-0-surf container-0-1-surf - surface
    depot48-2-2-surf depot48-2-1-surf - surface
  )

  (:init
    ; Hoist location and availability
    (at_hoist hoist0 depot48-1-1)
    (available hoist0)

    ; Depot storearea connections (adjacent in map)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)

    ; All depot storeareas are in depot48
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-2-1 depot48)
    (in_place depot48-2-2 depot48)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)

    ; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)

    ; All container storeareas are in container0
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)

    ; Surfaces in container storeareas
    (in container-0-0-surf container-0-0)
    (in container-0-1-surf container-0-1)

    ; Surfaces in depot storeareas
    (in depot48-2-2-surf depot48-2-2)
    (in depot48-2-1-surf depot48-2-1)

    ; Crates on surfaces
    (on crate0 container-0-0-surf)
    (on crate1 container-0-1-surf)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-2)
  )

  (:goal
    (and
      (on crate0 depot48-2-2-surf)
      (on crate1 depot48-2-1-surf)
    )
  )
)