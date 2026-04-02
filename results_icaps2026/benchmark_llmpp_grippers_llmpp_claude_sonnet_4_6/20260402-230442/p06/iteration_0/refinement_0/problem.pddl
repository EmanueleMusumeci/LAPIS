(define (problem gripper-problem)
  (:domain gripper-strips)

  (:objects
    robot1 robot2 - robot
    left_gripper1 right_gripper1 left_gripper2 right_gripper2 - gripper
    room1 room2 room3 - room
    ball1 - object
  )

  (:init
    (at-robby robot1 room3)
    (at-robby robot2 room2)
    (at ball1 room1)
    (free robot1 left_gripper1)
    (free robot1 right_gripper1)
    (free robot2 left_gripper2)
    (free robot2 right_gripper2)
  )

  (:goal
    (and
      (at ball1 room3)
    )
  )
)