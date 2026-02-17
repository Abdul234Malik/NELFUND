import { Loader } from "lucide-react";

export function LoadingIndicator() {
  return (
    <div className="flex gap-4 justify-start">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
        <Loader className="w-5 h-5 text-primary animate-spin" />
      </div>
      <div className="flex flex-col gap-2 max-w-[80%]">
        <div className="bg-card p-4 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}

