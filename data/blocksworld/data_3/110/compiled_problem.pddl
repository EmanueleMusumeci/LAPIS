(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
   purple_block_1 - block
 )
 (:init (ontable purple_block_1) (ontable brown_block_1) (on yellow_block_1 brown_block_1) (on purple_block_2 purple_block_1) (on black_block_1 purple_block_2) (clear yellow_block_1) (clear black_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (clear purple_block_1) (hold_0) (hold_2) (hold_3)))
 (:metric minimize (total-cost))
)
