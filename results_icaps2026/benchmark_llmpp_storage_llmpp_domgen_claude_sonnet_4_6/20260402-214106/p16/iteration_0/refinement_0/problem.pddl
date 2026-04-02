(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    hoist0 hoist1 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; Places for depot storeareas
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; Places for container storeareas
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Adjacency connections among depot storeareas (horizontal and vertical)
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

    ; depot48-2-2 connected to loadarea
    (connected depot48-2-2 loadarea)

    ; Crates on container storeareas
    (crate-on crate0 container-0-0)
    (crate-in crate0 container0)
    (crate-on crate1 container-0-1)
    (crate-in crate1 container0)

    ; Clear storeareas
    (clear depot48-2-1)
    (clear depot48-1-2)

    ; Hoist positions
    (hoist-at hoist1 depot48-1-1)
    (hoist-at hoist0 depot48-2-2)

    ; Hoists available
    (hoist-available hoist0)
    (hoist-available hoist1)
  )

  (:goal
    (and
      (crate-in crate0 depot48)
      (crate-in crate1 depot48)
    )
  )
)