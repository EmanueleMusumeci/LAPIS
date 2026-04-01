(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   black_block_1 red_block_1 white_block_1 white_block_2 black_block_2 - block
 )
 (:init (ontable black_block_1) (on red_block_1 black_block_1) (ontable white_block_1) (ontable white_block_2) (on black_block_2 white_block_2) (clear red_block_1) (clear white_block_1) (clear black_block_2) (handempty) (= (total-cost) 0))
 (:goal (and (holding white_block_2)))
 (:constraints (sometime (ontable black_block_2)) (sometime-before (ontable black_block_2) (or (not (ontable white_block_2)) (not (clear red_block_1)))) (sometime (not (clear red_block_1))))
 (:metric minimize (total-cost))
)
