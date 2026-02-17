# Frontend Documentation - Student Loan NELFUND Chatbot

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Key Components Explained](#key-components-explained)
5. [How It Works](#how-it-works)
6. [Setup and Installation](#setup-and-installation)
7. [State Management](#state-management)
8. [Styling and UI](#styling-and-ui)
9. [API Integration](#api-integration)

---

## Overview

This frontend is a **React-based chat interface** built with:
- **React 19**: Modern UI library for building interactive interfaces
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Radix UI**: Accessible component primitives (ScrollArea, Separator, etc.)
- **Lucide React**: Icon library

The application provides a clean, modern chat interface where users can ask questions about NELFUND student loans and receive AI-powered answers with source citations.

---

## Architecture

```
User Interaction → React Components → API Calls → Backend → Response → UI Update
```

### High-Level Flow:
1. User types a question in the chat input
2. React sends HTTP POST request to backend API
3. Backend processes query and returns answer + sources
4. React updates the UI to show the new message
5. User sees answer with clickable source citations

---

## Project Structure

```
frontend/
├── index.html              # HTML entry point
├── src/
│   ├── main.jsx           # React app entry point
│   ├── index.css          # Global styles and Tailwind imports
│   └── app/
│       ├── App.jsx        # ⭐ MAIN: Main application component
│       ├── ErrorBoundary.jsx  # Error handling wrapper
│       └── components/
│           ├── ChatMessage.jsx      # Displays individual messages
│           ├── ChatInput.jsx        # Input field for typing messages
│           ├── LoadingIndicator.jsx # Shows loading animation
│           ├── ErrorMessage.jsx     # Displays error messages
│           └── ui/                  # Reusable UI components
│               ├── button.jsx
│               ├── card.jsx
│               ├── textarea.jsx
│               ├── scroll-area.jsx
│               ├── badge.jsx
│               ├── alert.jsx
│               ├── separator.jsx
│               └── utils.jsx        # Utility functions
├── package.json            # Dependencies and scripts
├── vite.config.js         # Vite configuration
└── README.md              # This file
```

---

## Key Components Explained

### 1. `src/main.jsx` - Application Entry Point

**Purpose**: This is where React starts rendering your application.

**Code Breakdown**:
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './app/App.jsx'
import { ErrorBoundary } from './app/ErrorBoundary.jsx'
import './index.css'

// Find the root element in index.html
const rootElement = document.getElementById('root');

// Create React root and render the app
const root = createRoot(rootElement);

root.render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);
```

**What it does**:
- **StrictMode**: React development tool that helps find potential problems
- **ErrorBoundary**: Catches any errors in the app and shows a fallback UI
- **createRoot**: Modern React way to render the app (React 18+)
- **App**: The main component that contains all your chat interface

**Why it matters**: This is the starting point. Without this, nothing would render.

---

### 2. `src/app/App.jsx` - Main Application Component ⭐ **MOST IMPORTANT**

**Purpose**: The heart of the application. Manages all state, handles API calls, and renders the chat interface.

**Key Features**:
- Manages message history (state)
- Handles sending messages to backend
- Manages loading and error states
- Auto-scrolls to new messages
- Session management

**Code Breakdown**:

#### State Management
```jsx
const [messages, setMessages] = useState(initialMessages);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);
const [sessionId, setSessionId] = useState(null);
```

**What each state does**:
- **messages**: Array of all chat messages (user + assistant)
- **isLoading**: Boolean - true when waiting for API response
- **error**: String - error message if API call fails
- **sessionId**: Unique ID for this chat session (for future conversation history)

#### Initial Messages
```jsx
const initialMessages = [
  {
    id: "1",
    role: "assistant",
    content: "Welcome to the Student Loan information portal...",
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
];
```
**What it does**: Sets up a welcome message when the app first loads.

#### Auto-Scroll Effect
```jsx
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages, isLoading]);
```
**What it does**: Automatically scrolls to the bottom when new messages arrive or loading state changes.

**Why it matters**: Users always see the latest message without manually scrolling.

#### Session Initialization
```jsx
useEffect(() => {
  const initializeSession = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
      }
    } catch (err) {
      console.error("Failed to initialize session:", err);
    }
  };
  initializeSession();
}, []);
```
**What it does**: 
- Runs once when component mounts (empty dependency array `[]`)
- Creates a new session ID from the backend
- Stores it for future use (conversation history, etc.)

#### Sending Messages
```jsx
const handleSendMessage = async (content) => {
  // 1. Clear any existing errors
  setError(null);

  // 2. Add user message to the chat immediately
  const userMessage = {
    id: Date.now().toString(),
    role: "user",
    content,
    timestamp: new Date(),
  };
  setMessages((prev) => [...prev, userMessage]);

  // 3. Show loading indicator
  setIsLoading(true);

  try {
    // 4. Call backend API
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message: content,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    // 5. Parse response
    const data = await response.json();

    // 6. Create assistant message from response
    const assistantMessage = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: data.answer || data.response || "No response received",
      citations: data.citations || data.sources || [],
      timestamp: new Date(),
    };

    // 7. Add assistant message to chat
    setMessages((prev) => [...prev, assistantMessage]);
  } catch (err) {
    // 8. Handle errors
    setError("Failed to get a response. Please try again.");
    console.error("Error sending message:", err);
  } finally {
    // 9. Hide loading indicator
    setIsLoading(false);
  }
};
```

**Step-by-step flow**:
1. User types and submits a message
2. User message appears immediately in chat
3. Loading indicator shows
4. HTTP POST request sent to backend
5. Backend processes and returns answer
6. Assistant message appears with answer and citations
7. Loading indicator hides

**Why it matters**: This is the core functionality - without this, the chat wouldn't work.

#### Clearing Chat
```jsx
const handleClearChat = () => {
  setMessages([initialMessages[0]]);  // Reset to just welcome message
  setError(null);
  // Delete session on backend
  if (sessionId) {
    fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
      method: "DELETE",
    }).catch(console.error);
    setSessionId(null);
  }
};
```

#### Retry Function
```jsx
const handleRetry = () => {
  setError(null);
  // Find last user message and resend it
  const lastUserMessage = [...messages].reverse().find(m => m.role === "user");
  if (lastUserMessage) {
    handleSendMessage(lastUserMessage.content);
  }
};
```

#### UI Structure
```jsx
return (
  <div className="w-full h-full flex flex-col">
    {/* Header with title and clear button */}
    <Card className="border-b">
      <div className="flex items-center justify-between p-4">
        <div>AI Assistant</div>
        <Button onClick={handleClearChat}>Clear Chat</Button>
      </div>
    </Card>

    {/* Messages area with scroll */}
    <div className="flex-1 overflow-hidden">
      <ScrollArea className="h-full">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isLoading && <LoadingIndicator />}
        {error && <ErrorMessage message={error} onRetry={handleRetry} />}
      </ScrollArea>
    </div>

    {/* Input area at bottom */}
    <div className="border-t">
      <ChatInput 
        onSendMessage={handleSendMessage} 
        disabled={isLoading}
      />
    </div>
  </div>
);
```

**Layout Structure**:
- **Header**: Fixed at top with title and clear button
- **Messages**: Scrollable area in the middle
- **Input**: Fixed at bottom

---

### 3. `src/app/components/ChatMessage.jsx` - Message Display

**Purpose**: Renders individual chat messages (both user and assistant).

**Key Features**:
- Different styling for user vs. assistant messages
- Displays citations/sources
- Shows timestamps
- Icons for user and bot

**Code Breakdown**:

#### Message Type Detection
```jsx
const isUser = message.role === "user";
```

#### Message Layout
```jsx
<div className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
  {/* Bot icon (only for assistant) */}
  {!isUser && (
    <div className="w-8 h-8 rounded-full bg-primary/10">
      <Bot className="w-5 h-5" />
    </div>
  )}
  
  {/* Message content */}
  <Card className={isUser ? "bg-primary text-primary-foreground" : "bg-card"}>
    <p className="whitespace-pre-wrap">{message.content}</p>
  </Card>
  
  {/* User icon (only for user) */}
  {isUser && (
    <div className="w-8 h-8 rounded-full bg-primary">
      <CircleUser className="w-5 h-5" />
    </div>
  )}
</div>
```

**What it does**:
- User messages: Right-aligned, primary color background
- Assistant messages: Left-aligned, card background
- Icons on opposite sides

#### Citations Display
```jsx
{message.citations && message.citations.length > 0 && (
  <div className="flex flex-col gap-2">
    <p className="text-sm text-muted-foreground">Sources:</p>
    {message.citations.map((citation, index) => (
      <Card key={index} className="p-3">
        <a href={citation.url} target="_blank">
          <Badge>{index + 1}</Badge>
          <p>{citation.title}</p>
          <ExternalLink className="w-3 h-3" />
        </a>
      </Card>
    ))}
  </div>
)}
```

**What it does**: Shows clickable source links below assistant messages.

**Note**: The current implementation expects citations with `url` and `title`, but the backend currently returns source file names. This can be enhanced to show file names or convert them to links.

---

### 4. `src/app/components/ChatInput.jsx` - Input Field

**Purpose**: Text input area where users type their questions.

**Key Features**:
- Multi-line textarea (grows as needed)
- Enter to send (Shift+Enter for new line)
- Send button
- Disabled state during loading

**Code Breakdown**:

#### State
```jsx
const [message, setMessage] = useState("");
```
Stores the current input text.

#### Form Submission
```jsx
const handleSubmit = (e) => {
  e.preventDefault();  // Prevent page refresh
  if (message.trim() && !disabled) {
    onSendMessage(message.trim());  // Call parent's send function
    setMessage("");  // Clear input
  }
};
```

#### Keyboard Handling
```jsx
const handleKeyDown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSubmit(e);  // Send on Enter
  }
  // Shift+Enter creates new line (default behavior)
};
```

**What it does**:
- **Enter**: Sends message
- **Shift+Enter**: New line
- **Disabled**: Prevents sending while loading

#### UI
```jsx
<form onSubmit={handleSubmit} className="flex gap-2 items-end">
  <Textarea
    value={message}
    onChange={(e) => setMessage(e.target.value)}
    onKeyDown={handleKeyDown}
    placeholder="Ask me anything..."
    disabled={disabled}
    className="min-h-[60px] max-h-[200px] resize-none"
    rows={2}
  />
  <Button 
    type="submit" 
    disabled={disabled || !message.trim()}
  >
    <Send className="w-5 h-5" />
  </Button>
</form>
```

---

### 5. `src/app/components/LoadingIndicator.jsx` - Loading Animation

**Purpose**: Shows a visual indicator while waiting for the API response.

**Code**:
```jsx
export function LoadingIndicator() {
  return (
    <div className="flex gap-4 justify-start">
      <div className="w-8 h-8 rounded-full bg-primary/10">
        <Loader className="w-5 h-5 text-primary animate-spin" />
      </div>
      <div className="bg-card p-4 rounded-lg">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" 
               style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" 
               style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" 
               style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
}
```

**What it does**: Shows a spinning loader icon and animated dots to indicate the system is processing.

---

### 6. `src/app/components/ErrorMessage.jsx` - Error Display

**Purpose**: Displays error messages with a retry option.

**Code**:
```jsx
export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex gap-4 justify-start">
      <div className="w-8 h-8 rounded-full bg-destructive/10">
        <CircleAlert className="w-5 h-5 text-destructive" />
      </div>
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
        {onRetry && (
          <Button variant="outline" onClick={onRetry}>
            Retry
          </Button>
        )}
      </Alert>
    </div>
  );
}
```

**What it does**: Shows error message in a red alert box with a retry button.

---

### 7. `src/app/ErrorBoundary.jsx` - Error Handling

**Purpose**: Catches React errors and prevents the entire app from crashing.

**Code**:
```jsx
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h1>Something went wrong</h1>
          <p>{this.state.error?.toString()}</p>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**What it does**:
- Catches any JavaScript errors in child components
- Shows a fallback UI instead of a blank screen
- Provides a reload button

**Why it matters**: Prevents the entire app from breaking if one component has an error.

---

### 8. UI Components (`src/app/components/ui/`)

These are reusable, styled components built with Tailwind CSS and Radix UI.

#### `button.jsx`
- Variants: default, destructive, outline, secondary, ghost, link
- Sizes: default, sm, lg, icon
- Uses `class-variance-authority` for variant management

#### `card.jsx`
- Card container with header, title, description, content, footer
- Consistent styling across the app

#### `utils.jsx`
```jsx
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
```
**Purpose**: Utility function to merge Tailwind classes intelligently, handling conflicts.

**Example**:
```jsx
cn("px-4", "px-2")  // Returns "px-2" (last one wins)
```

---

## How It Works (Step-by-Step Example)

**User asks**: "What are the eligibility requirements?"

### Step 1: User Types and Submits
```
User types in ChatInput → Presses Enter or clicks Send
```

### Step 2: Input Component Handles Submit
```jsx
// ChatInput.jsx
handleSubmit() → onSendMessage("What are the eligibility requirements?")
```

### Step 3: App Component Processes
```jsx
// App.jsx
handleSendMessage("What are the eligibility requirements?")
  → setMessages([...prev, userMessage])  // User message appears
  → setIsLoading(true)  // Loading indicator shows
```

### Step 4: API Call
```jsx
fetch("http://localhost:8000/api/chat", {
  method: "POST",
  body: JSON.stringify({
    session_id: sessionId,
    message: "What are the eligibility requirements?"
  })
})
```

### Step 5: Backend Response
```json
{
  "answer": "Based on the NELFUND documents, eligibility requirements include...",
  "sources": ["NELFUND_Eligibility_Detailed.txt"],
  "citations": ["NELFUND_Eligibility_Detailed.txt"]
}
```

### Step 6: Update UI
```jsx
// App.jsx
const assistantMessage = {
  id: "...",
  role: "assistant",
  content: data.answer,
  citations: data.citations,
  timestamp: new Date()
};
setMessages([...prev, assistantMessage])  // Assistant message appears
setIsLoading(false)  // Loading indicator hides
```

### Step 7: Auto-Scroll
```jsx
// useEffect triggers
messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
// Page scrolls to show new message
```

### Step 8: User Sees Result
- User message on the right (blue)
- Assistant message on the left (white card)
- Sources listed below assistant message
- Timestamp shown

---

## Setup and Installation

### Prerequisites
- Node.js 18+ and npm
- Backend server running (see backend README)

### Installation Steps

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure API URL** (Optional)
Create a `.env` file in the `frontend/` directory:
```
VITE_API_BASE_URL=http://localhost:8000
```
If not set, defaults to `http://localhost:8000`.

3. **Start Development Server**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

4. **Build for Production**
```bash
npm run build
```
Creates optimized production build in `dist/` folder.

---

## State Management

This app uses **React's built-in state management** (useState hooks). No external state management library is needed for this simple chat interface.

### State Flow
```
User Action
    ↓
Event Handler (handleSendMessage)
    ↓
State Update (setMessages, setIsLoading)
    ↓
Component Re-render
    ↓
UI Update
```

### State Locations
- **App.jsx**: Main state (messages, loading, error, sessionId)
- **ChatInput.jsx**: Local state (message text)
- **Other components**: Mostly presentational (receive props, no state)

---

## Styling and UI

### Tailwind CSS
The app uses **Tailwind CSS** for styling - a utility-first CSS framework.

**Example**:
```jsx
<div className="flex items-center gap-4 p-4 bg-card rounded-lg">
```
- `flex`: display: flex
- `items-center`: align-items: center
- `gap-4`: gap: 1rem
- `p-4`: padding: 1rem
- `bg-card`: background color from theme
- `rounded-lg`: border-radius: 0.5rem

### Design System
Colors and themes are defined in `src/index.css` using CSS variables:
- `--primary`: Main brand color
- `--background`: Page background
- `--card`: Card background
- `--muted-foreground`: Secondary text color
- etc.

### Responsive Design
The layout is responsive and works on:
- Desktop (full width, centered content)
- Tablet (adjusted spacing)
- Mobile (stacked layout)

---

## API Integration

### API Base URL
```jsx
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
```

### Endpoints Used

#### 1. Create Session
```jsx
POST /api/sessions
Response: { session_id: "uuid" }
```

#### 2. Send Message
```jsx
POST /api/chat
Request: { session_id: "...", message: "..." }
Response: { answer: "...", sources: [...], citations: [...] }
```

#### 3. Delete Session
```jsx
DELETE /api/sessions/{session_id}
Response: { message: "Session deleted", session_id: "..." }
```

### Error Handling
- Network errors: Shows error message with retry button
- API errors: Displays error from backend
- Timeout: Could be added (not currently implemented)

---

## Key React Concepts Used

### Hooks

#### `useState`
```jsx
const [messages, setMessages] = useState(initialMessages);
```
Manages component state.

#### `useEffect`
```jsx
useEffect(() => {
  // Run on mount
  initializeSession();
}, []);  // Empty array = run once

useEffect(() => {
  // Run when messages change
  scrollToBottom();
}, [messages]);  // Dependencies
```
Handles side effects (API calls, DOM updates).

#### `useRef`
```jsx
const messagesEndRef = useRef(null);
// Later: messagesEndRef.current?.scrollIntoView()
```
References DOM elements without causing re-renders.

### Component Patterns

#### Presentational Components
Components that only display data (ChatMessage, LoadingIndicator).

#### Container Components
Components that manage state and logic (App.jsx).

#### Controlled Components
Input components controlled by React state (ChatInput).

---

## Troubleshooting

### "Failed to get a response"
- **Cause**: Backend not running or wrong URL
- **Fix**: Check backend is running on port 8000, verify `VITE_API_BASE_URL`

### "CORS error"
- **Cause**: Backend CORS not configured for frontend origin
- **Fix**: Add frontend URL to backend's allowed origins in `main.py`

### Messages not scrolling
- **Cause**: ScrollArea or ref issue
- **Fix**: Check `messagesEndRef` is properly attached

### Styling looks broken
- **Cause**: Tailwind not processing or CSS not loaded
- **Fix**: Restart dev server, check `index.css` is imported

---

## Summary

This frontend is a **modern React chat interface** that:
1. Provides a clean, user-friendly chat UI
2. Manages message state and API communication
3. Displays answers with source citations
4. Handles loading and error states gracefully
5. Auto-scrolls to keep conversation in view

The architecture is simple and maintainable, using React's built-in features without unnecessary complexity. It's designed to be easily extensible for features like:
- Conversation history
- Message editing
- Dark mode toggle
- File uploads
- Voice input

---

## Additional Notes

- The app uses **React 19** (latest version)
- **Vite** provides fast hot module replacement (HMR) during development
- **Radix UI** components are accessible (ARIA compliant)
- The UI is responsive and works on all screen sizes
- Error boundaries prevent the entire app from crashing
- Session management is set up for future conversation history features
