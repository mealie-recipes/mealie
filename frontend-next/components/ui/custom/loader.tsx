import { Loader2 } from "lucide-react";

export default function Loader() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-900">
      <div className="text-center flex flex-col items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-orange-400" />
        <p className="mt-4 ml-2 text-zinc-600 dark:text-zinc-400">Loading...</p>
      </div>
    </div>
  );
}
