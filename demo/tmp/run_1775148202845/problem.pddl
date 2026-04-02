(define (problem blocks-problem)
  (:domain blocks)
  (:objects b1 b2 b3 - block)
  (:init
    (on b2 b3)
    (on b3 b1)
    (clear b2)
    (empty)
    (num-blocks 3)
  )
  (:goal
    (and
      (goal-on b2 b3)
      (goal-on b3 b1)
    )
  )
)