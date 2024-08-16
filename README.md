# Car Reinforcement Learning Game

## Changes done
- Flag introduced for understanding of the destination
- Introduced randomness in the angle decision instead of pure dependence on the model for new areas
- Angle change when stuck at edges to get out of that
	- Introduced randomness in this as well for the same
- Changed the map end calculations - Was incorrect due to the overall area aspect
- Changed the Dqn to have an additional FF layer
- Changed the input to have an angle instead of 2 orientations as another input
- Changed the Reward calculation using 4 parameters
  - locReward: Location Reward - Directly based on car location. Will be from +1 to -1 based on car sand location which is from 0 to 1 where full sand is 1. Weightage of 0.4.
    - Based on if the location is sand vs not this is calculated and is important to ensure car is driving on the designated road
  - dirReward: Is 1 or -1 based on if the distance is increasing or decreasing from the last distance with weightage of 0.4
    - This is important to ensure that car is moving toward the target
  - distReward: Distance Reward - Based on the distance from the destination. Increasing as distance reduces. Weightage of 0.2.
    - This is important to ensure the distance is reducing - though weightage is slightly low as direction is more important
    - TBD: Try with some function of the distance for this like log or something else
  - edgeReward: Is set to -1 when the car is close to the edge with a weightage of 1.0
    - Given one of the highest negative rewards to avoid getting stuck in this position


## Reward thought process
- Reward should increase with the reduction in the distance (function of distance) - Medium weight
	distance divided by the total area of the map is the distance function
- Reward should depend on the direction of movement that can be the difference in between current and last distance and probably even the velocity that would cover the road picked up - Medium weight
- Reward to be dependent on the Sand vs Road aspect as well - Highest weight


## Signal thought process
- Signal should be able to clearly give some direction to where the road is
- Reduced the signal to 2 for end of the road from current 10

## Details of the concepts
- What happens when "boundary-signal" is weak when compared to the last reward?
  - The car get stuck at the boundary and is not able to get out of that location
  - Also it does not move away from the boundary
- What happens when Temperature is reduced?
  - Temperature helps in the model being more creative and being able to explore new routes
  - Introduced this in the code and found this missing in the earlier one
- What is the effect of reducing (gamma)?
  - Based on the formula Gamma helps focus on the future events and not only the current one
  - After Gamma reduction I saw that the model was not able to converge and the car kept moving around the same location
  - Higher Gamma helps to ensure the future rewards are also important and not only the current one for the convergence

## Outputs can be viewed at
- Endless Space map: https://youtu.be/1pkaSCBZoFA
- Car based City map: https://youtu.be/Yel3ZUuFPzo
