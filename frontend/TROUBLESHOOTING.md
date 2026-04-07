# Troubleshooting WebSocket Connection

## Error: "WebSocket connection failed"

If you see this error in the React application, follow these steps:

### 1. Verify Backend is Running

```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy","debug":false}
```

### 2. Test WebSocket Connection Directly

**Using Python:**
```bash
python /tmp/test_ws.py
# Should print: "✓ WebSocket connection successful!"
```

**Using Browser (HTML test page):**
```bash
# Open in browser:
file:///tmp/test_ws.html
# Click "Test Connection" button
```

### 3. Check Environment Variables

```bash
cd /DATA/lapis/lapis-web/frontend
cat .env
# Should show:
# VITE_API_URL=http://localhost:8001
# VITE_WS_URL=ws://localhost:8001
```

### 4. Verify Frontend is Using Correct URL

Open browser DevTools (F12) and check:

**Console Tab:**
- Look for WebSocket connection attempts
- Check the URL being used (should be `ws://localhost:8001/ws/pipeline`)

**Network Tab:**
- Filter by "WS" (WebSocket)
- Check if connection attempt appears
- Look at the connection URL and status

### 5. Hard Refresh Frontend

The frontend needs to reload environment variables:

```bash
# Stop frontend
pkill -f "vite"

# Restart frontend
cd /DATA/lapis/lapis-web/frontend
npm run dev
```

Then in browser:
- Press **Ctrl+Shift+R** (hard refresh)
- Or clear cache and reload

### 6. Check Browser Console

Open the browser console and look for:

```javascript
// Expected WebSocket URL construction:
// import.meta.env.VITE_WS_URL should be "ws://localhost:8001"
// Final URL: ws://localhost:8001/ws/pipeline

// You can test this in console:
const ws = new WebSocket('ws://localhost:8001/ws/pipeline');
ws.onopen = () => console.log('✓ Connected!');
ws.onerror = (e) => console.error('✗ Error:', e);
ws.onmessage = (e) => console.log('Message:', e.data);
```

### 7. Common Issues

**Issue**: Connection attempts go to `ws://localhost:5173`
- **Cause**: Environment variables not loaded
- **Fix**: Restart frontend dev server, hard refresh browser

**Issue**: Connection timeout
- **Cause**: Backend not running or firewall blocking
- **Fix**: Check backend with `curl http://localhost:8001/health`

**Issue**: CORS error
- **Cause**: Backend CORS configuration
- **Fix**: Check `backend/main.py` CORS origins include `http://localhost:5173`

**Issue**: ERR_CONNECTION_REFUSED
- **Cause**: Backend not running on port 8001
- **Fix**: Start backend with `python -m uvicorn backend.main:app --port 8001`

### 8. Manual WebSocket Test in Browser

If the app still doesn't connect, test manually:

1. Open http://localhost:5173
2. Open DevTools Console (F12)
3. Run:

```javascript
// Test WebSocket directly
const testWS = () => {
  const ws = new WebSocket('ws://localhost:8001/ws/pipeline');

  ws.onopen = () => {
    console.log('%c✓ WebSocket Connected!', 'color: green; font-weight: bold');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('%cReceived:', 'color: blue', data);
  };

  ws.onerror = (error) => {
    console.error('%c✗ WebSocket Error:', 'color: red; font-weight: bold', error);
  };

  ws.onclose = (event) => {
    console.log('%cWebSocket Closed:', 'color: orange', event.code, event.reason);
  };

  return ws;
};

// Run the test
const ws = testWS();
```

### 9. Check usePipeline Hook

The connection is managed by `src/hooks/usePipeline.ts`. Check the console for:
- "Connection status" messages
- Error messages from the hook
- WebSocket state changes

### 10. Verify CORS Headers

Backend should allow WebSocket connections from frontend:

```bash
# Check CORS configuration
grep -A 10 "CORS_ORIGINS" /DATA/lapis/lapis-web/backend/main.py
```

Should include:
```python
CORS_ORIGINS = [
    "http://localhost:5173",      # Vite dev server
    ...
]
```

---

## Still Not Working?

1. **Check both services are running:**
   ```bash
   curl http://localhost:8001/health  # Backend
   curl http://localhost:5173         # Frontend
   ```

2. **Check logs:**
   ```bash
   tail -f /tmp/lapis_backend.log    # Backend logs
   tail -f /tmp/lapis_frontend_new.log  # Frontend logs
   ```

3. **Restart everything:**
   ```bash
   # Stop all
   pkill -f "uvicorn.*backend.main"
   pkill -f "vite"

   # Start backend
   cd /DATA/lapis/lapis-web
   source /DATA/lapis/key.sh
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 > /tmp/lapis_backend.log 2>&1 &

   # Start frontend
   cd /DATA/lapis/lapis-web/frontend
   npm run dev > /tmp/lapis_frontend.log 2>&1 &

   # Wait 5 seconds, then open http://localhost:5173
   ```

4. **Try a different browser:**
   - Chrome/Chromium
   - Firefox
   - Edge

Some browsers have stricter WebSocket policies.
