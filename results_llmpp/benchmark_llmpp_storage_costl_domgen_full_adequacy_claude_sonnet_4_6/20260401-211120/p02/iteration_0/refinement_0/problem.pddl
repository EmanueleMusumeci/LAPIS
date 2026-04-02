(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 - storearea
    container-0-0 - storearea
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)

    ; Container storeareas in container0
    (in container-0-0 container0)

    ; Adjacency within depot (map: depot48-1-1 depot48-1-2)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-1 and loadarea connected
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)

    ; Crate placement
    (on crate0 container-0-0)

    ; Hoist positions
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)