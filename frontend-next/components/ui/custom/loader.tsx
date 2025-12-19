import { Loader2 } from "lucide-react";

export default function Loader() {
  return (
    <div className="text-center flex flex-col items-center justify-center animate-in fade-in slide-in-from-right-2 duration-500">
      <Loader2 className="h-8 w-8 animate-spin text-orange-400" />
      <p className="mt-4 ml-2 text-zinc-600 dark:text-zinc-400">Loading...</p>
    </div>
  );
}
