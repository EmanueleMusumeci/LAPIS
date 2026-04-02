(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - storearea
    container-0-0 container-0-1 container-0-2 - storearea
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 - crate
  )

  (:init
    ; depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ; container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; adjacency within depot48 (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; adjacency within depot48 (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; adjacency within depot48 (between rows)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-2)

    ; depot48-2-3 and loadarea connected
    (connected depot48-2-3 loadarea)
    (connected loadarea depot48-2-3)

    ; crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ; clear storeareas
    (clear depot48-2-3)
    (clear depot48-2-1)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; hoist locations
    (at hoist0 depot48-2-2)
    (at hoist1 depot48-1-3)

    ; hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
      (on crate1 depot48-2-1)
      (on crate2 depot48-1-2)
    )
  )
)