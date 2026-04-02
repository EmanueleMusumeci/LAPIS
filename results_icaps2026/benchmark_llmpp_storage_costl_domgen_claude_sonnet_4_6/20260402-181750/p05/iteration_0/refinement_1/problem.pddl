(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Crates in container0
    (in_crate crate0 container0)
    (in_crate crate1 container0)

    ; Crates on surfaces
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Clear store areas
    (clear depot48-2-1)
    (clear depot48-2-2)

    ; Hoist positions
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Adjacency in depot48 (grid connections)
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

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)
  )

  (:goal
    (and
      (in_crate crate0 depot48)
      (in_crate crate1 depot48)
    )
  )
)