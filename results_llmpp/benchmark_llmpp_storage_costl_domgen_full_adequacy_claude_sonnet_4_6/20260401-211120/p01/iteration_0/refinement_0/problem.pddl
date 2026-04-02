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
    ; Places
    (in depot48-1-1 depot48)
    (in container-0-0 container0)

    ; Crate locations
    (on crate0 container-0-0)
    (crate-at crate0 container0)

    ; Hoist (depot48-1-1 is NOT clear because hoist0 occupies it)
    (at hoist0 depot48-1-1)
    (available hoist0)

    ; Connections
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)

    ; Load area predicate
    (is-loadarea loadarea)
  )

  (:goal
    (and
      (crate-at crate0 depot48)
    )
  )
)