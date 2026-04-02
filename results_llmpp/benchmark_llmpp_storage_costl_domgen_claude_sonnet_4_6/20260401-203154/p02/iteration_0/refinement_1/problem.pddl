(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48-1-1 depot48-1-2 container-0-0 - store
    loadarea - transit
    hoist0 hoist1 - hoist
    crate0 - crate
    container-0-0-surface depot48-1-1-surface depot48-1-2-surface - surface
    container0 - place
    depot48 - place
  )

  (:init
    ; Hoist positions
    (at-hoist hoist0 depot48-1-1)
    (at-hoist hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Crate on surface
    (on crate0 container-0-0-surface)

    ; Surface in store
    (in container-0-0-surface container-0-0)

    ; Depot surface in depot store
    (in depot48-1-1-surface depot48-1-1)
    (in depot48-1-2-surface depot48-1-2)

    ; Store in place
    (in-place depot48-1-1 depot48)
    (in-place depot48-1-2 depot48)
    (in-place container-0-0 container0)

    ; Crate in place
    (crate-in-place crate0 container0)

    ; Clear stores
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear container-0-0)

    ; Connections between depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storearea connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-1 connected to loadarea
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
  )

  (:goal
    (and
      (crate-in-place crate0 depot48)
    )
  )
)