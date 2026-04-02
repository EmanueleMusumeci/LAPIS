(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; All depot storeareas are in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; All container storeareas are in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Adjacency connections for depot storeareas (bidirectional)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)

    ; Container storeareas connected to loadarea (bidirectional)
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)

    ; depot48-2-1 and loadarea connected (bidirectional)
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; Crates on surfaces (container storeareas as surfaces)
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; Occupied container storeareas
    (occupied container-0-0 crate0)
    (occupied container-0-1 crate1)

    ; Clear depot storeareas
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-1)

    ; hoist0 is in depot48-1-2
    (at hoist0 depot48-1-2)

    ; All hoists are available
    (available hoist0)

    ; is-surface for container storeareas (crate sources)
    (is-surface container-0-0)
    (is-surface container-0-1)

    ; is-surface for depot storeareas (crate destinations)
    (is-surface depot48-1-1)
    (is-surface depot48-1-2)
    (is-surface depot48-2-1)
    (is-surface depot48-2-2)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
      (on crate1 depot48-2-1)
    )
  )
)