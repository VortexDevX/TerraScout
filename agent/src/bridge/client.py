"""
Terra Scout Bridge Client
Communicates with the Node.js Mineflayer bot
"""

import asyncio
import json
from typing import Any, Dict, Optional

import httpx
import websockets

from ..utils.logger import get_logger # type: ignore

logger = get_logger(__name__)


class BridgeClient:
    """HTTP client for communicating with Terra Scout bot."""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.base_url = f"http://{host}:{port}"
        self.ws_url = f"ws://{host}:{port}"
        self.client = httpx.Client(timeout=30.0)
        
    def health_check(self) -> bool:
        """Check if bot server is running."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def get_observation(self) -> Optional[Dict[str, Any]]:
        """Get current observation from bot."""
        try:
            response = self.client.get(f"{self.base_url}/observation")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get observation: {e}")
            return None
    
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action and get result."""
        try:
            response = self.client.post(
                f"{self.base_url}/action",
                json=action
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
            return {"error": str(e)}
    
    def reset(self) -> Dict[str, Any]:
        """Reset episode."""
        try:
            response = self.client.post(f"{self.base_url}/reset")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to reset: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status."""
        try:
            response = self.client.get(f"{self.base_url}/status")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"error": str(e)}
    
    def connect(self) -> Dict[str, Any]:
        """Connect bot to Minecraft server."""
        try:
            response = self.client.post(f"{self.base_url}/connect")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return {"error": str(e)}
    
    def disconnect(self) -> Dict[str, Any]:
        """Disconnect bot from Minecraft server."""
        try:
            response = self.client.post(f"{self.base_url}/disconnect")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close the client."""
        self.client.close()


class AsyncBridgeClient:
    """Async WebSocket client for real-time communication."""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.ws_url = f"ws://{host}:{port}"
        self.ws = None
        
    async def connect(self):
        """Connect to WebSocket server."""
        self.ws = await websockets.connect(self.ws_url)
        logger.info("WebSocket connected")
        
    async def send_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Send action and wait for response."""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
            
        await self.ws.send(json.dumps({
            "type": "action",
            "action": action
        }))
        
        response = await self.ws.recv()
        return json.loads(response)
    
    async def reset(self) -> Dict[str, Any]:
        """Reset episode."""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
            
        await self.ws.send(json.dumps({"type": "reset"}))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def get_observation(self) -> Dict[str, Any]:
        """Get current observation."""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
            
        await self.ws.send(json.dumps({"type": "observation"}))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def close(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.ws = None