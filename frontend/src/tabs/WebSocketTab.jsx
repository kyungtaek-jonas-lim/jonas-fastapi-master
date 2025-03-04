import React, { useState } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import { WEBSOCKET_CONNECTION_STATUS } from '../utils/websocketConnectionStatus';  // Import websocket connection status constants

const WebSocketTab = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [token, setToken] = useState('');
  const { 
    messages, 
    connectionStatus, 
    sendMessage, 
    connectWebSocket, 
    closeWebSocket, 
    cancelReconnect, 
    reconnectEnabled,
    reconnectAttempt
  } = useWebSocket('ws://localhost:8000/v1/websocket/ws', token);

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      sendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const handleTokenChange = (e) => {
    setToken(e.target.value);
  };

  const handleEnterPress = (e) => {
    if (e.key === 'Enter' && token) {
      connectWebSocket();
    }
  };

  return (
    <div>
      <h2>WebSocket Tab</h2>
      <p>Status: <strong>{connectionStatus}</strong></p>

      {connectionStatus === WEBSOCKET_CONNECTION_STATUS.DISCONNECTED || connectionStatus === WEBSOCKET_CONNECTION_STATUS.ERROR ? (
        <div>
          <input
            type="text"
            value={token}
            onChange={handleTokenChange}
            placeholder="Enter JWT token"
            onKeyDown={handleEnterPress}
            disabled={connectionStatus === WEBSOCKET_CONNECTION_STATUS.CONNECTED}
          />
          <button 
            onClick={connectWebSocket} 
            disabled={!token || connectionStatus === WEBSOCKET_CONNECTION_STATUS.CONNECTED}
          >
            Open Connection
          </button>
        </div>
      ) : (
        <div>
          {reconnectEnabled && connectionStatus === WEBSOCKET_CONNECTION_STATUS.RECONNECTING && (
            <button onClick={cancelReconnect}>
              Cancel Retry - {reconnectAttempt}
            </button>
          )}
          <button onClick={closeWebSocket} disabled={connectionStatus !== WEBSOCKET_CONNECTION_STATUS.CONNECTED}>
            Close Connection
          </button>
        </div>
      )}

      <div>
        <h3>Received Messages:</h3>
        <ul style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px' }}>
          {messages.length > 0 ? (
            messages.map((message, index) => <li key={index}>{message}</li>)
          ) : (
            <li></li>
          )}
        </ul>
      </div>

      <div>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message"
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <button onClick={handleSendMessage} disabled={connectionStatus !== WEBSOCKET_CONNECTION_STATUS.CONNECTED}>
          Send
        </button>
      </div>
    </div>
  );
};

export default WebSocketTab;
