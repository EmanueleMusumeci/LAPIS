(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - storearea
    container-0-0 container-0-1 - storearea
    loadarea - transitarea
    hoist0 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; adjacency within depot48 (grid connections)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; crates on surfaces
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; crates in storeareas
    (in-store crate0 container-0-0)
    (in-store crate1 container-0-1)

    ; hoist0 location and availability
    (at hoist0 depot48-1-1)
    (available hoist0)

    ; clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-2)
  )

  (:goal
    (and
      (in-store crate0 depot48-1-1)
      (in-store crate1 depot48-1-2)
    )
  )
)