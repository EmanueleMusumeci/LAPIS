(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 - store_area
    container-0-0 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; Places and store areas
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in container-0-0 container0)

    ; Crate locations
    (on crate0 container-0-0)
    (crate-at-place crate0 container0)

    ; Hoist positions
    (at hoist1 depot48-1-1)
    (at hoist0 depot48-1-2)

    ; Hoist availability
    (available hoist0)
    (available hoist1)

    ; Clearness of store areas
    (clear depot48-1-1)
    ; depot48-1-2 is occupied by hoist0 but not by a crate, so it is clear for crates
    (clear depot48-1-2)

    ; Adjacency within depot48
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-2 and loadarea connected
    (connected depot48-1-2 loadarea)
    (connected loadarea depot48-1-2)
  )

  (:goal
    (and
      (crate-at-place crate0 depot48)
    )
  )
)