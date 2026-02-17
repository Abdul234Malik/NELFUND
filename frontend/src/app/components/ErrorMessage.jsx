import { CircleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { Button } from "./ui/button";

export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex gap-4 justify-start">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-destructive/10 flex items-center justify-center">
        <CircleAlert className="w-5 h-5 text-destructive" />
      </div>
      <div className="flex flex-col gap-2 max-w-[80%]">
        <Alert variant="destructive">
          <CircleAlert className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {message}
          </AlertDescription>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="mt-2"
            >
              Retry
            </Button>
          )}
        </Alert>
      </div>
    </div>
  );
}

