(define (problem tyreworld-problem)
  (:domain tyreworld)

  (:objects
    jack pump wrench - tool
    boot - container
    hub1 hub2 hub3 hub4 - hub
    nut1 nut2 nut3 nut4 - nut
    flat1 flat2 flat3 flat4 - wheel
    intact1 intact2 intact3 intact4 - wheel
  )

  (:init
    ; Boot state
    (unlocked boot)
    (closed boot)

    ; Tools in boot
    (in jack boot)
    (in pump boot)
    (in wrench boot)

    ; Intact tyres in boot, not inflated
    (in intact1 boot)
    (in intact2 boot)
    (in intact3 boot)
    (in intact4 boot)
    (not-inflated intact1)
    (not-inflated intact2)
    (not-inflated intact3)
    (not-inflated intact4)
    (intact intact1)
    (intact intact2)
    (intact intact3)
    (intact intact4)

    ; Flat tyres on hubs
    (on flat1 hub1)
    (on flat2 hub2)
    (on flat3 hub3)
    (on flat4 hub4)

    ; Hubs on ground
    (on-ground hub1)
    (on-ground hub2)
    (on-ground hub3)
    (on-ground hub4)

    ; Nuts tight on hubs
    (tight nut1 hub1)
    (tight nut2 hub2)
    (tight nut3 hub3)
    (tight nut4 hub4)

    ; Hubs fastened
    (fastened hub1)
    (fastened hub2)
    (fastened hub3)
    (fastened hub4)
  )

  (:goal
    (and
      ; Intact tyres on hubs and inflated
      (on intact1 hub1)
      (on intact2 hub2)
      (on intact3 hub3)
      (on intact4 hub4)
      (inflated intact1)
      (inflated intact2)
      (inflated intact3)
      (inflated intact4)

      ; Nuts tight on hubs
      (tight nut1 hub1)
      (tight nut2 hub2)
      (tight nut3 hub3)
      (tight nut4 hub4)

      ; Flat tyres, wrench, jack, pump in boot
      (in flat1 boot)
      (in flat2 boot)
      (in flat3 boot)
      (in flat4 boot)
      (in wrench boot)
      (in jack boot)
      (in pump boot)

      ; Boot closed
      (closed boot)
    )
  )
)