(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48-1-1 depot48-1-2 container-0-0 - storearea
    loadarea - transitarea
    depot48 container0 - place
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in container-0-0 container0)

    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 loadarea)
    (connected container-0-0 loadarea)

    (on crate0 container-0-0)

    (at hoist1 depot48-1-1)
    (at hoist0 depot48-1-2)

    (available hoist0)
    (available hoist1)

    (clear depot48-1-1)
    (clear container-0-0)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)