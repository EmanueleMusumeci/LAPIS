(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4
    container-0-0 container-0-1 container-0-2 container-0-3 - storearea
    hoist0 hoist1 hoist2 - hoist
    crate0 crate1 crate2 crate3 - crate
  )

  (:init
    ; storeareas in places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in depot48-1-4 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)
    (in depot48-2-3 depot48)
    (in depot48-2-4 depot48)
    (in container-0-0 container0)
    (in container-0-1 container0)
    (in container-0-2 container0)
    (in container-0-3 container0)

    ; adjacency within depot48 (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)

    ; adjacency within depot48 (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ; adjacency between rows
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)

    ; container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-1)
    (connected container-0-2 loadarea)
    (connected loadarea container-0-2)
    (connected container-0-3 loadarea)
    (connected loadarea container-0-3)

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; crates on container storeareas
    (on crate0 container-0-0)
    (on crate1 container-0-1)
    (on crate2 container-0-2)
    (on crate3 container-0-3)

    ; crates occupy their storeareas
    (occupies crate0 container-0-0)
    (occupies crate1 container-0-1)
    (occupies crate2 container-0-2)
    (occupies crate3 container-0-3)

    ; clear storeareas
    (clear depot48-2-3)
    (clear depot48-2-4)
    (clear depot48-2-2)
    (clear depot48-1-4)
    (clear depot48-1-1)

    ; hoist locations
    (at hoist0 depot48-2-1)
    (at hoist1 depot48-1-2)
    (at hoist2 depot48-1-3)

    ; all hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)
  )

  (:goal
    (and
      (in depot48-1-1 depot48)
      (on crate0 depot48-1-1)
      (on crate1 depot48-1-4)
      (on crate2 depot48-2-2)
      (on crate3 depot48-2-3)
    )
  )
)