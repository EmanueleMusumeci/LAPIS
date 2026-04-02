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
    (clear depot48-1-1)
    (connected container-0-0 loadarea)
    (connected depot48-1-1 loadarea)
    (at hoist0 depot48-1-1)
    (available hoist0)
    (placed crate0 container0)
  )

  (:goal
    (and
      (placed crate0 depot48)
    )
  )
)