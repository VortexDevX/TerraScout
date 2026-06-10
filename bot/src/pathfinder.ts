import pathfinderPackage from 'mineflayer-pathfinder';

const pathfinderApi = pathfinderPackage as typeof pathfinderPackage & {
  pathfinder: typeof import('mineflayer-pathfinder').pathfinder;
  Movements: typeof import('mineflayer-pathfinder').Movements;
  goals: typeof import('mineflayer-pathfinder').goals;
};

export const { pathfinder, Movements, goals } = pathfinderApi;

