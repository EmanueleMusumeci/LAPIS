(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
   green_block_1 brown_block_1 - block
 )
 (:init (ontable green_block_1) (on brown_block_1 green_block_1) (on grey_block_1 brown_block_1) (on green_block_2 grey_block_1) (ontable white_block_1) (clear green_block_2) (clear white_block_1) (handempty) (hold_1) (= (total-cost) 0))
 (:goal (and (on white_block_1 brown_block_1) (hold_0) (hold_1) (hold_2)))
 (:metric minimize (total-cost))
)
