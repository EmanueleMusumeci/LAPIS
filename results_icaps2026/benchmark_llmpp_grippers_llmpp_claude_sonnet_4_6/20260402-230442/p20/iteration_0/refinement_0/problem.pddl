(define (problem gripper-problem)
  (:domain gripper-strips)

  (:objects
    robot1 robot2 robot3 robot4 - robot
    lgripper1 rgripper1 lgripper2 rgripper2 lgripper3 rgripper3 lgripper4 rgripper4 - gripper
    room1 room2 room3 - room
    ball1 ball2 - object
  )

  (:init
    (at-robby robot1 room1)
    (at-robby robot2 room1)
    (at-robby robot3 room1)
    (at-robby robot4 room1)

    (free robot1 lgripper1)
    (free robot1 rgripper1)
    (free robot2 lgripper2)
    (free robot2 rgripper2)
    (free robot3 lgripper3)
    (free robot3 rgripper3)
    (free robot4 lgripper4)
    (free robot4 rgripper4)

    (at ball1 room2)
    (at ball2 room3)
  )

  (:goal
    (and
      (at ball1 room2)
      (at ball2 room3)
    )
  )
)