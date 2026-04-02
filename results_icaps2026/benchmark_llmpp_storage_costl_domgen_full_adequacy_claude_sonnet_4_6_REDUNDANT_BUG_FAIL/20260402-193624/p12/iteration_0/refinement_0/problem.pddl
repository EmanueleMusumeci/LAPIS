(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 container-0-0 - store_area
    loadarea - transit_area
    hoist0 - hoist
    crate0 - crate
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in container-0-0 container0)

    ; Crate locations
    (on crate0 container-0-0)
    (in-place crate0 container0)

    ; Clear areas (depot48-1-1 is NOT clear: hoist0 occupies it)
    ; container-0-0 is NOT clear: crate0 is on it

    ; Hoist
    (hoist-at hoist0 depot48-1-1)
    (available hoist0)

    ; Connections within depot48
    (connected depot48-1-1 loadarea)
    (connected loadarea depot48-1-1)

    ; Container store areas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)
  )

  (:goal
    (and
      (in-place crate0 depot48)
    )
  )
)