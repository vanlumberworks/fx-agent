# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Google AI API key

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/vanlumberworks/vibecode_claude.git
cd vibecode_claude
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- `langgraph` - Agent orchestration framework
- `langchain-google-genai` - Google Gemini integration
- `google-genai` - Google AI SDK
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management
- Other required dependencies

**Note**: Installation may take 2-3 minutes as it downloads all dependencies.

### 4. Get Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

**Important**: Keep your API key secure and never commit it to version control.

### 5. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

Your `.env` file should look like:
```
GOOGLE_AI_API_KEY=your_actual_api_key_here
ACCOUNT_BALANCE=10000.0
MAX_RISK_PER_TRADE=0.02
```

### 6. Verify Installation

Run the basic validation tests:

```bash
python3 test_basic.py
```

You should see:
```
✅ ALL TESTS PASSED
```

## First Run

### Test with EUR/USD

```bash
python3 main.py EUR/USD
```

Expected output:
```
🚀 Initializing Forex Agent System...
✅ Forex Agent System initialized
   Account Balance: $10000.0
   Max Risk Per Trade: 2.0%

============================================================
🔍 ANALYZING: EUR/USD
============================================================

📰 News Agent analyzing EUR/USD...
   Step 1 completed
📊 Technical Agent analyzing EUR/USD...
   Step 2 completed
💰 Fundamental Agent analyzing EUR/USD...
   Step 3 completed
⚖️  Risk Agent calculating parameters...
   Step 4 completed
✅ Risk approved, proceeding to synthesis
🤖 Synthesis Agent making final decision with Google Search...
✅ Final decision: BUY/SELL/WAIT
   Step 5 completed

============================================================
[Decision details...]
============================================================
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'langgraph'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: API Key Error

**Problem**: `ValueError: GOOGLE_AI_API_KEY not found`

**Solution**:
1. Make sure `.env` file exists in the project root
2. Verify the API key is correctly set in `.env`
3. Check that the `.env` file doesn't have extra quotes around the key

### Issue: Import Errors

**Problem**: `ImportError: cannot import name 'ForexAgentState'`

**Solution**:
- Make sure you're in the project root directory
- Verify all files were cloned correctly
- Try running from the project root: `python3 main.py`

### Issue: Google API Errors

**Problem**: `google.api_core.exceptions.PermissionDenied`

**Solution**:
1. Verify your API key is valid
2. Check that Google AI Studio API is enabled
3. Make sure you haven't exceeded your API quota

## Running Examples

After successful installation, try the examples:

```bash
# Run all examples
python3 examples/basic_usage.py

# Or import in Python
python3
>>> from system import ForexAgentSystem
>>> system = ForexAgentSystem()
>>> result = system.analyze("EUR/USD")
```

## Updating

To update the system:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstallation

To remove the system:

```bash
# Deactivate virtual environment (if using)
deactivate

# Remove directory
cd ..
rm -rf vibecode_claude
```

## Next Steps

- Read the [README.md](README.md) for detailed usage
- Check [examples/basic_usage.py](examples/basic_usage.py) for code examples
- Modify agent prompts in [graph/nodes.py](graph/nodes.py)
- Add real data sources to agents in [agents/](agents/)

## Support

If you encounter issues:
1. Check this setup guide
2. Review the [README.md](README.md)
3. Open an issue on GitHub

---

**Happy Trading! 🚀**
