(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 - crate
    surface0 surface1 - surface
  )

  (:init
    ; Hoist location and availability
    (at_hoist hoist0 depot48-1-1)
    (available hoist0)

    ; Depot storearea adjacency (connected means adjacent in map)
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

    ; All container storeareas are in container0
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)

    ; depot48-2-1 and loadarea are connected
    (connected depot48-2-1 loadarea)

    ; Surfaces in store areas
    (in surface0 container-0-0)
    (in surface1 container-0-1)

    ; Crates on surfaces
    (on crate0 surface0)
    (on crate1 surface1)

    ; Crates in place (container0)
    (crate_in_place crate0 container0)
    (crate_in_place crate1 container0)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-2)
  )

  (:goal
    (and
      (crate_in_place crate0 depot48)
      (crate_in_place crate1 depot48)
    )
  )
)