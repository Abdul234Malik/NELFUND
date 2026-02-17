import { Bot, CircleUser, ExternalLink } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary" />
        </div>
      )}
      
      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <Card className={`p-4 ${isUser ? "bg-primary text-primary-foreground" : "bg-card"}`}>
          <p className="whitespace-pre-wrap">{message.content}</p>
        </Card>

        {message.citations && message.citations.length > 0 && (
          <div className="flex flex-col gap-2 w-full">
            <p className="text-sm text-muted-foreground px-2">Sources:</p>
            <div className="flex flex-col gap-2">
              {message.citations.map((citation, index) => {
                // Handle both string (file name) and object (with url/title) formats
                const isString = typeof citation === 'string';
                const fileName = isString ? citation : citation.title || citation.url || 'Source';
                const citationUrl = isString ? null : citation.url;
                const citationSnippet = isString ? null : citation.snippet;
                
                return (
                  <Card key={citation.id || index} className="p-3 hover:bg-accent/50 transition-colors">
                    {citationUrl ? (
                      <a
                        href={citationUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-start gap-2 group"
                      >
                        <Badge variant="secondary" className="flex-shrink-0 mt-0.5">
                          {index + 1}
                        </Badge>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm group-hover:text-primary transition-colors truncate">
                              {fileName}
                            </p>
                            <ExternalLink className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                          </div>
                          {citationSnippet && (
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                              {citationSnippet}
                            </p>
                          )}
                        </div>
                      </a>
                    ) : (
                      <div className="flex items-start gap-2">
                        <Badge variant="secondary" className="flex-shrink-0 mt-0.5">
                          {index + 1}
                        </Badge>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-foreground">
                            {fileName}
                          </p>
                        </div>
                      </div>
                    )}
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        <p className="text-xs text-muted-foreground px-2">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <CircleUser className="w-5 h-5 text-primary-foreground" />
        </div>
      )}
    </div>
  );
}

