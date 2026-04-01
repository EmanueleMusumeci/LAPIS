(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
 )
 (:init (ontable black_block_1) (on red_block_1 black_block_1) (ontable white_block_1) (ontable white_block_2) (on black_block_2 white_block_2) (clear red_block_1) (clear white_block_1) (clear black_block_2) (handempty) (= (total-cost) 0))
 (:goal (and (holding white_block_2) (hold_0) (hold_2) (hold_3) (hold_4)))
 (:metric minimize (total-cost))
)
