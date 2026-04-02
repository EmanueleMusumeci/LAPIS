(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - depot
    container0 - distributor
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - storearea
    container-0-0-area container-0-1-area container-0-2-area - storearea
    container-0-0 container-0-1 container-0-2 - pallet
    hoist0 - hoist
    crate0 crate1 crate2 - crate
  )

  (:init
    ;; Depot storeareas in depot48
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)

    ;; Container storeareas in container0
    (in container-0-0-area container0)
    (in container-0-1-area container0)
    (in container-0-2-area container0)

    ;; Adjacency in depot48 (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ;; Adjacency in depot48 (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ;; Adjacency between rows
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)

    ;; Container storeareas connected to loadarea
    (connected container-0-0-area loadarea)
    (connected loadarea container-0-0-area)
    (connected container-0-1-area loadarea)
    (connected loadarea container-0-1-area)
    (connected container-0-2-area loadarea)
    (connected loadarea container-0-2-area)

    ;; depot48-2-2 and loadarea connected
    (connected depot48-2-2 loadarea)
    (connected loadarea depot48-2-2)

    ;; Pallets located in container storeareas
    (at container-0-0 container-0-0-area)
    (at container-0-1 container-0-1-area)
    (at container-0-2 container-0-2-area)

    ;; Crates on pallets
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)

    ;; Clear storeareas
    (clear depot48-2-2)
    (clear depot48-2-3)
    (clear depot48-1-3)
    (clear depot48-2-1)
    (clear depot48-1-1)

    ;; Hoist location and availability
    (at hoist0 depot48-1-2)
    (available hoist0)
  )

  (:goal
    (and
      (on crate0 depot48-2-1)
      (on crate1 depot48-2-3)
      (on crate2 depot48-1-3)
    )
  )
)