(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 - store_area
    container-0-0 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 - crate
    container-0-0-surface - surface
  )

  (:init
    ; Places and store areas
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place container-0-0 container0)

    ; Surfaces in store areas
    (in container-0-0-surface container-0-0)

    ; Crate on surface
    (on crate0 container-0-0-surface)
    (crate_in_place crate0 container0)

    ; Clear areas
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Hoists
    (at_hoist hoist0 depot48-1-1)
    (at_hoist hoist1 depot48-1-2)
    (available hoist0)
    (available hoist1)

    ; Connections between adjacent depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storearea connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-1 and loadarea connected
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)
  )

  (:goal
    (and
      (crate_in_place crate0 depot48)
    )
  )
)