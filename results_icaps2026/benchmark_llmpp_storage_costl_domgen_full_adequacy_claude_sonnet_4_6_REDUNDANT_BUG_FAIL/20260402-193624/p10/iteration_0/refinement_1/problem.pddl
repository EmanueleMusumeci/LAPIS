(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4 depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - storearea
    container-0-0 container-0-1 container-0-2 container-0-3 - storearea
    hoist0 - hoist
    crate0 crate1 crate2 crate3 - crate
    surface-0-0 surface-0-1 surface-0-2 surface-0-3 - surface
  )

  (:init
    ; Hoist location and availability
    (at hoist0 depot48-1-1)
    (available hoist0)

    ; Crates on surfaces
    (on crate0 surface-0-0)
    (on crate1 surface-0-1)
    (on crate2 surface-0-2)
    (on crate3 surface-0-3)

    ; Surfaces in storeareas
    (in surface-0-0 container-0-0)
    (in surface-0-1 container-0-1)
    (in surface-0-2 container-0-2)
    (in surface-0-3 container-0-3)

    ; Storeareas in places
    (areain depot48-1-1 depot48)
    (areain depot48-1-2 depot48)
    (areain depot48-1-3 depot48)
    (areain depot48-1-4 depot48)
    (areain depot48-2-1 depot48)
    (areain depot48-2-2 depot48)
    (areain depot48-2-3 depot48)
    (areain depot48-2-4 depot48)
    (areain container-0-0 container0)
    (areain container-0-1 container0)
    (areain container-0-2 container0)
    (areain container-0-3 container0)

    ; Crates in places
    (crat-in crate0 container0)
    (crat-in crate1 container0)
    (crat-in crate2 container0)
    (crat-in crate3 container0)

    ; Clear storeareas
    (clear depot48-1-2)
    (clear depot48-1-3)
    (clear depot48-1-4)
    (clear depot48-2-1)
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-2-4)

    ; Adjacency connections among depot storeareas (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)

    ; Adjacency connections among depot storeareas (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ; Adjacency connections between row 1 and row 2
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected container-0-3 loadarea)

    ; depot48-2-3 connected to loadarea
    (connected depot48-2-3 loadarea)
  )

  (:goal
    (and
      (crat-in crate0 depot48)
      (crat-in crate1 depot48)
      (crat-in crate2 depot48)
      (crat-in crate3 depot48)
    )
  )
)