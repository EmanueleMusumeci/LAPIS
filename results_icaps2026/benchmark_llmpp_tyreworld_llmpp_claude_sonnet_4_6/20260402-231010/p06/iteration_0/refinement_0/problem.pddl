(define (problem tyreworld-problem)
  (:domain tyreworld)

  (:objects
    jack pump wrench - tool
    boot - container
    hub1 hub2 hub3 hub4 hub5 hub6 - hub
    nut1 nut2 nut3 nut4 nut5 nut6 - nut
    flat1 flat2 flat3 flat4 flat5 flat6 - wheel
    intact1 intact2 intact3 intact4 intact5 intact6 - wheel
  )

  (:init
    ; Boot state
    (unlocked boot)
    (closed boot)

    ; Tools and intact tyres are in the boot
    (in jack boot)
    (in pump boot)
    (in wrench boot)
    (in intact1 boot)
    (in intact2 boot)
    (in intact3 boot)
    (in intact4 boot)
    (in intact5 boot)
    (in intact6 boot)

    ; Intact tyres are not inflated but intact
    (not-inflated intact1)
    (not-inflated intact2)
    (not-inflated intact3)
    (not-inflated intact4)
    (not-inflated intact5)
    (not-inflated intact6)
    (intact intact1)
    (intact intact2)
    (intact intact3)
    (intact intact4)
    (intact intact5)
    (intact intact6)

    ; Flat tyres are on the hubs
    (on flat1 hub1)
    (on flat2 hub2)
    (on flat3 hub3)
    (on flat4 hub4)
    (on flat5 hub5)
    (on flat6 hub6)

    ; Hubs are on the ground
    (on-ground hub1)
    (on-ground hub2)
    (on-ground hub3)
    (on-ground hub4)
    (on-ground hub5)
    (on-ground hub6)

    ; Nuts are tight on the hubs
    (tight nut1 hub1)
    (tight nut2 hub2)
    (tight nut3 hub3)
    (tight nut4 hub4)
    (tight nut5 hub5)
    (tight nut6 hub6)

    ; Hubs are fastened
    (fastened hub1)
    (fastened hub2)
    (fastened hub3)
    (fastened hub4)
    (fastened hub5)
    (fastened hub6)
  )

  (:goal
    (and
      ; Intact tyres are on the hubs and inflated
      (on intact1 hub1)
      (on intact2 hub2)
      (on intact3 hub3)
      (on intact4 hub4)
      (on intact5 hub5)
      (on intact6 hub6)
      (inflated intact1)
      (inflated intact2)
      (inflated intact3)
      (inflated intact4)
      (inflated intact5)
      (inflated intact6)

      ; Nuts are tight on the hubs
      (tight nut1 hub1)
      (tight nut2 hub2)
      (tight nut3 hub3)
      (tight nut4 hub4)
      (tight nut5 hub5)
      (tight nut6 hub6)

      ; Flat tyres, wrench, jack, and pump are in the boot
      (in flat1 boot)
      (in flat2 boot)
      (in flat3 boot)
      (in flat4 boot)
      (in flat5 boot)
      (in flat6 boot)
      (in wrench boot)
      (in jack boot)
      (in pump boot)

      ; Boot is closed
      (closed boot)
    )
  )
)