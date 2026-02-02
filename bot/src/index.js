/**
 * Terra Scout Bot - Main Entry Point
 */

require("dotenv").config();
const logger = require("./utils/logger");
const TerraScoutServer = require("./server");

logger.info("========================================");
logger.info("       Terra Scout Bot Starting        ");
logger.info("========================================");

const server = new TerraScoutServer();

// Handle graceful shutdown
process.on("SIGINT", () => {
  logger.warn("Shutting down...");
  server.bot.disconnect();
  process.exit(0);
});

process.on("uncaughtException", (err) => {
  logger.error("Uncaught exception:", err);
});

process.on("unhandledRejection", (reason) => {
  logger.error("Unhandled rejection:", reason);
});

// Start server
server.start().catch((err) => {
  logger.error("Failed to start:", err.message);
  process.exit(1);
});
