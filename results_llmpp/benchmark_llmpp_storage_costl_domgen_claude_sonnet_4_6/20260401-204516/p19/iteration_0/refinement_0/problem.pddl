(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 - crate
  )

  (:init
    ; Place memberships for depot storeareas
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ; Place memberships for container storeareas
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Adjacency within depot48 (grid connections)
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
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-2)

    ; depot48-2-2 and loadarea connected
    (connected depot48-2-2 loadarea)
    (connected loadarea depot48-2-2)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-1-2)
    (clear depot48-1-3)

    ; Hoist positions
    (at_hoist hoist0 depot48-2-1)
    (at_hoist hoist1 depot48-1-1)

    ; Hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (in container-0-0 depot48)
      (in container-0-1 depot48)
      (in container-0-2 depot48)
      (on crate0 container-0-0)
      (on crate1 container-0-1)
      (on crate2 container-0-2)
    )
  )
)