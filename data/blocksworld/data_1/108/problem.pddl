(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   green_block_1 blue_block_1 purple_block_1 orange_block_1 purple_block_2 - block
 )
 (:init (ontable green_block_1) (ontable blue_block_1) (on purple_block_1 green_block_1) (ontable orange_block_1) (on purple_block_2 blue_block_1) (clear purple_block_1) (clear orange_block_1) (clear purple_block_2) (handempty) (= (total-cost) 0))
 (:goal (and (ontable purple_block_1)))
 (:constraints (sometime (or (not (ontable blue_block_1)) (on orange_block_1 purple_block_1))))
 (:metric minimize (total-cost))
)
