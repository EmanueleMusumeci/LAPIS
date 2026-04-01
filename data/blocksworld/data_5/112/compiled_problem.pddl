(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
 )
 (:init (ontable black_block_1) (ontable brown_block_1) (on brown_block_2 black_block_1) (ontable orange_block_1) (on black_block_2 orange_block_1) (clear brown_block_1) (clear brown_block_2) (clear black_block_2) (handempty) (hold_6) (= (total-cost) 0))
 (:goal (and (clear orange_block_1) (hold_0) (hold_2) (hold_3) (hold_5) (hold_6) (hold_7)))
 (:metric minimize (total-cost))
)
