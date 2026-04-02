(define (problem depot-problem)
  (:domain depot)

  (:objects
    depot48 container0 - place
    loadarea - transitarea
    depot48-1-1 depot48-1-2 depot48-1-3 depot48-1-4
    depot48-2-1 depot48-2-2 depot48-2-3 depot48-2-4 - storearea
    container-0-0 container-0-1 container-0-2 container-0-3 - storearea
    hoist0 hoist1 - hoist
    crate0 crate1 crate2 crate3 - crate
    surface0 surface1 surface2 surface3 - surface
  )

  (:init
    ;; All depot storeareas are in depot48
    (in-place depot48-1-1 depot48)
    (in-place depot48-1-2 depot48)
    (in-place depot48-1-3 depot48)
    (in-place depot48-1-4 depot48)
    (in-place depot48-2-1 depot48)
    (in-place depot48-2-2 depot48)
    (in-place depot48-2-3 depot48)
    (in-place depot48-2-4 depot48)

    ;; All container storeareas are in container0
    (in-place container-0-0 container0)
    (in-place container-0-1 container0)
    (in-place container-0-2 container0)
    (in-place container-0-3 container0)

    ;; Surfaces are in container storeareas
    (in surface0 container-0-0)
    (in surface1 container-0-1)
    (in surface2 container-0-2)
    (in surface3 container-0-3)

    ;; Crates on surfaces
    (on crate0 surface0)
    (on crate1 surface1)
    (on crate2 surface2)
    (on crate3 surface3)

    ;; Crates are in container0
    (crate-in-place crate0 container0)
    (crate-in-place crate1 container0)
    (crate-in-place crate2 container0)
    (crate-in-place crate3 container0)

    ;; Container storeareas connected to loadarea
    (connected container-0-0 loadarea)
    (connected container-0-1 loadarea)
    (connected container-0-2 loadarea)
    (connected container-0-3 loadarea)

    ;; depot48-2-1 connected to loadarea
    (connected depot48-2-1 loadarea)

    ;; Adjacent depot storeareas connected (row 1)
    (connected depot48-1-1 depot48-1-2)
    (connected depot48-1-2 depot48-1-1)
    (connected depot48-1-2 depot48-1-3)
    (connected depot48-1-3 depot48-1-2)
    (connected depot48-1-3 depot48-1-4)
    (connected depot48-1-4 depot48-1-3)

    ;; Adjacent depot storeareas connected (row 2)
    (connected depot48-2-1 depot48-2-2)
    (connected depot48-2-2 depot48-2-1)
    (connected depot48-2-2 depot48-2-3)
    (connected depot48-2-3 depot48-2-2)
    (connected depot48-2-3 depot48-2-4)
    (connected depot48-2-4 depot48-2-3)

    ;; Adjacent depot storeareas connected (between rows)
    (connected depot48-1-1 depot48-2-1)
    (connected depot48-2-1 depot48-1-1)
    (connected depot48-1-2 depot48-2-2)
    (connected depot48-2-2 depot48-1-2)
    (connected depot48-1-3 depot48-2-3)
    (connected depot48-2-3 depot48-1-3)
    (connected depot48-1-4 depot48-2-4)
    (connected depot48-2-4 depot48-1-4)

    ;; Hoist positions
    (at hoist0 depot48-2-1)
    (at hoist1 depot48-1-4)

    ;; Hoists available
    (available hoist0)
    (available hoist1)

    ;; Clear storeareas (not occupied by hoist or crate)
    (clear depot48-1-3)
    (clear depot48-2-3)
    (clear depot48-2-4)
    (clear depot48-2-2)
    (clear depot48-1-1)
    (clear depot48-1-2)
  )

  (:goal
    (and
      (crate-in-place crate0 depot48)
      (crate-in-place crate1 depot48)
      (crate-in-place crate2 depot48)
      (crate-in-place crate3 depot48)
    )
  )
)