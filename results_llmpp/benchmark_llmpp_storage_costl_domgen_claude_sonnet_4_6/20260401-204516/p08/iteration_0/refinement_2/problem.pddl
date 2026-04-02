(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-2-1 depot48-2-2 depot48-2-3 - store_area
    container-0-0 container-0-1 container-0-2 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 - crate
  )

  (:init
    ; All depot storeareas in depot48
    (store_in_place depot48-1-1 depot48)
    (store_in_place depot48-1-2 depot48)
    (store_in_place depot48-1-3 depot48)
    (store_in_place depot48-2-1 depot48)
    (store_in_place depot48-2-2 depot48)
    (store_in_place depot48-2-3 depot48)

    ; All container storeareas in container0
    (store_in_place container-0-0 container0)
    (store_in_place container-0-1 container0)
    (store_in_place container-0-2 container0)

    ; Adjacency within depot48 (horizontal)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)

    ; Adjacency within depot48 (vertical)
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

    ; depot48-2-3 and loadarea connected
    (connected depot48-2-3 loadarea)
    (connected loadarea depot48-2-3)

    ; Crates on container storeareas
    (on crate0 container-0-0)
    (in_store crate0 container-0-0)
    (on crate1 container-0-1)
    (in_store crate1 container-0-1)
    (on crate2 container-0-2)
    (in_store crate2 container-0-2)

    ; Clear storeareas
    (store_clear depot48-2-3)
    (store_clear depot48-2-1)
    (store_clear depot48-1-1)
    (store_clear depot48-1-2)

    ; hoist0 in depot48-2-2
    (hoist_in_store hoist0 depot48-2-2)
    (at_hoist hoist0 depot48-2-2)
    (available hoist0)

    ; hoist1 in depot48-1-3
    (hoist_in_store hoist1 depot48-1-3)
    (at_hoist hoist1 depot48-1-3)
    (available hoist1)
  )

  (:goal
    (and
      (in_store crate0 depot48-2-1)
      (in_store crate1 depot48-1-1)
      (in_store crate2 depot48-1-2)
    )
  )
)