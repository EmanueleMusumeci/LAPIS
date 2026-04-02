(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 - storearea
    container-0-0 - storearea
    loadarea - transitarea
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)

    ; container storeareas in container0
    (in container-0-0 container0)

    ; adjacency within depot48 (map: depot48-1-1 depot48-1-2)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)

    ; depot48-1-1 connected to loadarea
    (connected depot48-1-1 loadarea)

    ; crate0 on container-0-0
    (on crate0 container-0-0)
    (crate-at crate0 container0)

    ; clear storeareas (those without a crate on them)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; hoists
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (crate-at crate0 depot48)
    )
  )
)