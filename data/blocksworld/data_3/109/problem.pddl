(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   orange_block_1 yellow_block_1 black_block_1 black_block_2 white_block_1 - block
 )
 (:init (ontable orange_block_1) (ontable yellow_block_1) (ontable black_block_1) (on black_block_2 black_block_1) (on white_block_1 yellow_block_1) (clear orange_block_1) (clear black_block_2) (clear white_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on white_block_1 orange_block_1)))
 (:constraints (sometime (holding white_block_1)) (sometime-before (holding white_block_1) (clear black_block_1)) (sometime (clear yellow_block_1)) (sometime-before (clear yellow_block_1) (on black_block_1 orange_block_1)) (sometime (not (clear black_block_2))))
 (:metric minimize (total-cost))
)
