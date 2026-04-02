(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 crate2 - crate
    container-0-0 container-0-1 container-0-2 - surface
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Crates on container store areas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ; Crates in container0
    (in-place crate0 container0)
    (in-place crate1 container0)
    (in-place crate2 container0)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)
    (connected loadarea container-0-2)

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; Adjacent depot storeareas connected (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Adjacent depot storeareas connected (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Adjacent depot storeareas connected (columns)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ; Clear areas
    (clear depot48-2-3)
    (clear depot48-2-2)
    (clear depot48-2-1)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Hoist0 in depot48-1-3
    (at hoist0 depot48-1-3)
    (available hoist0)
  )

  (:goal
    (and
      (in-place crate0 depot48)
      (in-place crate1 depot48)
      (in-place crate2 depot48)
    )
  )
)