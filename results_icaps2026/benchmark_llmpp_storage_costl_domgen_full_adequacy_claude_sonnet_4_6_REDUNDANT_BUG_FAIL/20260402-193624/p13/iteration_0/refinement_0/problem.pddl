(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48-1-1 depot48-1-2 - store
    container-0-0 - store
    loadarea - transit
    depot48 - place
    container0 - place
    hoist0 hoist1 - hoist
    crate0 - crate
    pallet0 - surface
    pallet1 - surface
    pallet2 - surface
  )

  (:init
    ;; Hoist locations
    (at hoist1 depot48-1-1)
    (at hoist0 depot48-1-2)

    ;; Hoists are available
    (available hoist0)
    (available hoist1)

    ;; Container surface holds crate0
    (on crate0 pallet0)

    ;; Surfaces in stores
    (in pallet0 container-0-0)
    (in pallet1 depot48-1-1)
    (in pallet2 depot48-1-2)

    ;; Surfaces in places
    (in-place pallet0 container0)
    (in-place pallet1 depot48)
    (in-place pallet2 depot48)

    ;; Store clearances
    ;; container-0-0 is NOT clear (crate0 is on pallet0 inside it)
    (clear depot48-1-1)
    (clear depot48-1-2)

    ;; Depot storeareas in depot48
    (in-place depot48-1-1 depot48)
    (in-place depot48-1-2 depot48)

    ;; Container storearea in container0
    (in-place container-0-0 container0)

    ;; Connectivity: adjacent depot storeareas
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)

    ;; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected loadarea container-0-0)

    ;; depot48-1-2 and loadarea are connected
    (connected depot48-1-2 loadarea)
    (connected loadarea depot48-1-2)
  )

  (:goal
    (and
      (in container-0-0 depot48-1-1)
    )
  )
)