#!/usr/bin/env python3
"""
Server Startup Script for Smart Tourist Safety & Emergency Response System
Runs the Flask app with Socket.IO support.
"""

from backend.config import Config
from backend.app import app, socketio
from backend.utils.logger import logger

if __name__ == "__main__":
    host = Config.FLASK_HOST
    port = Config.FLASK_PORT
    debug = Config.FLASK_DEBUG
    logger.info(f"Launching Tourist Safety Server on http://{host}:{port} (debug={debug})...")
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
