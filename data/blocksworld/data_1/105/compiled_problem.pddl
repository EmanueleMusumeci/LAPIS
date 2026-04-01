(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
   brown_block_1 grey_block_1 red_block_1 - block
 )
 (:init (ontable brown_block_1) (on grey_block_1 brown_block_1) (on brown_block_2 grey_block_1) (ontable blue_block_1) (on red_block_1 brown_block_2) (clear blue_block_1) (clear red_block_1) (handempty) (hold_1) (= (total-cost) 0))
 (:goal (and (ontable grey_block_1) (hold_0) (hold_1)))
 (:metric minimize (total-cost))
)
