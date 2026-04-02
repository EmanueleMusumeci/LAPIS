(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store
    container-0-0 container-0-1 - store
    loadarea - transit
    hoist0 hoist1 - hoist
    crate0 crate1 - crate
    container-0-0-surface container-0-1-surface - surface
  )

  (:init
    ; Places
    (in-place depot48-1-1 depot48)
    (in-place depot48-1-2 depot48)
    (in-place depot48-2-1 depot48)
    (in-place depot48-2-2 depot48)
    (in-place container-0-0 container0)
    (in-place container-0-1 container0)

    ; Surfaces in stores
    (in container-0-0-surface container-0-0)
    (in container-0-1-surface container-0-1)

    ; Crates on surfaces
    (on crate0 container-0-0-surface)
    (on crate1 container-0-1-surface)

    ; Crate locations
    (at-place crate0 container0)
    (at-place crate1 container0)

    ; Hoist positions
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Clear stores
    (clear depot48-2-1)
    (clear depot48-2-2)

    ; Adjacency within depot48 (grid)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)

    ; Depot store to loadarea connections
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; Container stores to loadarea connections
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)
  )

  (:goal
    (and
      (at-place crate0 depot48)
      (at-place crate1 depot48)
    )
  )
)