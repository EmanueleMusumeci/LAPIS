(define (problem gripper-two-robots)
  (:domain gripper-strips)

  (:objects
    robot1 robot2 - robot
    lgripper1 rgripper1 lgripper2 rgripper2 - gripper
    room1 room2 room3 room4 room5 - room
    ball1 ball2 - object
  )

  (:init
    (at-robby robot1 room1)
    (at-robby robot2 room2)
    (at ball1 room1)
    (at ball2 room1)
    (free robot1 lgripper1)
    (free robot1 rgripper1)
    (free robot2 lgripper2)
    (free robot2 rgripper2)
  )

  (:goal
    (and
      (at ball1 room5)
      (at ball2 room4)
    )
  )
)