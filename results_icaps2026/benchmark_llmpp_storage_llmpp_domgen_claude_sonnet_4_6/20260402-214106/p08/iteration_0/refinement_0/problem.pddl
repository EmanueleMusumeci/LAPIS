(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 - crate
    container0 depot48 - place
    container-0-0 container-0-1 container-0-2 depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - surface
  )

  (:init
    ; Hoists locations
    (hoist-at hoist0 depot48-2-2)
    (hoist-at hoist1 depot48-1-3)

    ; Hoists available
    (hoist-available hoist0)
    (hoist-available hoist1)

    ; Crates on surfaces
    (crate-on crate0 container-0-0)
    (crate-on crate1 container-0-1)
    (crate-on crate2 container-0-2)

    ; Crates in container0
    (crate-in crate0 container0)
    (crate-in crate1 container0)
    (crate-in crate2 container0)

    ; Container storeareas in container0
    (in-place container-0-0 container0)
    (in-place container-0-1 container0)
    (in-place container-0-2 container0)

    ; Depot storeareas in depot48
    (in-place depot48-1-1 depot48)
    (in-place depot48-1-2 depot48)
    (in-place depot48-1-3 depot48)
    (in-place depot48-2-1 depot48)
    (in-place depot48-2-2 depot48)
    (in-place depot48-2-3 depot48)

    ; Clear areas
    (area-clear depot48-2-3)
    (area-clear depot48-2-1)
    (area-clear depot48-1-1)
    (area-clear depot48-1-2)

    ; Depot adjacency connections (bidirectional)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
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

    ; depot48-2-3 and loadarea connected
    (connected depot48-2-3 loadarea)
    (connected loadarea depot48-2-3)
  )

  (:goal
    (and
      (crate-in crate0 depot48)
      (crate-in crate1 depot48)
      (crate-in crate2 depot48)
    )
  )
)