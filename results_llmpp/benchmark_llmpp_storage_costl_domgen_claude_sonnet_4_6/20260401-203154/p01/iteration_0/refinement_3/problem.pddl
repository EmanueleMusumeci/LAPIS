(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 - crate
  )

  (:init
    (in depot48-1-1 depot48)
    (in container-0-0 container0)
    (clear depot48-1-1)
    (on crate0 container-0-0)
    (in_place crate0 container0)
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
    (at hoist0 depot48-1-1)
    (available hoist0)
  )

  (:goal
    (and
      (in_place crate0 depot48)
    )
  )
)