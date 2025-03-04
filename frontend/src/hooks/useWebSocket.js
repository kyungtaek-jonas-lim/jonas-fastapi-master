import { useState, useRef, useEffect } from 'react';
import { WEBSOCKET_CONNECTION_STATUS } from '../utils/websocketConnectionStatus';

const useWebSocket = (url, token) => {
  const ws = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState(WEBSOCKET_CONNECTION_STATUS.DISCONNECTED);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [reconnectEnabled, setReconnectEnabled] = useState(true);

  const connectWebSocket = () => {
    if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
      console.log('WebSocket already connected or connecting.');
      return;
    }

    ws.current = new WebSocket(`${url}?token=${token}`);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.CONNECTED);
      setReconnectAttempt(0);
      setReconnectEnabled(true);
      setMessages([]);

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      setMessages((prev) => [...prev, event.data]);
    };

    ws.current.onclose = (event) => {
      console.log('WebSocket closed:', event);
      setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.DISCONNECTED);

      if (reconnectEnabled && event.code !== 1000) {
        
        if (reconnectAttempt < 3) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempt(reconnectAttempt + 1);
          }, 0);
        } else {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempt(0);
          }, 0);
        }
      } else {
        console.log('Reconnect attempts exhausted or normal close.');
        setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.DISCONNECTED);
      }
    };

    ws.current.onerror = (error) => {
      console.log('WebSocket error:', error);
      setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.ERROR);
    };
  };

  const closeWebSocket = () => {
    if (ws.current) {
      ws.current.close(1000, 'User initiated close');
      ws.current = null;
      setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.DISCONNECTED);
      setReconnectAttempt(0);
      setReconnectEnabled(false);

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    }
  };

  const cancelReconnect = () => {
    console.log('Reconnect cancelled.');
    setReconnectAttempt(0);
    setReconnectEnabled(false);
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    ws.current = null;
    setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.DISCONNECTED);
  };

  useEffect(() => {
  
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  
    if (reconnectEnabled) {
      if (reconnectAttempt == 0) {

      } else if (reconnectAttempt <= 3) {
        setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.RECONNECTING);
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`Reconnecting attempt ${reconnectAttempt}...`);
          connectWebSocket();
        }, reconnectAttempt === 1 ? 0 : 2000);
      } else {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log("Max reconnect attempts reached.");
          setConnectionStatus(WEBSOCKET_CONNECTION_STATUS.DISCONNECTED);
          ws.current = null;
          setReconnectAttempt(0);
          setReconnectEnabled(true);
        }, 0);
      }
    } else {
      setReconnectEnabled(true);
    }
  
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [reconnectAttempt]);  

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current= null;
      }
    };
  }, []);

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(message);
    }
  };

  return {
    messages,
    connectionStatus,
    sendMessage,
    connectWebSocket,
    closeWebSocket,
    cancelReconnect,
    reconnectEnabled,
    reconnectAttempt,
  };
};

export default useWebSocket;
