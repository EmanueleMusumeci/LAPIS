(define (problem gripper-problem)
  (:domain gripper-strips)

  (:objects
    room1 room2 room3 - room
    ball1 ball2 ball3 ball4 - object
    robot1 robot2 - robot
    left right - gripper
  )

  (:init
    (at-robby robot1 room2)
    (at-robby robot2 room3)
    (at ball1 room3)
    (at ball2 room1)
    (at ball3 room1)
    (at ball4 room3)
    (free robot1 left)
    (free robot1 right)
    (free robot2 left)
    (free robot2 right)
  )

  (:goal
    (and
      (at ball1 room2)
      (at ball2 room2)
      (at ball3 room3)
      (at ball4 room3)
    )
  )
)