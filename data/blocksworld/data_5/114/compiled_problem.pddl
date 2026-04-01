(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
 )
 (:init (ontable yellow_block_1) (ontable brown_block_1) (on blue_block_1 brown_block_1) (on grey_block_1 blue_block_1) (on yellow_block_2 grey_block_1) (clear yellow_block_1) (clear yellow_block_2) (handempty) (hold_4) (= (total-cost) 0))
 (:goal (and (on blue_block_1 yellow_block_2) (hold_0) (hold_1) (hold_3) (hold_4) (hold_5)))
 (:metric minimize (total-cost))
)
