(define (problem depot48-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - storearea
    container-0-0 container-0-1 - storearea
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 - crate
    pallet0 pallet1 - pallet
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
    (connected-store depot48-1-1 depot48-1-2)
    (connected-store depot48-1-2 depot48-1-1)
    (connected-store depot48-2-1 depot48-2-2)
    (connected-store depot48-2-2 depot48-2-1)
    (connected-store depot48-1-1 depot48-2-1)
    (connected-store depot48-2-1 depot48-1-1)
    (connected-store depot48-1-2 depot48-2-2)
    (connected-store depot48-2-2 depot48-1-2)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)

    ; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)

    ; crates on pallets
    (on crate0 pallet0)
    (on crate1 pallet1)

    ; occupied container storeareas (crates present)
    (occupied container-0-0)
    (occupied container-0-1)

    ; only depot48-2-1 is clear (no hoist, no crate)
    (clear depot48-2-1)

    ; depot storeareas occupied by hoists
    (occupied depot48-1-1)
    (occupied depot48-1-2)
    (occupied depot48-2-2)

    ; hoist locations
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
      (on crate0 crate1)
    )
  )
)