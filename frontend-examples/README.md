# Frontend Integration Examples

Complete collection of frontend integration examples for the Forex Agent System streaming API.

## 📦 What's Included

| File | Description | Framework | Use Case |
|------|-------------|-----------|----------|
| `types.ts` | TypeScript type definitions for all API events | TypeScript | Type safety for any TS project |
| `useForexAnalysis.tsx` | Custom React hook for streaming API | React | Easy integration in React apps |
| `ForexAnalysisComponent.tsx` | Complete React component example | React | Drop-in component |
| `demo.html` | Standalone HTML/JS/CSS demo | Vanilla JS | No build tools needed |
| `FRONTEND_INTEGRATION_GUIDE.md` | Complete integration guide | - | Step-by-step tutorials |

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Terminal 1: From project root
cd /path/to/vibecode_claude
python backend/server.py
```

Server runs at `http://localhost:8000`

### 2. Try the Demo

**Option A: Open directly** (easiest)
```bash
open demo.html
```

**Option B: Serve with Python**
```bash
cd frontend-examples
python -m http.server 8080
# Visit: http://localhost:8080/demo.html
```

**Option C: Serve with Node**
```bash
npx serve .
# Visit the URL shown
```

## 📚 Integration Guides

### TypeScript Projects

1. Copy `types.ts` to your project:
```bash
cp types.ts src/types/forex-api.ts
```

2. Import and use:
```typescript
import type { AnalysisResult, Decision } from './types/forex-api';
```

See [type definitions](./types.ts) for all available types.

### React Applications

**Option 1: Use the custom hook** (recommended)

```bash
# Copy files
cp useForexAnalysis.tsx src/hooks/
cp types.ts src/types/
```

```tsx
import { useForexAnalysis } from './hooks/useForexAnalysis';

function MyComponent() {
  const { analyze, state, isAnalyzing } = useForexAnalysis();

  return (
    <button onClick={() => analyze('EUR/USD')}>
      Analyze
    </button>
  );
}
```

**Option 2: Use the complete component**

```bash
cp ForexAnalysisComponent.tsx src/components/
```

```tsx
import ForexAnalysisComponent from './components/ForexAnalysisComponent';

function App() {
  return <ForexAnalysisComponent />;
}
```

### Vue.js Applications

See [FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md#vuejs-integration) for Composition API and Options API examples.

### Vanilla JavaScript

Use `demo.html` as a reference or copy the EventSource code:

```javascript
const url = `http://localhost:8000/analyze/stream?query=EUR/USD`;
const eventSource = new EventSource(url);

eventSource.addEventListener('decision', (event) => {
  const data = JSON.parse(event.data);
  console.log('Decision:', data.decision.action);
});
```

## 📖 Documentation

### Event Types

The API emits 7 event types:

1. **start** - Analysis initiated
2. **query_parsed** - Query parsed into context
3. **agent_update** - Agent completed (news, technical, fundamental)
4. **risk_update** - Risk assessment result
5. **decision** - Final trading decision
6. **complete** - Full analysis result
7. **error** - Error occurred

### Example Event Flow

```
start
  ↓
query_parsed (pair: "EUR/USD")
  ↓
agent_update (agent: "news")
agent_update (agent: "technical")
agent_update (agent: "fundamental")
  ↓
risk_update (approved: true)
  ↓
decision (action: "BUY", confidence: 0.75)
  ↓
complete (full result)
```

## 🎯 Use Cases

### Real-Time Trading Dashboard

```tsx
import { useForexAnalysis } from './hooks/useForexAnalysis';

function TradingDashboard() {
  const { analyze, state } = useForexAnalysis();

  return (
    <div>
      {/* Query context */}
      {state.queryContext && (
        <div>Analyzing: {state.queryContext.pair}</div>
      )}

      {/* Agent progress */}
      <div>
        Agents: {state.progress.agentsCompleted}/{state.progress.totalAgents}
      </div>

      {/* Decision */}
      {state.decision && (
        <TradeDecision decision={state.decision} />
      )}
    </div>
  );
}
```

### Multi-Pair Analyzer

```tsx
function MultiPairAnalyzer() {
  const pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY'];
  const [results, setResults] = useState({});

  const analyzeAll = async () => {
    for (const pair of pairs) {
      const result = await analyzeNonStreaming(pair);
      setResults(prev => ({ ...prev, [pair]: result }));
    }
  };

  return (
    <div>
      <button onClick={analyzeAll}>Analyze All</button>
      {pairs.map(pair => (
        <PairCard key={pair} pair={pair} result={results[pair]} />
      ))}
    </div>
  );
}
```

### Alert System

```tsx
function AlertSystem() {
  const { analyze, state } = useForexAnalysis({
    onComplete: (result) => {
      if (result.decision.action === 'BUY' && result.decision.confidence > 0.8) {
        sendNotification(`Strong BUY signal for ${result.pair}!`);
      }
    }
  });

  return <div>Monitoring...</div>;
}
```

## 🔧 Configuration

### Custom API URL

```tsx
const { analyze } = useForexAnalysis({
  apiUrl: 'https://api.yourdomain.com'
});
```

### Callbacks

```tsx
const { analyze } = useForexAnalysis({
  onStart: () => console.log('Started'),
  onComplete: (result) => console.log('Complete:', result),
  onError: (error) => console.error('Error:', error)
});
```

### Auto-Reconnect

```tsx
const { analyze } = useForexAnalysis({
  autoReconnect: true,
  maxReconnectAttempts: 3
});
```

## 🐛 Troubleshooting

### Server Not Running

```bash
# Terminal 1: Start server
cd /path/to/vibecode_claude
python backend/server.py

# Terminal 2: Test
curl http://localhost:8000/health
```

### CORS Issues

The server allows all origins in development. For production, update `backend/server.py`:

```python
allow_origins=["https://yourdomain.com"]
```

### No Events Received

1. Open browser console (F12)
2. Check for errors
3. Verify EventSource connection:
```javascript
eventSource.addEventListener('open', () => console.log('Connected!'));
```

### Type Errors

Make sure to import types correctly:

```typescript
// ✓ Correct
import type { Decision } from './types/forex-api';

// ✗ Incorrect
import { Decision } from './types/forex-api'; // Not a value export
```

## 📱 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile Safari
- ✅ Mobile Chrome
- ⚠️ IE 11 (requires polyfill)

For IE 11 support:
```html
<script src="https://cdn.jsdelivr.net/npm/event-source-polyfill@1.0.25/src/eventsource.min.js"></script>
```

## 🎨 Styling Tips

The React component includes inline styles using `<style jsx>`. For production:

1. **Extract to CSS modules:**
```tsx
import styles from './ForexAnalysis.module.css';
<div className={styles.container}>
```

2. **Use Tailwind:**
```tsx
<div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
```

3. **Use styled-components:**
```tsx
const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;
```

## 🚀 Performance Tips

1. **Debounce queries:**
```tsx
const debouncedAnalyze = useMemo(
  () => debounce(analyze, 300),
  [analyze]
);
```

2. **Memoize event handlers:**
```tsx
const handleComplete = useCallback((result) => {
  // Handle completion
}, []);
```

3. **Clean up connections:**
```tsx
useEffect(() => {
  return () => eventSource?.close();
}, [eventSource]);
```

## 📦 Production Checklist

- [ ] Update API URL for production
- [ ] Configure CORS for your domain
- [ ] Add error tracking (Sentry, etc.)
- [ ] Implement authentication if needed
- [ ] Add loading states
- [ ] Handle network errors
- [ ] Test on all target browsers
- [ ] Optimize bundle size
- [ ] Add analytics
- [ ] Use environment variables

## 📚 Additional Resources

- [Full API Documentation](../docs/STREAMING_API.md)
- [Frontend Integration Guide](./FRONTEND_INTEGRATION_GUIDE.md)
- [Main Project README](../README.md)
- [EventSource API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

## 💡 Examples

### Simple Analysis

```typescript
import { useForexAnalysis } from './hooks/useForexAnalysis';

function SimpleAnalysis() {
  const { analyze, state } = useForexAnalysis();

  return (
    <div>
      <button onClick={() => analyze('EUR/USD')}>
        Analyze EUR/USD
      </button>
      {state.decision && (
        <div>Decision: {state.decision.action}</div>
      )}
    </div>
  );
}
```

### With Progress

```typescript
function WithProgress() {
  const { analyze, state, isAnalyzing } = useForexAnalysis();

  return (
    <div>
      {isAnalyzing && (
        <div>
          Stage: {state.progress.stage}
          <br />
          Agents: {state.progress.agentsCompleted}/{state.progress.totalAgents}
        </div>
      )}
    </div>
  );
}
```

### With Error Handling

```typescript
function WithErrorHandling() {
  const { analyze, error } = useForexAnalysis({
    onError: (error) => {
      console.error('Analysis failed:', error);
    }
  });

  return (
    <div>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
```

## 🤝 Contributing

Found a bug or want to add an example?

1. Check existing examples
2. Follow the code style
3. Add TypeScript types
4. Test thoroughly
5. Update documentation

## 📄 License

Same as the main project (MIT).

---

**Need Help?** See the [Integration Guide](./FRONTEND_INTEGRATION_GUIDE.md) for detailed tutorials.
