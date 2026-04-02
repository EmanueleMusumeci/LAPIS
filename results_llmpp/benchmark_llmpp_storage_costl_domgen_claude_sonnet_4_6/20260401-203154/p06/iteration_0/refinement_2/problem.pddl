(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
    container-0-0-surface container-0-1-surface - surface
  )

  (:init
    ; Places for depot storeareas
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-2-1 depot48)
    (in_place depot48-2-2 depot48)

    ; Places for container storeareas
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)

    ; Surfaces in container storeareas
    (in container-0-0-surface container-0-0)
    (in container-0-1-surface container-0-1)

    ; Crates on surfaces
    (on crate0 container-0-0-surface)
    (on crate1 container-0-1-surface)

    ; Crates in container0 place
    (crate_in_place crate0 container0)
    (crate_in_place crate1 container0)

    ; Adjacency within depot48 (row/col neighbors)
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
    (at_hoist hoist0 depot48-1-1)
    (at_hoist hoist1 depot48-1-2)
    (at_hoist hoist2 depot48-2-2)

    ; All hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; Clear storeareas
    (clear depot48-2-1)
  )

  (:goal
    (and
      (crate_in_place crate0 depot48)
      (crate_in_place crate1 depot48)
    )
  )
)