(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - store_area
    container-0-0 container-0-1 container-0-2 container-0-3 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 crate1 crate2 crate3 - crate
    container-0-0-surface container-0-1-surface container-0-2-surface container-0-3-surface - surface
  )

  (:init
    ; Hoist location and availability
    (at_hoist hoist0 depot48-1-1)
    (available hoist0)

    ; Crates on surfaces
    (on crate0 container-0-0-surface)
    (on crate1 container-0-1-surface)
    (on crate2 container-0-2-surface)
    (on crate3 container-0-3-surface)

    ; Surfaces in container storeareas
    (in container-0-0-surface container-0-0)
    (in container-0-1-surface container-0-1)
    (in container-0-2-surface container-0-2)
    (in container-0-3-surface container-0-3)

    ; Container storeareas in container0
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)
    (in_place container-0-2 container0)
    (in_place container-0-3 container0)

    ; All depot storeareas in depot48
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-1-3 depot48)
    (in_place depot48-1-4 depot48)
    (in_place depot48-2-1 depot48)
    (in_place depot48-2-2 depot48)
    (in_place depot48-2-3 depot48)
    (in_place depot48-2-4 depot48)

    ; Clear depot storeareas (all except depot48-1-1 where hoist is)
    (clear depot48-1-2)
    (clear depot48-1-3)
    (clear depot48-1-4)
    (clear depot48-2-1)
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-2-4)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected container-0-3 loadarea)

    ; depot48-2-3 connected to loadarea
    (connected depot48-2-3 loadarea)

    ; Adjacent depot storeareas connected (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)

    ; Adjacent depot storeareas connected (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ; Adjacent depot storeareas connected (between rows)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)
  )

  (:goal
    (and
      (in_place depot48-1-1 depot48)
      (in_place depot48-1-2 depot48)
      (in_place depot48-1-3 depot48)
      (in_place depot48-1-4 depot48)
      (in_place depot48-2-1 depot48)
      (in_place depot48-2-2 depot48)
      (in_place depot48-2-3 depot48)
      (in_place depot48-2-4 depot48)
      (on crate0 container-0-0-surface)
      (in container-0-0-surface depot48-1-1)
      (on crate1 container-0-1-surface)
      (in container-0-1-surface depot48-1-2)
      (on crate2 container-0-2-surface)
      (in container-0-2-surface depot48-1-3)
      (on crate3 container-0-3-surface)
      (in container-0-3-surface depot48-1-4)
    )
  )
)