# Frontend Integration Guide

Complete guide for integrating the Forex Agent System streaming API into your frontend application.

## Table of Contents

- [Quick Start](#quick-start)
- [TypeScript Integration](#typescript-integration)
- [React Integration](#react-integration)
- [Vanilla JavaScript](#vanilla-javascript)
- [Vue.js Integration](#vuejs-integration)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Start the API Server

```bash
# Terminal 1: Start the backend
cd /path/to/vibecode_claude
python backend/server.py
```

The server will run at `http://localhost:8000`

### 2. Test with the Demo

Open `demo.html` in your browser:

```bash
# Option 1: Open directly
open frontend-examples/demo.html

# Option 2: Serve with Python
python -m http.server 8080
# Then visit: http://localhost:8080/frontend-examples/demo.html
```

## TypeScript Integration

### 1. Copy Type Definitions

Copy `types.ts` to your project:

```bash
cp frontend-examples/types.ts src/types/forex-api.ts
```

### 2. Use in Your Code

```typescript
import type {
  AnalysisResult,
  Decision,
  QueryContext,
  StreamEvent,
  DecisionEventData
} from './types/forex-api';

// Type-safe event handling
const handleDecision = (event: MessageEvent) => {
  const data: DecisionEventData = JSON.parse(event.data);
  console.log(`Action: ${data.decision.action}`);
  console.log(`Confidence: ${data.decision.confidence}`);
};
```

## React Integration

### Option 1: Use the Custom Hook (Recommended)

1. **Copy the hook to your project:**

```bash
cp frontend-examples/useForexAnalysis.tsx src/hooks/
cp frontend-examples/types.ts src/types/
```

2. **Use in your component:**

```tsx
import { useForexAnalysis } from './hooks/useForexAnalysis';

function TradingDashboard() {
  const { analyze, state, isAnalyzing, error } = useForexAnalysis({
    apiUrl: 'http://localhost:8000',
    onComplete: (result) => {
      console.log('Analysis complete:', result);
    }
  });

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={() => analyze(query)} disabled={isAnalyzing}>
        {isAnalyzing ? 'Analyzing...' : 'Analyze'}
      </button>

      {state.decision && (
        <div>
          <h2>{state.decision.action}</h2>
          <p>Confidence: {state.decision.confidence * 100}%</p>
        </div>
      )}
    </div>
  );
}
```

### Option 2: Use Complete Component

Copy the full component:

```bash
cp frontend-examples/ForexAnalysisComponent.tsx src/components/
```

Then import and use:

```tsx
import ForexAnalysisComponent from './components/ForexAnalysisComponent';

function App() {
  return <ForexAnalysisComponent />;
}
```

### Option 3: Build Your Own

```tsx
import { useState, useEffect } from 'react';

function MyAnalysis() {
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const [decision, setDecision] = useState(null);

  const startAnalysis = (query: string) => {
    const url = `http://localhost:8000/analyze/stream?query=${encodeURIComponent(query)}`;
    const es = new EventSource(url);

    es.addEventListener('decision', (event) => {
      const data = JSON.parse(event.data);
      setDecision(data.decision);
    });

    es.addEventListener('complete', () => {
      es.close();
    });

    setEventSource(es);
  };

  useEffect(() => {
    return () => {
      eventSource?.close();
    };
  }, [eventSource]);

  return (
    <div>
      <button onClick={() => startAnalysis('EUR/USD')}>
        Analyze EUR/USD
      </button>
      {decision && <div>Action: {decision.action}</div>}
    </div>
  );
}
```

## Vanilla JavaScript

### Basic Example

```html
<!DOCTYPE html>
<html>
<body>
  <input type="text" id="query" placeholder="Enter query">
  <button onclick="analyze()">Analyze</button>
  <div id="result"></div>

  <script>
    function analyze() {
      const query = document.getElementById('query').value;
      const url = `http://localhost:8000/analyze/stream?query=${encodeURIComponent(query)}`;
      const eventSource = new EventSource(url);

      eventSource.addEventListener('decision', (event) => {
        const data = JSON.parse(event.data);
        document.getElementById('result').innerHTML =
          `<h2>${data.decision.action}</h2>
           <p>Confidence: ${(data.decision.confidence * 100).toFixed(0)}%</p>`;
      });

      eventSource.addEventListener('complete', () => {
        eventSource.close();
      });

      eventSource.addEventListener('error', (event) => {
        console.error('Error:', event);
        eventSource.close();
      });
    }
  </script>
</body>
</html>
```

### Full-Featured Demo

Use the included `demo.html` as a reference for a complete implementation with:
- Progress tracking
- Agent status updates
- Error handling
- Styling

## Vue.js Integration

### Composition API

```vue
<template>
  <div>
    <input v-model="query" placeholder="Enter query" />
    <button @click="analyze" :disabled="isAnalyzing">
      {{ isAnalyzing ? 'Analyzing...' : 'Analyze' }}
    </button>

    <div v-if="decision">
      <h2>{{ decision.action }}</h2>
      <p>Confidence: {{ (decision.confidence * 100).toFixed(0) }}%</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';

const query = ref('');
const isAnalyzing = ref(false);
const decision = ref(null);
let eventSource = null;

const analyze = () => {
  if (!query.value.trim()) return;

  isAnalyzing.value = true;
  decision.value = null;

  const url = `http://localhost:8000/analyze/stream?query=${encodeURIComponent(query.value)}`;
  eventSource = new EventSource(url);

  eventSource.addEventListener('decision', (event) => {
    const data = JSON.parse(event.data);
    decision.value = data.decision;
  });

  eventSource.addEventListener('complete', () => {
    isAnalyzing.value = false;
    eventSource.close();
  });

  eventSource.addEventListener('error', () => {
    isAnalyzing.value = false;
    eventSource?.close();
  });
};

onUnmounted(() => {
  eventSource?.close();
});
</script>
```

### Options API

```vue
<script>
export default {
  data() {
    return {
      query: '',
      isAnalyzing: false,
      decision: null,
      eventSource: null
    };
  },
  methods: {
    analyze() {
      this.isAnalyzing = true;
      this.decision = null;

      const url = `http://localhost:8000/analyze/stream?query=${encodeURIComponent(this.query)}`;
      this.eventSource = new EventSource(url);

      this.eventSource.addEventListener('decision', (event) => {
        const data = JSON.parse(event.data);
        this.decision = data.decision;
      });

      this.eventSource.addEventListener('complete', () => {
        this.isAnalyzing = false;
        this.eventSource.close();
      });
    }
  },
  beforeUnmount() {
    this.eventSource?.close();
  }
};
</script>
```

## Error Handling

### Connection Errors

```javascript
eventSource.onerror = (error) => {
  console.error('Connection error:', error);

  // Check if server is running
  fetch('http://localhost:8000/health')
    .then(res => res.json())
    .then(data => console.log('Server is healthy:', data))
    .catch(() => {
      alert('Server is not running. Please start it with: python backend/server.py');
    });

  eventSource.close();
};
```

### Automatic Reconnection

```javascript
let reconnectAttempts = 0;
const maxReconnects = 3;

function connectWithRetry(query) {
  const url = `http://localhost:8000/analyze/stream?query=${encodeURIComponent(query)}`;
  const eventSource = new EventSource(url);

  eventSource.onerror = () => {
    eventSource.close();

    if (reconnectAttempts < maxReconnects) {
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);

      console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempts})`);
      setTimeout(() => connectWithRetry(query), delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  };

  eventSource.addEventListener('complete', () => {
    reconnectAttempts = 0; // Reset on success
    eventSource.close();
  });

  return eventSource;
}
```

### Event-Level Error Handling

```javascript
eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);

  // Handle different error types
  if (data.error_type === 'ValueError') {
    alert('Invalid input. Please check your query.');
  } else if (data.error_type === 'ConnectionError') {
    alert('Could not connect to external services.');
  } else {
    alert(`Error: ${data.error}`);
  }

  eventSource.close();
});
```

## Best Practices

### 1. Always Close Connections

```javascript
// React
useEffect(() => {
  return () => {
    eventSource?.close();
  };
}, [eventSource]);

// Vue
onUnmounted(() => {
  eventSource?.close();
});

// Vanilla JS
window.addEventListener('beforeunload', () => {
  eventSource?.close();
});
```

### 2. Handle All Event Types

Listen to all 7 event types for the best UX:

```javascript
const events = [
  'start',
  'query_parsed',
  'agent_update',
  'risk_update',
  'decision',
  'complete',
  'error'
];

events.forEach(eventType => {
  eventSource.addEventListener(eventType, (event) => {
    const data = JSON.parse(event.data);
    console.log(`[${eventType}]:`, data);
  });
});
```

### 3. Provide Progress Feedback

```javascript
const stages = {
  'start': 'Starting analysis...',
  'query_parsed': 'Parsing query...',
  'agent_update': 'Running agents...',
  'risk_update': 'Assessing risk...',
  'decision': 'Making decision...',
  'complete': 'Complete!'
};

eventSource.addEventListener('agent_update', (event) => {
  const data = JSON.parse(event.data);
  updateProgress(`${data.agent} agent completed`);
});
```

### 4. Use TypeScript

TypeScript provides type safety and autocomplete:

```typescript
import type { DecisionEventData } from './types';

eventSource.addEventListener('decision', (event) => {
  const data: DecisionEventData = JSON.parse(event.data);
  // TypeScript knows the exact shape of data.decision
  console.log(data.decision.action); // ✓ Type-safe
});
```

### 5. Validate API Availability

```javascript
async function checkAPI() {
  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();

    if (data.status !== 'healthy') {
      throw new Error('API is unhealthy');
    }

    if (!data.api_configured) {
      throw new Error('API key not configured');
    }

    return true;
  } catch (error) {
    console.error('API check failed:', error);
    return false;
  }
}

// Before starting analysis
if (await checkAPI()) {
  startAnalysis();
} else {
  alert('Please start the API server first');
}
```

## Troubleshooting

### CORS Errors

If you see CORS errors:

1. **Development:** The server allows all origins by default
2. **Production:** Update `backend/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### EventSource Not Connecting

1. Check if server is running:
```bash
curl http://localhost:8000/health
```

2. Check browser console for errors

3. Verify URL is correct:
```javascript
console.log(url); // Should be http://localhost:8000/analyze/stream?query=...
```

### No Events Received

1. Check server logs for errors
2. Verify event listeners are registered before connection
3. Test with cURL:
```bash
curl -N "http://localhost:8000/analyze/stream?query=EUR/USD"
```

### Browser Compatibility

EventSource is supported in all modern browsers. For older browsers, use a polyfill:

```html
<script src="https://cdn.jsdelivr.net/npm/event-source-polyfill@1.0.25/src/eventsource.min.js"></script>
```

## Production Checklist

- [ ] Update CORS to specific domain
- [ ] Add authentication if needed
- [ ] Implement rate limiting
- [ ] Add error tracking (Sentry, etc.)
- [ ] Use HTTPS
- [ ] Add loading skeletons/placeholders
- [ ] Implement retry logic
- [ ] Add analytics
- [ ] Test on all target browsers
- [ ] Optimize for mobile

## Additional Resources

- [Full API Documentation](../docs/STREAMING_API.md)
- [TypeScript Types](./types.ts)
- [React Hook](./useForexAnalysis.tsx)
- [React Component](./ForexAnalysisComponent.tsx)
- [Live Demo](./demo.html)
- [EventSource MDN](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)

## Support

For issues or questions:
- Check the [main README](../README.md)
- Review [STREAMING_API.md](../docs/STREAMING_API.md)
- Check browser console for errors
- Verify API server is running
