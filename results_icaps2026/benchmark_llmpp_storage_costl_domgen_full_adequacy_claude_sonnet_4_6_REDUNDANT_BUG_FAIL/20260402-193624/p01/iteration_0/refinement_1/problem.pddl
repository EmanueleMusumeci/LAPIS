(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 - storearea
    container-0-0 - storearea
    hoist0 - hoist
    crate0 - crate
  )

  (:init
    (in depot48-1-1 depot48)
    (in container-0-0 container0)
    (on crate0 container-0-0)
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
    (at hoist0 depot48-1-1)
    (available hoist0)
    (clear depot48-1-1)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)