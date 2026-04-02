(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 - store_area
    container-0-0 - store_area
    loadarea - transit_area
    hoist0 hoist1 - hoist
    crate0 - crate
  )

  (:init
    ; Places and store areas
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in container-0-0 container0)

    ; Crate locations
    (on crate0 container-0-0)

    ; Clear store areas (depot areas are empty)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ; Hoist positions
    (at_hoist hoist0 depot48-1-1)
    (at_hoist hoist1 depot48-1-2)

    ; Hoists available
    (available hoist0)
    (available hoist1)

    ; Connections between adjacent depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)

    ; depot48-1-1 connected to loadarea
    (connected depot48-1-1 loadarea)
  )

  (:goal
    (and
      (on crate0 depot48-1-1)
    )
  )
)