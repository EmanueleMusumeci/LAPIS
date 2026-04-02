(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - storearea
    container-0-0 container-0-1 - storearea
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
  )

  (:init
    ; depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; adjacency connections among depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)

    ; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)

    ; crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)

    ; crate locations
    (crate-at crate0 container0)
    (crate-at crate1 container0)

    ; clear storeareas (only depot48-2-1 is clear per observation)
    (clear depot48-2-1)

    ; hoist positions
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)
    (at hoist2 depot48-2-2)

    ; all hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)
  )

  (:goal
    (and
      (crate-at crate0 depot48)
      (crate-at crate1 depot48)
    )
  )
)