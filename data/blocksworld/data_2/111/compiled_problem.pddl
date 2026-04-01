(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
   grey_block_1 black_block_1 purple_block_1 - block
 )
 (:init (ontable yellow_block_1) (ontable grey_block_1) (on black_block_1 grey_block_1) (ontable yellow_block_2) (on purple_block_1 yellow_block_2) (clear yellow_block_1) (clear black_block_1) (clear purple_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on grey_block_1 yellow_block_2) (hold_0) (hold_1)))
 (:metric minimize (total-cost))
)
