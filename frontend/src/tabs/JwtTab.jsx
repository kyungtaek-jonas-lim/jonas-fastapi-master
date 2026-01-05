import React, { useState } from 'react';
import useAxios from '../hooks/useAxios';
import { CONTENT_TYPES } from '../utils/contentTypes';  // Import content types

function JwtTab() {
  const [userId, setUserId] = useState('');
  const [generatedToken, setGeneratedToken] = useState('');
  const [verifiedPayload, setVerifiedPayload] = useState('');
  const [verificationToken, setVerificationToken] = useState('');
  const [generateTokenAPIRequestResultMessage, setGenerateTokenAPIRequestResultMessage] = useState('');
  const [verifyTokenAPIRequestResultMessage, setVerifyTokenAPIRequestResultMessage] = useState('');

  const { data, loading, error: axiosError, post } = useAxios();

  // Generate JWT Token
  const generateToken = async () => {
    if (!userId) {
      setGenerateTokenAPIRequestResultMessage("User ID is required.");
      return;
    }

    await post('/v1/jwt/generate-token', { user_id: userId }, CONTENT_TYPES.JSON);
    if (data) {
      setGeneratedToken(data.token);
      setGenerateTokenAPIRequestResultMessage('OK');
    }
  };

  // Verify JWT Token
  const verifyToken = async () => {
    if (!verificationToken) {
      setVerifyTokenAPIRequestResultMessage("Token is required for verification.");
      return;
    }

    await post('/v1/jwt/verify-token', { token: verificationToken }, CONTENT_TYPES.JSON);
    if (data) {
      setVerifiedPayload(JSON.stringify(data.decoded_payload, null, 2));
      setVerifyTokenAPIRequestResultMessage('OK');
    }
  };

  const handleUserIdChange = (e) => {
    setUserId(e.target.value);
  };

  const handleEnterPressGenerateToken = (e) => {
    if (e.key === 'Enter' && userId) {
      generateToken();
    }
  };

  const handleVerificationTokenChange = (e) => {
    setVerificationToken(e.target.value);
  };

  const handleEnterPressVerifyToken = (e) => {
    if (e.key === 'Enter' && verificationToken) {
      verifyToken();
    }
  };

  return (
    <div>
      <h2>JWT Operations</h2>

      <div>
        <h3>Generate Token</h3>
        <input
          type="text"
          placeholder="Enter User ID"
          onChange={handleUserIdChange}
          onKeyDown={handleEnterPressGenerateToken}
          value={userId}
        />
        <button onClick={generateToken} disabled={loading}>
          {loading ? 'Generating...' : 'Generate JWT'}
        </button>
        {generatedToken && (
          <div>
            <h4>Generated Token</h4>
            <textarea readOnly rows="6" value={generatedToken}></textarea>
          </div>
        )}
      </div>
      
      {generateTokenAPIRequestResultMessage ? (
        <p style={{ color: generateTokenAPIRequestResultMessage === 'OK' ? 'green' : 'red' }}>
          {generateTokenAPIRequestResultMessage}
        </p>
      ) : null}

      <div>
        <h3>Verify Token</h3>
        <input
          type="text"
          placeholder="Enter Token"
          onChange={handleVerificationTokenChange}
          onKeyDown={handleEnterPressVerifyToken}
          value={verificationToken}
        />
        <button onClick={verifyToken} disabled={loading}>
          {loading ? 'Verifying...' : 'Verify JWT'}
        </button>
        {verifiedPayload && (
          <div>
            <h4>Decoded Payload</h4>
            <pre>{verifiedPayload}</pre>
          </div>
        )}
      </div>

      {verifyTokenAPIRequestResultMessage ? (
        <p style={{ color: verifyTokenAPIRequestResultMessage === 'OK' ? 'green' : 'red' }}>
          {verifyTokenAPIRequestResultMessage}
        </p>
      ) : null}
      {axiosError && <p style={{ color: 'red' }}>Error: {axiosError}</p>}
    </div>
  );
}

export default JwtTab;
