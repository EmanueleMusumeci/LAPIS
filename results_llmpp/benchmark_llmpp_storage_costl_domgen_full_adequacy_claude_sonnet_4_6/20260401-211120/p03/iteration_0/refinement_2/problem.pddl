(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 - store_area
    container-0-0 - store_area
    loadarea - transit_area
    hoist0 hoist1 hoist2 - hoist
    crate0 - crate
  )

  (:init
    ; Places
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-1-3 depot48)
    (in_place container-0-0 container0)

    ; Adjacency within depot48 (row: 1-1 <-> 1-2 <-> 1-3)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-2 and loadarea connected
    (connected depot48-1-2 loadarea)
    (connected loadarea depot48-1-2)

    ; Hoists
    (at_hoist hoist0 depot48-1-2)
    (at_hoist hoist2 depot48-1-1)
    (at_hoist hoist1 depot48-1-3)
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; Crates
    (on crate0 container-0-0)
    (in_store crate0 container-0-0)
  )

  (:goal
    (and
      (in_store crate0 depot48-1-1)
    )
  )
)