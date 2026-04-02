(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    loadarea - transit_area
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 crate2 - crate
    depot48-1-1-surface depot48-1-2-surface depot48-1-3-surface
    depot48-2-1-surface depot48-2-2-surface depot48-2-3-surface
    container-0-0-surface container-0-1-surface container-0-2-surface - surface
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Crates on container storeareas
    (on crate0 container-0-0-surface)
    (on crate1 container-0-1-surface)
    (on crate2 container-0-2-surface)

    ; Crates in container0
    (in_place crate0 container0)
    (in_place crate1 container0)
    (in_place crate2 container0)

    ; Clear depot storeareas
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)

    ; Hoist positions
    (at_hoist hoist1 depot48-2-1)
    (at_hoist hoist2 depot48-2-2)
    (at_hoist hoist0 depot48-2-3)

    ; Hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; Depot adjacency (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Depot adjacency (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Depot adjacency (columns)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)
    (connected loadarea container-0-2)

    ; depot48-2-2 and loadarea connected
    (connected depot48-2-2 loadarea)
    (connected loadarea depot48-2-2)
  )

  (:goal
    (and
      (in_place crate0 depot48)
      (in_place crate1 depot48)
      (in_place crate2 depot48)
    )
  )
)