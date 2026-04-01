(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   green_block_1 brown_block_1 grey_block_1 green_block_2 white_block_1 - block
 )
 (:init (ontable green_block_1) (on brown_block_1 green_block_1) (on grey_block_1 brown_block_1) (on green_block_2 grey_block_1) (ontable white_block_1) (clear green_block_2) (clear white_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on white_block_1 brown_block_1)))
 (:constraints (sometime (on grey_block_1 white_block_1)) (sometime (ontable white_block_1)) (sometime-after (ontable white_block_1) (or (on white_block_1 green_block_2) (not (clear green_block_2)))) (sometime (not (ontable white_block_1))) (sometime-before (not (ontable white_block_1)) (holding brown_block_1)))
 (:metric minimize (total-cost))
)
