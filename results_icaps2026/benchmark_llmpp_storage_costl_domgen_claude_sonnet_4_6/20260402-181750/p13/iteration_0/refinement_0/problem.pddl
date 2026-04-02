(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 - storearea
    container-0-0 - storearea
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; Storearea memberships
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in container-0-0 container0)

    ; Adjacency within depot48
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storearea connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-2 and loadarea connected
    (connected depot48-1-2 loadarea)
    (connected loadarea depot48-1-2)

    ; Crate placement
    (on crate0 container-0-0)
    (crate-at crate0 container0)

    ; Clear storeareas (those without crates)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Hoist positions
    (at hoist1 depot48-1-1)
    (at hoist0 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)
  )

  (:goal
    (and
      (crate-at crate0 depot48)
    )
  )
)