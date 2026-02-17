import { useState, useRef, useEffect } from "react";
import { BotMessageSquare, Trash2 } from "lucide-react";
import { ChatMessage } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";
import { LoadingIndicator } from "./components/LoadingIndicator";
import { ErrorMessage } from "./components/ErrorMessage";
import { Button } from "./components/ui/button";
import { Card } from "./components/ui/card";
import { ScrollArea } from "./components/ui/scroll-area";

// API base URL - adjust this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Mock data for demonstration
const initialMessages = [
  {
    id: "1",
    role: "assistant",
    content: "Welcome to the Student Loan information portal. I use the latest NELFUND documents to provide accurate, cited answers regarding your financing options. What information are you looking for?",
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
];

export default function App() {
  const [messages, setMessages] = useState(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Initialize session on component mount
  useEffect(() => {
    const initializeSession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/sessions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
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

  const handleSendMessage = async (content) => {
    // Clear any existing errors
    setError(null);

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: content,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Create assistant message from API response
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || data.response || "No response received",
        citations: data.citations || data.sources || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError("Failed to get a response. Please try again.");
      console.error("Error sending message:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([initialMessages[0]]);
    setError(null);
    // Optionally reset session
    if (sessionId) {
      fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
        method: "DELETE",
      }).catch(console.error);
      setSessionId(null);
    }
  };

  const handleRetry = () => {
    setError(null);
    // Get the last user message and resend it
    const lastUserMessage = [...messages].reverse().find(m => m.role === "user");
    if (lastUserMessage) {
      handleSendMessage(lastUserMessage.content);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-background" style={{ minHeight: '100vh' }}>
      {/* Header */}
      <Card className="border-b rounded-none shadow-sm">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <BotMessageSquare className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold">AI Assistant</h1>
              <p className="text-sm text-muted-foreground">
                Always here to help
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearChat}
            disabled={messages.length <= 1}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear Chat
          </Button>
        </div>
      </Card>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="max-w-4xl mx-auto p-6 space-y-6">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            
            {isLoading && <LoadingIndicator />}
            
            {error && (
              <ErrorMessage 
                message={error} 
                onRetry={handleRetry}
              />
            )}

            {messages.length === 1 && !isLoading && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <BotMessageSquare className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-xl mb-2">Start a conversation</h2>
                <p className="text-muted-foreground max-w-md">
                  Ask me anything you want to understand about student loan policies, application status, and repayment plans, complete with source citations. 
                </p>
              </div>
            )}

            {/* Invisible element for auto-scrolling */}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="border-t bg-card">
        <div className="max-w-4xl mx-auto p-4">
          <ChatInput 
            onSendMessage={handleSendMessage} 
            disabled={isLoading}
            placeholder="Ask me anything..."
          />
          <p className="text-xs text-muted-foreground mt-2 text-center">
            AI can make mistakes. Verify important information with the provided sources.
          </p>
        </div>
      </div>
    </div>
  );
}

