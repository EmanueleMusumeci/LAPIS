(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - storearea
    container-0-0 container-0-1 - storearea
    hoist0 hoist1 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; Hoists locations
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

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

    ; Clear storeareas (only those observed as clear)
    (clear depot48-2-1)
    (clear depot48-2-2)

    ; Adjacency connections in depot48 (grid)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)

    ; depot48-2-1 and loadarea connected (only this one observed)
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)
  )

  (:goal
    (and
      (in depot48-1-1 depot48)
      (on crate0 depot48-2-1)
      (on crate1 depot48-2-2)
    )
  )
)