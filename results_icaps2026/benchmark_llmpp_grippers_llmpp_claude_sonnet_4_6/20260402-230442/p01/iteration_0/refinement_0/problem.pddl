(define (problem gripper-two-robots-two-balls)
  (:domain gripper-strips)

  (:objects
    room1 room2 - room
    ball1 ball2 - object
    robot1 robot2 - robot
    left right - gripper
  )

  (:init
    (at-robby robot1 room1)
    (at-robby robot2 room1)
    (at ball1 room1)
    (at ball2 room1)
    (free robot1 left)
    (free robot1 right)
    (free robot2 left)
    (free robot2 right)
  )

  (:goal
    (and
      (at ball1 room1)
      (at ball2 room1)
    )
  )
)