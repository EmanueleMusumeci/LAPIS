(define (problem gripper-4robots-4rooms-8balls)
  (:domain gripper-strips)

  (:objects
    robot1 robot2 robot3 robot4 - robot
    room1 room2 room3 room4 - room
    ball1 ball2 ball3 ball4 ball5 ball6 ball7 ball8 - object
    lgripper1 rgripper1 lgripper2 rgripper2 lgripper3 rgripper3 lgripper4 rgripper4 - gripper
  )

  (:init
    ; Robot locations
    (at-robby robot1 room1)
    (at-robby robot2 room4)
    (at-robby robot3 room3)
    (at-robby robot4 room4)

    ; Ball locations
    (at ball1 room3)
    (at ball2 room3)
    (at ball3 room3)
    (at ball4 room1)
    (at ball5 room4)
    (at ball6 room4)
    (at ball7 room1)
    (at ball8 room1)

    ; Grippers free
    (free robot1 lgripper1)
    (free robot1 rgripper1)
    (free robot2 lgripper2)
    (free robot2 rgripper2)
    (free robot3 lgripper3)
    (free robot3 rgripper3)
    (free robot4 lgripper4)
    (free robot4 rgripper4)
  )

  (:goal
    (and
      (at ball1 room2)
      (at ball2 room3)
      (at ball3 room1)
      (at ball4 room3)
      (at ball5 room1)
      (at ball6 room1)
      (at ball7 room4)
      (at ball8 room2)
    )
  )
)