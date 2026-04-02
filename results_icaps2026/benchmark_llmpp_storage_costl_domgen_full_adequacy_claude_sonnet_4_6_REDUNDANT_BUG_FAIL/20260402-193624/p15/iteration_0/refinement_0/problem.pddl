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
    ; Depot storeareas in depot48
    (area_in depot48-1-1 depot48)
    (area_in depot48-1-2 depot48)
    (area_in depot48-2-1 depot48)
    (area_in depot48-2-2 depot48)

    ; Container storeareas in container0
    (area_in container-0-0 container0)
    (area_in container-0-1 container0)

    ; Adjacent depot storeareas connected (bidirectional via connected predicate)
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

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)

    ; Crates on surfaces
    (on crate0 surface0)
    (on crate1 surface1)

    ; Surfaces in container storeareas
    (in surface0 container-0-0)
    (in surface1 container-0-1)

    ; Crates in container0
    (crate_in crate0 container0)
    (crate_in crate1 container0)

    ; Clear storeareas (depot areas without hoist, container areas without hoist)
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-1)
    (clear container-0-0)
    (clear container-0-1)

    ; Hoist0 is in depot48-1-2
    (at_hoist hoist0 depot48-1-2)

    ; All hoists available
    (available hoist0)
  )

  (:goal
    (and
      (crate_in crate0 depot48)
      (crate_in crate1 depot48)
    )
  )
)