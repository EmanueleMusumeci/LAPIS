(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - storearea
    container-0-0 container-0-1 container-0-2 - storearea
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 crate2 - crate
    pallet0 pallet1 pallet2 - pallet
  )

  (:init
    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Adjacency in depot48 (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Adjacency in depot48 (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Adjacency in depot48 (between rows)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-2)

    ; depot48-2-2 and loadarea connected
    (connected depot48-2-2 loadarea)
    (connected loadarea depot48-2-2)

    ; Crates on container storeareas
    (on crate0 pallet0)
    (on crate1 pallet1)
    (on crate2 pallet2)

    ; Pallets as surfaces in container storeareas
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)

    ; Crates in container0
    (in-place crate0 container0)
    (in-place crate1 container0)
    (in-place crate2 container0)

    ; Clear depot storeareas
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)

    ; Hoist positions
    (at hoist1 depot48-2-1)
    (at hoist2 depot48-2-2)
    (at hoist0 depot48-2-3)

    ; All hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)
  )

  (:goal
    (and
      (in-place crate0 depot48)
      (in-place crate1 depot48)
      (in-place crate2 depot48)
    )
  )
)