(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - storearea
    container-0-0 container-0-1 container-0-2 - storearea
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 - crate
  )

  (:init
    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Adjacency connections among depot storeareas (bidirectional)
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
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)
    (connected loadarea container-0-2)

    ; depot48-2-2 and loadarea connected
    (connected depot48-2-2 loadarea)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-1-2)
    (clear depot48-1-3)

    ; Hoist locations
    (at hoist0 depot48-2-1)
    (at hoist1 depot48-1-1)

    ; Hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (in container-0-0 depot48)
      (in container-0-1 depot48)
      (in container-0-2 depot48)
    )
  )
)