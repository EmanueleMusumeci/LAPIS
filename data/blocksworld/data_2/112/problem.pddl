(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   black_block_1 brown_block_1 brown_block_2 orange_block_1 black_block_2 - block
 )
 (:init (ontable black_block_1) (ontable brown_block_1) (on brown_block_2 black_block_1) (ontable orange_block_1) (on black_block_2 orange_block_1) (clear brown_block_1) (clear brown_block_2) (clear black_block_2) (handempty) (= (total-cost) 0))
 (:goal (and (clear orange_block_1)))
 (:constraints (sometime (not (clear black_block_2))) (sometime-before (not (clear black_block_2)) (or (on brown_block_1 brown_block_2) (clear black_block_1))) (sometime (and (holding brown_block_2) (not (clear brown_block_1)))))
 (:metric minimize (total-cost))
)
