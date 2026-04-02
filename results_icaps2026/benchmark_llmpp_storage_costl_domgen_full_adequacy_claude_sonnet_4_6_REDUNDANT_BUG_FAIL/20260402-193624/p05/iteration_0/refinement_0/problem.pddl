(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-2-1 depot48-2-2 - store_area
    container-0-0 container-0-1 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 - crate
    surface-0-0 surface-0-1 - surface
  )

  (:init
    ; Places for depot storeareas
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-2-1 depot48)
    (in depot48-2-2 depot48)

    ; Places for container storeareas
    (in container-0-0 container0)
    (in container-0-1 container0)

    ; Adjacency within depot48 (grid connections)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected loadarea container-0-0)
    (connected loadarea container-0-1)

    ; depot48-2-1 and loadarea connected
    (connected depot48-2-1 loadarea)
    (connected loadarea depot48-2-1)

    ; Crates on container storeareas (using proper surface objects)
    (on crate0 surface-0-0)
    (on crate1 surface-0-1)

    ; Crates in container0
    (crate_in crate0 container0)
    (crate_in crate1 container0)

    ; Occupied container storeareas
    (occupied container-0-0 crate0)
    (occupied container-0-1 crate1)

    ; Clear depot storeareas
    (clear depot48-2-1)
    (clear depot48-2-2)

    ; Hoists location
    (at_hoist hoist0 depot48-1-1)
    (at_hoist hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Hoists in store
    (hoist_in_store depot48-1-1)
    (hoist_in_store depot48-1-2)
  )

  (:goal
    (and
      (crate_in crate0 depot48)
      (crate_in crate1 depot48)
    )
  )
)