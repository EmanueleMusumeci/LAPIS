(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 container-0-0 container-0-1 - storearea
    loadarea - transitarea
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
    container0 depot48 - place
  )

  (:init
    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Clear storeareas
    (clear depot48-1-1)

    ; Adjacency connections within depot48 (grid map)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)

    ; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)

    ; Hoist positions
    (at hoist1 depot48-2-1)
    (at hoist2 depot48-1-2)
    (at hoist0 depot48-2-2)

    ; All hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
      (on crate1 depot48-1-2)
    )
  )
)