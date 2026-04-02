(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    depot48-1-1 depot48-1-2 depot48-1-3 - store_area
    container-0-0 - store_area
    loadarea - transit_area
    hoist0 hoist1 hoist2 - hoist
    crate0 - crate
    container-0-0 - surface
  )

  (:init
    ; Places
    (in depot48-1-1 depot48)
    (in depot48-1-2 depot48)
    (in depot48-1-3 depot48)
    (in container-0-0 container0)

    ; Adjacency within depot48 row
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ; depot48-1-2 connected to loadarea
    (connected depot48-1-2 loadarea)
    (connected loadarea depot48-1-2)

    ; Hoist positions
    (at hoist0 depot48-1-2)
    (at hoist1 depot48-1-3)
    (at hoist2 depot48-1-1)

    ; Hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; Crate on container-0-0
    (on crate0 container-0-0)

    ; Clear storeareas (those without crates or hoists occupying them)
    ; depot48-1-1 has hoist2, depot48-1-2 has hoist0, depot48-1-3 has hoist1
    ; container-0-0 has crate0, so not clear
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)
  )

  (:goal
    (and
      (in_place crate0 depot48)
    )
  )
)