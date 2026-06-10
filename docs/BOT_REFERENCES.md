# Bot References

Used as design references, not copied code.

- Mineflayer core: https://github.com/PrismarineJS/mineflayer
- Mineflayer docs/examples: https://prismarinejs.github.io/mineflayer/
- Mineflayer pathfinder: https://github.com/PrismarineJS/mineflayer-pathfinder
- Pathfinder goals guide: https://github.com/PrismarineJS/mineflayer-pathfinder/blob/master/examples/tutorial/goalsExplained.md
- Mineflayer collect block: https://github.com/PrismarineJS/mineflayer-collectblock
- Mineflayer auto eat: https://github.com/linkle69/mineflayer-auto-eat

MVP choices:

- Use pathfinder goals for movement.
- Keep digging/mining/collecting/eating/PVP out of MVP until exploration loop stable.
- Keep autonomy gated by explicit dashboard/API start.
- Train from real replay outcomes: decision cycle + execution result + optional feedback.
