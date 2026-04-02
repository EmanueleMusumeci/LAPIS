(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 - storearea
    container-0-0 - storearea
    hoist0 hoist1 hoist2 - hoist
    crate0 - crate
  )

  (:init
    ; depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)

    ; container storeareas in container0
    (in container-0-0 container0)

    ; adjacency connections among depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)

    ; depot48-1-2 connected to loadarea
    (connected depot48-1-2 loadarea)

    ; hoist positions
    (at hoist1 depot48-1-1)
    (at hoist0 depot48-1-3)
    (at hoist2 depot48-1-2)

    ; all hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; crate0 on container-0-0
    (on crate0 container-0-0)

    ; clear status: storeareas occupied by a hoist are NOT clear
    ; depot48-1-1 has hoist1 -> not clear
    ; depot48-1-2 has hoist2 -> not clear
    ; depot48-1-3 has hoist0 -> not clear
    ; container-0-0 has crate0 -> not clear
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)