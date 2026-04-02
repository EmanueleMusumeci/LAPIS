(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 - storearea
    container-0-0 - storearea
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; Depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)

    ; Container storeareas are in container0
    (in container-0-0 container0)

    ; Map connectivity: depot48-1-1 and depot48-1-2 are adjacent
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; depot48-1-2 and loadarea are connected
    (connected depot48-1-2 loadarea)
    (connected-to loadarea depot48-1-2)

    ; All container storeareas are connected to loadarea
    (connected container-0-0 loadarea)
    (connected-to loadarea container-0-0)

    ; crate0 is on container-0-0
    (on crate0 container-0-0)
    (crate-at crate0 container0)

    ; Clear storeareas (those without crates on them)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Hoists placement
    (at hoist1 depot48-1-1)
    (at hoist0 depot48-1-2)

    ; All hoists are available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (crate-at crate0 depot48)
    )
  )
)