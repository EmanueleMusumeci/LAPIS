(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   brown_block_1 white_block_1 orange_block_1 red_block_1 blue_block_1 - block
 )
 (:init (ontable brown_block_1) (on white_block_1 brown_block_1) (on orange_block_1 white_block_1) (ontable red_block_1) (on blue_block_1 orange_block_1) (clear red_block_1) (clear blue_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (holding blue_block_1)))
 (:constraints (sometime (not (on blue_block_1 brown_block_1))) (sometime-after (not (on blue_block_1 brown_block_1)) (not (ontable red_block_1))) (sometime (and (on red_block_1 orange_block_1) (ontable white_block_1))) (sometime (not (ontable white_block_1))) (sometime-after (not (ontable white_block_1)) (on brown_block_1 red_block_1)) (sometime (not (on red_block_1 red_block_1))) (sometime-after (not (on red_block_1 red_block_1)) (or (not (clear orange_block_1)) (not (on orange_block_1 white_block_1)))) (sometime (and (not (ontable brown_block_1)) (clear brown_block_1))))
 (:metric minimize (total-cost))
)
