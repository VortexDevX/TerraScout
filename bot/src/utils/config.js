/**
 * Terra Scout Bot Configuration
 */

require("dotenv").config();

const config = {
  // Minecraft Server
  minecraft: {
    host: process.env.MC_HOST || "localhost",
    port: parseInt(process.env.MC_PORT) || 25565,
    username: process.env.MC_USERNAME || "TerraScout",
    version: process.env.BOT_VERSION || "1.21.1",
  },

  // API Server
  api: {
    port: parseInt(process.env.API_PORT) || 3000,
    wsPort: parseInt(process.env.WS_PORT) || 3001,
  },

  // Bot Settings
  bot: {
    viewDistance: parseInt(process.env.VIEW_DISTANCE) || 4,
    physicsEnabled: process.env.PHYSICS_ENABLED !== "false",
    autoEat: true,
    autoReconnect: true,
    reconnectDelay: 5000,
  },

  // Observation Settings
  observation: {
    includeInventory: true,
    includeNearbyBlocks: true,
    includeNearbyEntities: true,
    nearbyBlockRadius: 5,
    nearbyEntityRadius: 10,
  },

  // Action Settings
  actions: {
    movementSpeed: 1.0,
    miningTimeout: 10000,
    pathfindingTimeout: 30000,
  },
};

module.exports = config;
