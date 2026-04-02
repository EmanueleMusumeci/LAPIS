(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - store_area
    container-0-0 container-0-1 container-0-2 container-0-3 - store_area
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 crate3 - crate
  )

  (:init
    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-1-4 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)
    (in depot48-2-4 depot48)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)
    (in container-0-3 container0)

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

    ; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)
    (on crate3 container-0-3)

    ; Crates in container0
    (crate_in_place crate0 container0)
    (crate_in_place crate1 container0)
    (crate_in_place crate2 container0)
    (crate_in_place crate3 container0)

    ; Clear storeareas
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-2-4)

    ; Hoists
    (at_hoist hoist0 depot48-2-1)
    (at_hoist hoist1 depot48-1-4)
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (crate_in_place crate0 depot48)
      (crate_in_place crate1 depot48)
      (crate_in_place crate2 depot48)
      (crate_in_place crate3 depot48)
    )
  )
)