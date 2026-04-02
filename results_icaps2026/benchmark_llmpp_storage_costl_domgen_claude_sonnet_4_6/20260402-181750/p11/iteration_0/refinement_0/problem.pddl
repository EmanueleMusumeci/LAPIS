(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - store_area
    container-0-0 container-0-1 container-0-2 container-0-3 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 crate3 - crate
    container-0-0-surface container-0-1-surface container-0-2-surface container-0-3-surface - surface
  )

  (:init
    ;; All depot storeareas are in depot48
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-1-3 depot48)
    (in_place depot48-1-4 depot48)
    (in_place depot48-2-1 depot48)
    (in_place depot48-2-2 depot48)
    (in_place depot48-2-3 depot48)
    (in_place depot48-2-4 depot48)

    ;; All container storeareas are in container0
    (in_place container-0-0 container0)
    (in_place container-0-1 container0)
    (in_place container-0-2 container0)
    (in_place container-0-3 container0)

    ;; Surfaces in container storeareas
    (in container-0-0-surface container-0-0)
    (in container-0-1-surface container-0-1)
    (in container-0-2-surface container-0-2)
    (in container-0-3-surface container-0-3)

    ;; Crates on container surfaces
    (on crate0 container-0-0-surface)
    (on crate1 container-0-1-surface)
    (on crate2 container-0-2-surface)
    (on crate3 container-0-3-surface)

    ;; Adjacent depot storeareas connected (horizontal)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ;; Adjacent depot storeareas connected (vertical)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)

    ;; All container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-2)
    (connected container-0-3 loadarea)
    (connected loadarea container-0-3)

    ;; depot48-2-1 and loadarea are connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ;; Clear storeareas
    (clear depot48-1-3)
    (clear depot48-2-3)
    (clear depot48-2-4)
    (clear depot48-2-2)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ;; Hoist locations
    (at_hoist hoist0 depot48-2-1)
    (at_hoist hoist1 depot48-1-4)

    ;; Hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (in_place container-0-0 depot48)
      (in_place container-0-1 depot48)
      (in_place container-0-2 depot48)
      (in_place container-0-3 depot48)
    )
  )
)