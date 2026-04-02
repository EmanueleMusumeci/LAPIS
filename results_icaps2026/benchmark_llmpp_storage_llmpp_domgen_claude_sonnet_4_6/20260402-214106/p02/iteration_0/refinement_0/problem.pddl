(define (problem depots-problem)
  (:domain depots)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - place
    depot48-1-1 depot48-1-2 - place
    container-0-0 - pallet
    crate0 - crate
    hoist0 hoist1 - hoist
  )

  (:init
    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Hoist locations
    (at hoist0 depot48-1-1)
    (at hoist1 depot48-1-2)

    ; Pallets in places
    (in container-0-0 container0)

    ; Crate on pallet
    (on crate0 container-0-0)
    (in crate0 container0)

    ; Clear surfaces
    (clear crate0)

    ; Connections between depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-1 and loadarea connected
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
  )

  (:goal
    (and
      (in crate0 depot48)
    )
  )
)