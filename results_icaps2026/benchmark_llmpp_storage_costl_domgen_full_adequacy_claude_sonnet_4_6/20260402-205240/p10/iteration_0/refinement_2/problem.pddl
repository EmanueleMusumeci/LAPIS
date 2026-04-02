(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - storearea
    container-0-0 container-0-1 container-0-2 container-0-3 - storearea
    hoist0 - hoist
    crate0 crate1 crate2 crate3 - crate
    pallet0 pallet1 pallet2 pallet3 - pallet
  )

  (:init
    ; Hoists available
    (available hoist0)

    ; Hoist location
    (at hoist0 depot48-1-1)

    ; Pallets at container storeareas
    (at pallet0 container-0-0)
    (at pallet1 container-0-1)
    (at pallet2 container-0-2)
    (at pallet3 container-0-3)

    ; Crates on pallets
    (on crate0 pallet0)
    (on crate1 pallet1)
    (on crate2 pallet2)
    (on crate3 pallet3)

    ; Crates at container storeareas
    (at crate0 container-0-0)
    (at crate1 container-0-1)
    (at crate2 container-0-2)
    (at crate3 container-0-3)

    ; Container storeareas in container0
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)
    (in container-0-3 container0)

    ; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-1-4 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)
    (in depot48-2-4 depot48)

    ; Clear depot storeareas (depot48-1-1 is occupied by hoist0, not listed as clear)
    (clear depot48-1-2)
    (clear depot48-1-3)
    (clear depot48-1-4)
    (clear depot48-2-1)
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-2-4)

    ; Adjacency within depot48 (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)

    ; Adjacency within depot48 (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ; Adjacency between rows
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected container-0-3 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)
    (connected loadarea container-0-2)
    (connected loadarea container-0-3)

    ; depot48-2-3 and loadarea connected
    (connected depot48-2-3 loadarea)
    (connected loadarea depot48-2-3)
  )

  (:goal
    (and
      (at crate0 depot48-1-2)
      (at crate1 depot48-1-3)
      (at crate2 depot48-1-4)
      (at crate3 depot48-2-1)
    )
  )
)