(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - storearea
    loadarea - transitarea
    hoist0 - hoist
    crate0 - crate
  )

  (:init
    (in depot48-1-1 depot48)
    (in container-0-0 container0)

    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    (on crate0 container-0-0)

    (at hoist0 depot48-1-1)
    (available hoist0)

    (in container-0-0 container0)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)