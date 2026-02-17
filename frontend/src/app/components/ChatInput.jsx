import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

export function ChatInput({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Ask me anything..." 
}) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="min-h-[60px] max-h-[200px] resize-none"
        rows={2}
      />
      <Button 
        type="submit" 
        size="icon" 
        disabled={disabled || !message.trim()}
        className="h-[60px] w-[60px] flex-shrink-0"
      >
        <Send className="w-5 h-5" />
        <span className="sr-only">Send message</span>
      </Button>
    </form>
  );
}

