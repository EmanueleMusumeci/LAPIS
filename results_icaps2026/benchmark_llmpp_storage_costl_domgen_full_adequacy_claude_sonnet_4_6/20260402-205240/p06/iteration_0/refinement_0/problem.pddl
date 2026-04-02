(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
    container-0-0-surface container-0-1-surface - surface
  )

  (:init
    ; Hoists locations
    (hoist-at hoist0 depot48-1-1)
    (hoist-at hoist1 depot48-1-2)
    (hoist-at hoist2 depot48-2-2)

    ; All hoists available
    (hoist-available hoist0)
    (hoist-available hoist1)
    (hoist-available hoist2)

    ; Crates on surfaces
    (crate-on crate0 container-0-0-surface)
    (crate-on crate1 container-0-1-surface)

    ; Crates in container0
    (crate-in crate0 container0)
    (crate-in crate1 container0)

    ; Container storeareas in container0
    (area-in container-0-0 container0)
    (area-in container-0-1 container0)

    ; Depot storeareas in depot48
    (area-in depot48-1-1 depot48)
    (area-in depot48-1-2 depot48)
    (area-in depot48-2-1 depot48)
    (area-in depot48-2-2 depot48)

    ; Clear areas
    (area-clear depot48-2-1)

    ; Adjacency in depot48 (grid connections)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)
  )

  (:goal
    (and
      (crate-in crate0 depot48)
      (crate-in crate1 depot48)
    )
  )
)