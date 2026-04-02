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
    container-0-0-surface - surface
  )

  (:init
    ; Places for depot storeareas
    (in_place depot48-1-1 depot48)
    (in_place depot48-1-2 depot48)
    (in_place depot48-1-3 depot48)

    ; Places for container storeareas
    (in_place container-0-0 container0)

    ; Adjacency connections among depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)

    ; Container storeareas connected to loadarea
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

    ; crate0 is on container-0-0-surface, which is in container-0-0
    (in container-0-0-surface container-0-0)
    (on crate0 container-0-0-surface)
    (crate_in_place crate0 container0)

    ; Clear status: depot storeareas that have hoists are not clear,
    ; depot48-1-1 has hoist1, depot48-1-2 has hoist2, depot48-1-3 has hoist0
    ; container-0-0 has crate0 so not clear
    ; depot storeareas without crates/hoists blocking are clear — none here since all have hoists
    ; Actually, clear refers to store_area being free for dropping crates.
    ; Hoists do not block clear; only crates do.
    ; depot storeareas are clear (no crates)
    (clear depot48-1-1)
    (clear depot48-1-2)
    (clear depot48-1-3)
    ; container-0-0 has crate0 so NOT clear
  )

  (:goal
    (and
      (crate_in_place crate0 depot48)
    )
  )
)