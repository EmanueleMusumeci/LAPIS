(define (problem tyreworld-problem)
  (:domain tyreworld)

  (:objects
    jack pump wrench - tool
    boot - container
    hub1 - hub
    nut1 - nut
    flat1 - wheel
    intact1 - wheel
  )

  (:init
    ; Boot state
    (unlocked boot)
    (closed boot)

    ; Items in the boot
    (in jack boot)
    (in pump boot)
    (in wrench boot)
    (in intact1 boot)

    ; Intact tyre state
    (not-inflated intact1)
    (intact intact1)

    ; Flat tyre on hub
    (on flat1 hub1)

    ; Hub state
    (on-ground hub1)
    (fastened hub1)

    ; Nut state
    (tight nut1 hub1)
  )

  (:goal
    (and
      ; Intact tyre on hub and inflated
      (on intact1 hub1)
      (inflated intact1)

      ; Nut tight on hub
      (tight nut1 hub1)

      ; Flat tyre, tools in boot
      (in flat1 boot)
      (in wrench boot)
      (in jack boot)
      (in pump boot)

      ; Boot closed
      (closed boot)
    )
  )
)