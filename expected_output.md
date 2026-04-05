# Expected Output Guide

## What to Expect When Running the DevFix Auto-Agent

### Command:
```bash
python main.py --task "Create a function that adds two numbers and test it"
```

### Expected Output Flow:

1. **Agent Start Message:**
   ```
   Starting DevFix Auto-Agent...
   ```

2. **Planning Phase:**
   - The AI creates a step-by-step plan for your task
   - No direct output, but processes in the background

3. **Code Generation Phase:**
   ```
   Generated code (latest attempt):
   def add(a, b):
       return a + b

   def test_add():
       assert add(1, 2) == 3
       assert add(-1, 1) == 0
   ```

4. **Validation & Testing Phase:**
   ```
   Test output:
   .1 passed in 0.01s
   ```

5. **Success Message:**
   ```
   SUCCESS! All tests passed.

   Final code:
   def add(a, b):
       return a + b

   def test_add():
       assert add(1, 2) == 3
       assert add(-1, 1) == 0
   ```

### Alternative Scenarios:

**If Tests Fail:**
- Shows error message
- Reflects on the issue
- Generates fixed code
- Retries (up to 5 attempts)

**If Max Attempts Reached:**
```
Max attempts reached or tests still failing.
```

## Key Features:
- ✅ **Automatic code generation** based on your task
- ✅ **Built-in testing** with pytest
- ✅ **Self-correction** if tests fail
- ✅ **Clean, tested code** as final output
- ✅ **Docker-isolated execution** for safety