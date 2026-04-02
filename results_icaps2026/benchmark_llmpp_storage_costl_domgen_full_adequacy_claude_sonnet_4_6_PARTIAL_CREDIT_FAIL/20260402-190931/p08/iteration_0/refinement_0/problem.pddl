(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 - crate
    depot48-1-1-surface depot48-1-2-surface depot48-1-3-surface
    depot48-2-1-surface depot48-2-2-surface depot48-2-3-surface
    container-0-0-surface container-0-1-surface container-0-2-surface - surface
  )

  (:init
    ; Places for depot storeareas
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-1-3 depot48)
    (in_place depot48-2-1 depot48)
    (in_place depot48-2-2 depot48)
    (in_place depot48-2-3 depot48)

    ; Places for container storeareas
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)
    (in_place container-0-2 container0)

    ; Surfaces in store areas
    (in depot48-1-1-surface depot48-1-1)
    (in depot48-1-2-surface depot48-1-2)
    (in depot48-1-3-surface depot48-1-3)
    (in depot48-2-1-surface depot48-2-1)
    (in depot48-2-2-surface depot48-2-2)
    (in depot48-2-3-surface depot48-2-3)
    (in container-0-0-surface container-0-0)
    (in container-0-1-surface container-0-1)
    (in container-0-2-surface container-0-2)

    ; Crates on container surfaces
    (on crate0 container-0-0-surface)
    (on crate1 container-0-1-surface)
    (on crate2 container-0-2-surface)

    ; Adjacency connections in depot48 (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Adjacency connections in depot48 (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Adjacency connections between rows
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)

    ; depot48-2-3 connected to loadarea
    (connected depot48-2-3 loadarea)

    ; Clear storeareas
    (clear depot48-2-3)
    (clear depot48-2-1)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Hoist positions
    (at_hoist hoist0 depot48-2-2)
    (at_hoist hoist1 depot48-1-3)

    ; Hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (in_place depot48-1-1 depot48)
      (in_place depot48-1-2 depot48)
      (in_place depot48-1-3 depot48)
      (in_place depot48-2-1 depot48)
      (in_place depot48-2-2 depot48)
      (in_place depot48-2-3 depot48)
      (on crate0 depot48-1-1-surface)
      (on crate1 depot48-1-2-surface)
      (on crate2 depot48-2-1-surface)
    )
  )
)