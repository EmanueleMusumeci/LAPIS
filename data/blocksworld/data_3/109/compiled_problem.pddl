(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
 )
 (:init (ontable orange_block_1) (ontable yellow_block_1) (ontable black_block_1) (on black_block_2 black_block_1) (on white_block_1 yellow_block_1) (clear orange_block_1) (clear black_block_2) (clear white_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on white_block_1 orange_block_1) (hold_0) (hold_2) (hold_4)))
 (:metric minimize (total-cost))
)
