(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 - place
    container0 - place
    loadarea - transit_area
    depot48-1-1 depot48-1-2 depot48-1-3 - store_area
    container-0-0 - store_area
    hoist0 hoist1 hoist2 - hoist
    crate0 - crate
    surface0 - surface
  )

  (:init
    ; Places for depot storeareas
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-1-3 depot48)

    ; Place for container storearea
    (in_place container-0-0 container0)

    ; Adjacency connections among depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Container storearea connected to loadarea
    (connected container-0-0 loadarea)

    ; depot48-1-2 connected to loadarea
    (connected depot48-1-2 loadarea)

    ; Hoist positions
    (at_hoist hoist1 depot48-1-1)
    (at_hoist hoist0 depot48-1-3)
    (at_hoist hoist2 depot48-1-2)

    ; All hoists available
    (available hoist0)
    (available hoist1)
    (available hoist2)

    ; crate0 is on surface0 which is in container-0-0
    (on crate0 surface0)
    (in surface0 container-0-0)

    ; Clear storeareas (those without crates)
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)
  )

  (:goal
    (and
      (in_place depot48-1-1 depot48)
      (on crate0 surface0)
      (in surface0 depot48-1-1)
    )
  )
)