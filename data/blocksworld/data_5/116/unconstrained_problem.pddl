(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   brown_block_1 white_block_1 orange_block_1 red_block_1 blue_block_1 - block
 )
 (:init (ontable brown_block_1) (on white_block_1 brown_block_1) (on orange_block_1 white_block_1) (ontable red_block_1) (on blue_block_1 orange_block_1) (clear red_block_1) (clear blue_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (holding blue_block_1)))
 (:metric minimize (total-cost))
)
