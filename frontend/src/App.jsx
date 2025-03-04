import React, { useState } from 'react';
// import FileTab from './tabs/FileTab';
import WebSocketTab from './tabs/WebSocketTab';
// import JwtTab from './tabs/JwtTab';
// import AsyncTab from './tabs/AsyncTab';
// import CryptographyTab from './tabs/CryptographyTab';
// import RedisTab from './tabs/RedisTab';

function App() {
  const [activeTab, setActiveTab] = useState("websocket");

  const renderTab = () => {
    switch (activeTab) {
      case "file":
        return <FileTab />;
      case "websocket":
        return <WebSocketTab />;
      case "jwt":
        return <JwtTab />;
      case "async":
        return <AsyncTab />;
      case "cryptography":
        return <CryptographyTab />;
      case "redis":
        return <RedisTab />;
      default:
        return <FileTab />;
    }
  };

  return (
    <div>
      <div className="tabs">
        {/* <button onClick={() => setActiveTab("file")}>File</button> */}
        <button onClick={() => setActiveTab("websocket")}>WebSocket</button>
        {/* <button onClick={() => setActiveTab("jwt")}>JWT</button>
        <button onClick={() => setActiveTab("async")}>Async</button>
        <button onClick={() => setActiveTab("cryptography")}>Cryptography</button>
        <button onClick={() => setActiveTab("redis")}>Redis</button> */}
      </div>
      <div className="tab-content">
        {renderTab()}
      </div>
    </div>
  );
}

export default App;
